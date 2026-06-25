import geopandas as gpd
import os
import fiona
from IPython.display import display
import rasterio
from geojson import Feature, Point, FeatureCollection
from shapely.geometry import shape, mapping
import json
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox
from rasterio.features import geometry_mask
from osgeo import gdal
import datetime
import warnings
import pandas as pd
from scipy.stats import mode
from rasterio.windows import from_bounds, Window
import pyogrio
import traceback
from exactextract import exact_extract
import scipy
warnings.filterwarnings('ignore')

root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)


def zonal_stats_exact(name, gdf, method='sum', raster_path='', init_dir=''):
    if raster_path == '':
        messagebox.showinfo('OnSSET', 'Select the {} map'.format(name))
        raster_path = filedialog.askopenfilename(initialdir=init_dir,
                                                 filetypes=(("rasters", "*.tif"), ("all files", "*.*")))

    try:
        gdf.sort_values(by=['id'], inplace=True)

        with rasterio.open(raster_path) as r:

            results = exact_extract(r, gdf, '{}={}'.format(name, method), include_cols='id', output='pandas')
            results.sort_values(by=['id'], inplace=True)

            gdf[name] = results[name]

        print('Processing finished:', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return gdf, raster_path
    except rasterio.RasterioIOError as e:
        print('Could not process {}, layer was not selected or not in the correct format'.format(name))
        return [], []
    except Exception as e:
        print('Error occured: ')
        print(traceback.print_exc())
        return [], []


def admin_1(clusters, admin_1_path='', admin_col_name='', init_dir=''):
    try:
        if admin_1_path == '':
            messagebox.showinfo('OnSSET', 'Select the admin 1 boundaries')
            admin_1_path = filedialog.askopenfilename(initialdir=init_dir,
                filetypes=(("vector", ["*.shp", "*.gpkg", "*.geojson", "*.parquet"]), ("all files", "*.*")))

            if admin_1_path == '':
                print(print('Could not process Admin 1 layer, it was not selected'))
                return [], []

            try:
                admin_1 = gpd.read_file(admin_1_path)
            except:
                admin_1 = gpd.read_parquet(admin_1_path)

            messagebox.showinfo('OnSSET', 'Select the column which contains the Admin 1 level names')
            options = admin_1.columns.tolist()
            admin_col_name = dropdown_popup(options)
        else:
            try:
                admin_1 = gpd.read_file(admin_1_path)
            except:
                admin_1 = gpd.read_parquet(admin_1_path)

        clusters_2 = clusters.copy()

        clusters_support = clusters_2[['id', 'geometry']].to_crs({'init': "EPSG:4326"})

        # Apply spatial join
        try:
            cluster_support_2 = gpd.sjoin(clusters_support, admin_1[["geometry", admin_col_name]],
                                          op='intersects').drop(['index_right'], axis=1)
        except:
            cluster_support_2 = gpd.sjoin(clusters_support, admin_1[["geometry", admin_col_name]],
                                          predicate='intersects').drop(['index_right'], axis=1)

        clusters_2 = pd.merge(clusters_2, cluster_support_2[['id', admin_col_name]], on='id', how='left')
        clusters_2.rename(columns={admin_col_name: 'Admin_1'}, inplace=True)

        print('Processing finished:', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        clusters_2.drop_duplicates(subset="id", keep="first", inplace=True)
        return clusters_2, admin_1_path

    except fiona.errors.DriverError as e:
        print('Could not process Admin 1, layer was not selected or not in the correct format')
        return [], []
    except pyogrio.errors.DataSourceError:
        print('Could not process Admin 1, layer was not selected or not in the correct format')
        return [], []
    except ValueError as e:
        print('Could not process Admin 1. Check the coordinate system and that there is data in the study area')
        print(e)
        return [], []


def preparing_for_vectors(workspace, clusters, crs):
    clusters = clusters.to_crs({'init': crs})
    clusters.drop_duplicates(subset="id", keep="first", inplace=True)
    points = clusters.copy()
    if (points.geometry[0].type == 'Polygon') or (points.geometry[0].type == 'MultiPolygon'):
        points["geometry"] = points["geometry"].centroid
    points.to_file(os.path.join(workspace, 'clusters_cp.shp'), driver='ESRI Shapefile')
    print('Processing finished:', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    return clusters


def processing_lines(name, admin, crs, workspace, clusters, lines_path='', init_dir=''):
    if lines_path == '':
        messagebox.showinfo('OnSSET', 'Select the {} data'.format(name))
        lines_path = filedialog.askopenfilename(initialdir=init_dir,
            filetypes=(("vector", ["*.shp", "*.gpkg", "*.geojson", "*.parquet"]), ("all files", "*.*")))

        if lines_path == '':
            print('Could not process ' + '{}'.format(name) + ', layer was not selected or not in the correct format')
            return [], []

    try:
        try:
            lines = gpd.read_file(lines_path)
        except:
            lines = gpd.read_parquet(lines_path)

        lines_clip = gpd.clip(lines, admin)
        lines_proj = lines_clip.to_crs(crs)
        lines_proj = gpd.GeoDataFrame(lines_proj['geometry'].explode()).reset_index()

        # 1. FIX: Check if the dataset is empty before proceeding
        if lines_proj.empty:
            print(
                f"Warning: No features found within the admin boundary. Ensure both datasets are in EPSG:4326 and try again")
            return [], []

        lines_proj.to_file(os.path.join(workspace, name + "_proj.shp"), driver='ESRI Shapefile')

        with fiona.open(os.path.join(workspace, name + "_proj.shp")) as line:
            # 2. FIX: Removed 'firstline = line.next()' so you don't lose your first feature

            schema = {'geometry': 'Point', 'properties': {'id': 'int'}, }
            with fiona.open(os.path.join(workspace, name + "_proj_points.shp"), "w", "ESRI Shapefile",
                            schema) as output:
                for feat in line:  # Renamed loop variable to 'feat' to avoid overwriting 'lines'

                    # FIX: Skip rows that have no geographic shape data
                    if feat['geometry'] is None:
                        continue

                    first = shape(feat['geometry'])
                    length = first.length
                    for distance in range(0, int(length), 100):
                        point = first.interpolate(distance)
                        output.write({'geometry': mapping(point), 'properties': {'id': 1}})

        with fiona.open(os.path.join(workspace, name + "_proj_points.shp")) as lines_f, fiona.open(
                os.path.join(workspace, 'clusters_cp.shp')) as points:
            lines = gpd.read_file(os.path.join(workspace, name + "_proj.shp"))

            geoms1 = [shape(feat["geometry"]) for feat in lines_f]
            s1 = [np.array((geom.xy[0][0], geom.xy[1][0])) for geom in geoms1]
            s1_arr = np.array(s1)

            geoms2 = [shape(feat["geometry"]) for feat in points]
            s2 = [np.array((geom.xy[0][0], geom.xy[1][0])) for geom in geoms2]
            s2_arr = np.array(s2)

            def do_kdtree(combined_x_y_arrays, points):
                mytree = scipy.spatial.cKDTree(combined_x_y_arrays)
                dist, indexes = mytree.query(points)
                return dist, indexes

            def vector_overlap(vec, settlementfile, column_name):
                vec.drop_duplicates(vec.columns.difference(["geometry"]), keep="first", inplace=True)
                try:
                    a = gpd.sjoin(settlementfile, vec, op='intersects')
                except:
                    a = gpd.sjoin(settlementfile, vec, predicate='intersects')
                a[column_name + '2'] = 0
                return a

            results1, results2 = do_kdtree(s1_arr, s2_arr)

        z = results1.tolist()

        clusters_2 = clusters.copy()

        clusters_2[name + 'Dist'] = z
        clusters_2[name + 'Dist'] = clusters_2[name + 'Dist'] / 1000

        a = vector_overlap(lines, clusters_2, name + 'Dist')

        clusters_2 = pd.merge(left=clusters_2, right=a[['id', name + 'Dist2']], on='id', how='left')
        clusters_2.drop_duplicates(subset="id", keep="first", inplace=True)

        clusters_2.loc[clusters_2[name + 'Dist2'] == 0, name + 'Dist'] = 0

        del clusters_2[name + 'Dist2']
        print('Processing finished:', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Clean up temporary shapefile and associated files
        base_path = os.path.join(workspace, name + "_proj")
        for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
            try:
                os.remove(base_path + ext)
            except FileNotFoundError:
                pass  # File might not exist; skip it

        # Clean up temporary shapefile and associated files
        base_path = os.path.join(workspace, name + "_proj_points")
        for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
            try:
                os.remove(base_path + ext)
            except FileNotFoundError:
                pass  # File might not exist; skip it

        return clusters_2, lines_path
    except fiona.errors.DriverError as e:
        print('Could not process ' + '{}'.format(name) + ', layer was not selected or not in the correct format')
        return [], []
    except pyogrio.errors.DataSourceError:
        print('Could not process ' + '{}'.format(name) + ', layer was not selected or not in the correct format')
        return [], []


def processing_points(name, admin, crs, workspace, clusters, mg_filter, points_path='', init_dir=''):
    if points_path == '':
        messagebox.showinfo('OnSSET', 'Select the {} data'.format(name))
        points_path = filedialog.askopenfilename(initialdir=init_dir,
                                                 filetypes=(("vector", ["*.shp", "*.gpkg", "*.geojson", "*.parquet"]),
                                                            ("all files", "*.*")))

        if points_path == '':
            print('Could not process ' + '{}'.format(name) + ', layer was not selected or not in the correct format')
            return [], []

    try:
        try:
            points = gpd.read_file(points_path)
        except:
            points = gpd.read_parquet(points_path)
        if mg_filter:
            points['umgid'] = range(0, len(points))
            points_post = points

        points_clip = gpd.clip(points, admin)
        points_proj = points_clip.to_crs(crs)
        points_proj = gpd.GeoDataFrame(points_proj['geometry'].explode()).reset_index()

        # 1. FIX: Check if the dataset is empty before proceeding
        if points_proj.empty:
            print(
                f"Warning: No features found within the admin boundary. Ensure both datasets are in EPSG:4326 and try again")
            return [], []

        points_proj.to_file(os.path.join(workspace, name + "_proj.shp"), driver='ESRI Shapefile', mode="w")

        with fiona.open(os.path.join(workspace, name + "_proj.shp")) as points_f, fiona.open(
                os.path.join(workspace, 'clusters_cp.shp')) as points2:
            points = gpd.read_file(os.path.join(workspace, name + "_proj.shp"))

            geoms1 = [shape(feat["geometry"]) for feat in points_f]
            s1 = [np.array((geom.xy[0][0], geom.xy[1][0])) for geom in geoms1]
            s1_arr = np.array(s1)

            geoms2 = [shape(feat["geometry"]) for feat in points2]
            s2 = [np.array((geom.xy[0][0], geom.xy[1][0])) for geom in geoms2]
            s2_arr = np.array(s2)

        def do_kdtree(combined_x_y_arrays, points):
            mytree = scipy.spatial.cKDTree(combined_x_y_arrays)
            dist, indexes = mytree.query(points)
            return dist, indexes

        def vector_overlap(vec, settlementfile, column_name):
            vec.drop_duplicates(vec.columns.difference(["geometry"]), keep='first', inplace=True)
            try:
                a = gpd.sjoin(settlementfile, vec, op='intersects')
            except TypeError:
                a = gpd.sjoin(settlementfile, vec, predicate='intersects')
            a[column_name + '2'] = 0
            return a

        results1, results2 = do_kdtree(s1_arr, s2_arr)

        z = results1.tolist()

        clusters_2 = clusters.copy()

        clusters_2[name + 'Dist'] = z
        clusters_2[name + 'Dist'] = clusters_2[name + 'Dist'] / 1000.
        if mg_filter:
            z2 = results2.tolist()
            clusters_2['umgid'] = z2

        a = vector_overlap(points, clusters_2, name + 'Dist')

        clusters_2 = pd.merge(left=clusters_2, right=a[['id', name + 'Dist2']], on='id', how='left')
        clusters_2.drop_duplicates(subset="id", keep="first", inplace=True)

        clusters_2.loc[clusters_2[name + 'Dist2'] == 0, name + 'Dist'] = 0

        if mg_filter:
            cols = points_post.columns.tolist()
            try:
                cols.remove('id')
            except ValueError:
                pass
            try:
                cols.remove('geometry')
            except ValueError:
                pass

            try:
                clusters_2 = pd.merge(clusters_2, points_post[['umgid', 'name']], on='umgid', how='left')
            except:
                clusters_2 = pd.merge(clusters_2, points_post[['umgid']], on='umgid', how='left')

        del clusters_2[name + 'Dist2']
        if mg_filter:
            del clusters_2['umgid']
        print('Processing finished:', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        clusters_2.drop_duplicates(subset="id", keep="first", inplace=True)

        # Clean up temporary shapefile and associated files
        base_path = os.path.join(workspace, name + "_proj")
        for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
            try:
                os.remove(base_path + ext)
            except FileNotFoundError:
                pass  # File might not exist; skip it

        return clusters_2, points_path
    except fiona.errors.DriverError:
        print('Could not process ' + '{}'.format(name) + ', layer was not selected or not in the correct format')
        return [], []
    except pyogrio.errors.DataSourceError:
        print('Could not process ' + '{}'.format(name) + ', layer was not selected or not in the correct format')
        return [], []
    except ValueError as e:
        print('Could not process ' + '{}'.format(
            name) + '. Check the coordinate system and that there is data in the study area')
        print(e)
        return [], []


def processing_hydro(admin, crs, workspace, clusters, points, hydropowervalue,
                     hydropowerunit):

    points_clip = gpd.clip(points, admin)
    points_proj = points_clip.to_crs(crs)
    points_proj = points_proj.explode(index_parts=False, ignore_index=True)

    # 1. FIX: Check if the dataset is empty before proceeding
    if points_proj.empty:
        print(
            f"Warning: No features found within the admin boundary. Ensure both datasets are in EPSG:4326 and try again")
        return []

    points_proj.to_file(os.path.join(workspace, "HydropowerDist_proj.shp"), driver='ESRI Shapefile')

    with fiona.open(os.path.join(workspace, "HydropowerDist_proj.shp")) as points_f, fiona.open(
            os.path.join(workspace, 'clusters_cp.shp')) as points2:
        points = gpd.read_file(os.path.join(workspace, "HydropowerDist_proj.shp"))

        geoms1 = [shape(feat["geometry"]) for feat in points_f]
        s1 = [np.array((geom.xy[0][0], geom.xy[1][0])) for geom in geoms1]
        s1_arr = np.array(s1)

        geoms2 = [shape(feat["geometry"]) for feat in points2]
        s2 = [np.array((geom.xy[0][0], geom.xy[1][0])) for geom in geoms2]
        s2_arr = np.array(s2)

        mytree = scipy.spatial.cKDTree(s1_arr)
        dist, indexes = mytree.query(s2_arr)

    def vector_overlap(vec, settlementfile, column_name):
        vec.drop_duplicates(vec.columns.difference(["geometry"]), keep='first', inplace=True)
        try:
            a = gpd.sjoin(settlementfile, vec, op='intersects')
        except:
            a = gpd.sjoin(settlementfile, vec, predicate='intersects')
        a[column_name + '2'] = 0
        return a

    z1 = dist.tolist()
    z2 = indexes.tolist()

    clusters_2 = clusters.copy()

    clusters_2['HydropowerDist'] = z1
    clusters_2['HydropowerDist'] = clusters_2['HydropowerDist'] / 1000
    clusters_2['HydropowerFID'] = z2

    z3 = []
    for s in indexes:
        z3.append(points[hydropowervalue][s])

    clusters_2['Hydropower'] = z3

    x = hydropowerunit

    if x == 'MW':
        clusters_2['Hydropower'] = clusters_2['Hydropower'] * 1000
    elif x == 'kW':
        clusters_2['Hydropower'] = clusters_2['Hydropower']
    else:
        clusters_2['Hydropower'] = clusters_2['Hydropower'] / 1000

    a = vector_overlap(points, clusters_2, 'HydropowerDist')

    clusters_2 = pd.merge(left=clusters_2, right=a[['id', 'HydropowerDist2']], on='id', how='left')
    clusters_2.drop_duplicates(subset="id", keep="first", inplace=True)

    clusters_2.loc[clusters_2['HydropowerDist2'] == 0, 'HydropowerDist'] = 0

    del clusters_2['HydropowerDist2']
    print('Processing finished:', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Clean up temporary shapefile and associated files
    base_path = os.path.join(workspace, "HydropowerDist_proj")
    for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
        try:
            os.remove(base_path + ext)
        except FileNotFoundError:
            pass  # File might not exist; skip it

    return clusters_2


def hydro(admin, crs, workspace, clusters, init_dir=''):
    try:
        messagebox.showinfo('OnSSET', 'Select the Hydropower data')
        hydro_path = filedialog.askopenfilename(initialdir=init_dir,
                                                title="Select Hydro map",
                                                filetypes=(("vector", ["*.shp", "*.gpkg", "*.geojson", "*.parquet"]),
                                                           ("all files", "*.*")))
        if hydro_path == '':
            print('Could not process Hydro points, layer was not selected')
            return [], []

        try:
            hydro = gpd.read_file(hydro_path)
        except:
            hydro = gpd.read_parquet(hydro_path)

        messagebox.showinfo('OnSSET',
                            'Select the column which describes the hydropower POWER potential in each location')
        options = hydro.columns.tolist()
        hydropower = dropdown_popup(options)

        messagebox.showinfo('OnSSET', 'Select the UNIT of the power potential')
        options = ['W', 'kW', 'MW']
        hydrounit = dropdown_popup(options)

        print(hydropower)
        print(hydrounit)

        out = processing_hydro(admin, crs, workspace, clusters, hydro, hydropower, hydrounit)

        return out, hydro_path

    except fiona.errors.DriverError as e:
        print('Could not process Hydro points, layer was not selected')
        return [], []
    except pyogrio.errors.DataSourceError:
        print('Could not process Hydro points, layer was not selected')
        return [], []


def hydro_bulk(admin, hydro, hydropower, hydrounit, crs, workspace, clusters):
    try:
        out = processing_hydro(admin, crs, workspace, clusters, hydro, hydropower, hydrounit)

        return out

    except fiona.errors.DriverError as e:
        print('Could not process Hydro points, layer was not selected')
        return []
    except pyogrio.errors.DataSourceError:
        print('Could not process Hydro points, layer was not selected')
        return []
    except Exception as e:
        print('Error occured: ')
        print(traceback.print_exc())
        return []


def conditioning(clusters, workspace, popunit):
    clusters = clusters.to_crs({'init': 'epsg:4326'})

    clusters = clusters.rename(columns={"NightLight": "NightLights", popunit: "Pop", })

    if "Area" in clusters:
        clusters = clusters.rename(columns={"Area": "GridCellArea"})

    if "Night Lightsmean" in clusters:
        try:
            del clusters['NightLights']
            clusters = clusters.rename(columns={"NightLightmean": "NightLights"})
        except:
            pass

    if "Solar GHImean" in clusters:
        clusters = clusters.rename(columns={"Solar GHImean": "GHI"})

    if "TravelTime" in clusters:
        clusters["TravelTime"] = clusters["TravelTime"] / 60
        clusters = clusters.rename(columns={"TravelTime": "TravelHours"})
    elif "TravelHour" in clusters:
        clusters = clusters.rename(columns={"TravelHour": "TravelHours"})

    if "Wind speedmean" in clusters:
        clusters = clusters.rename(columns={"Wind speedmean": "WindVel"})

    if "Residentia" in clusters:
        clusters = clusters.rename(columns={"Residentia": "ResidentialDemandTierCustom"})
    elif "Custom Demandmean" in clusters:
        clusters = clusters.rename(columns={"Custom Demandmean": "ResidentialDemandTierCustom"})
    elif "CustomDemand" in clusters:
        clusters = clusters.rename(columns={"CustomDemand": "ResidentialDemandTierCustom"})
    else:
        clusters["ResidentialDemandTierCustom"] = 0

    if "Urban_Demand_Indexmean" in clusters:
        clusters = clusters.rename(columns={"Urban_Demand_Indexmean": "ResidentialDemandTierCustomUrban"})
    # else:
    #    clusters["ResidentialDemandTierCustomUrban"] = 0

    if "Rural_Demand_Indexmean" in clusters:
        clusters = clusters.rename(columns={"Rural_Demand_Indexmean": "ResidentialDemandTierCustomRural"})
    # else:
    #    clusters["ResidentialDemandTierCustomRural"] = 0

    if "Substation" in clusters:
        clusters = clusters.rename(columns={"Substation": "SubstationDist"})
    elif "SubstationDist" not in clusters:
        clusters["SubstationDist"] = 99999

    if "CurrentHVL" in clusters:
        clusters = clusters.rename(columns={"CurrentHVL": "Existing_HVDist"})

    if "CurrentMVL" in clusters:
        clusters = clusters.rename(columns={"CurrentMVL": "Existing_MVDist"})

    if "PlannedHVL" in clusters:
        clusters = clusters.rename(columns={"PlannedHVL": "Planned_HVDist"})

    if "PlannedMVL" in clusters:
        clusters = clusters.rename(columns={"PlannedMVL": "Planned_MVDist"})

    if "Existing_HVDist" in clusters:
        try:
            del clusters["CurrentHVLineDist"]
        except:
            pass
        clusters = clusters.rename(columns={"Existing_HVDist": "CurrentHVLineDist"})
    elif "Existing_HVDist" not in clusters and "CurrentHVLineDist" not in clusters:
        clusters["CurrentHVLineDist"] = 99999

    if "Planned_HVDist" in clusters:
        try:
            del clusters["PlannedHVLineDist"]
        except:
            pass
        clusters = clusters.rename(columns={"Planned_HVDist": "PlannedHVLineDist"})
        clusters["PlannedHVLineDist"] = np.minimum(clusters["CurrentHVLineDist"], clusters["PlannedHVLineDist"])
    elif "Planned_HVDist" not in clusters and "PlannedHVLineDist" not in clusters:
        clusters["PlannedHVLineDist"] = clusters["CurrentHVLineDist"]
    elif "Planned_HVDist" not in clusters and clusters["PlannedHVLineDist"].min() == 99999:
        clusters["PlannedHVLineDist"] = clusters["CurrentHVLineDist"]

    if "Existing_MVDist" in clusters:
        try:
            del clusters["CurrentMVLineDist"]
        except:
            pass
        clusters = clusters.rename(columns={"Existing_MVDist": "CurrentMVLineDist"})
    elif "Existing_MVDist" not in clusters and "CurrentMVLineDist" not in clusters:
        clusters["CurrentMVLineDist"] = 99999

    if "Planned_MVDist" in clusters:
        try:
            del clusters["PlannedMVLineDist"]
        except:
            pass
        clusters = clusters.rename(columns={"Planned_MVDist": "PlannedMVLineDist"})
        clusters["PlannedMVLineDist"] = np.minimum(clusters["CurrentMVLineDist"], clusters["PlannedMVLineDist"])
    elif "Planned_MVDist" not in clusters and "PlannedMVLineDist" not in clusters:
        clusters["PlannedMVLineDist"] = clusters["CurrentMVLineDist"]
    elif "Planned_MVDist" not in clusters and clusters["PlannedMVLineDist"].min() == 99999:
        clusters["PlannedMVLineDist"] = clusters["CurrentMVLineDist"]

    if "RoadsDist" in clusters:
        try:
            del clusters["RoadDist"]
        except:
            pass
        clusters = clusters.rename(columns={"RoadsDist": "RoadDist"})
    elif "RoadDist" not in clusters:
        clusters["RoadDist"] = 99999

    if "Transforme" in clusters:
        try:
            del clusters["TransformerDist"]
        except:
            pass
        clusters = clusters.rename(columns={"Transforme": "TransformerDist"})
    elif "Service TransformerDist" in clusters:
        try:
            del clusters["TransformerDist"]
        except:
            pass
        clusters = clusters.rename(columns={"Service TransformerDist": "TransformerDist"})
    elif "TransformerDist" not in clusters:
        clusters["TransformerDist"] = 99999

    if "Hydropower" not in clusters:
        clusters["Hydropower"] = 0

    if "Hydropow_1" in clusters:
        try:
            del clusters["HydropowerDist"]
        except:
            pass
        clusters = clusters.rename(columns={"Hydropow_1": "HydropowerDist"})
    elif 'HydropowerDist' not in clusters:
        clusters["HydropowerDist"] = 99999

    if "Hydropow_2" in clusters:
        try:
            del clusters["HydropowerFID"]
        except:
            pass
        clusters = clusters.rename(columns={"Hydropow_2": "HydropowerFID"})
    elif "HydropowerFID" not in clusters:
        clusters["HydropowerFID"] = 0

    if "IsUrban" not in clusters:
        clusters["IsUrban"] = 0

    if "HealthDema" not in clusters:
        clusters["HealthDemand"] = 0
    else:
        try:
            del clusters["HealthDemand"]
        except:
            pass
        clusters = clusters.rename(columns={"HealthDema": "HealthDemand"})
    if "HF_kWh" in clusters:
        clusters["HealthDemand"] = clusters["HF_kWh"]

    if "EducationD" not in clusters:
        clusters["EducationDemand"] = 0
    else:
        try:
            del clusters["EducationDemand"]
        except:
            pass
        clusters = clusters.rename(columns={"EducationD": "EducationDemand"})
    if "EF_kWh" in clusters:
        clusters["EducationDemand"] = clusters["EF_kWh"]

    if "AgriDemand" not in clusters:
        clusters["AgriDemand"] = 0

    if "Commercial" not in clusters:
        clusters["CommercialDemand"] = 0
    else:
        try:
            del clusters["CommercialDemand"]
        except:
            pass
        clusters = clusters.rename(columns={"Commercial": "CommercialDemand"})

    if ("MiniGridDist" not in clusters) and ("MGDist" not in clusters):
        clusters["MGDist"] = 99999
    elif "MiniGridDist" in clusters:
        clusters = clusters.rename(columns={"MiniGridDist": "MGDist"})

    clusters["X_deg"] = clusters.geometry.centroid.x

    clusters["Y_deg"] = clusters.geometry.centroid.y

    cols = clusters.columns.tolist()
    cols.remove('geometry')

    clusters_2 = clusters[cols]

    if 'ElecPop' not in clusters_2:
        clusters_2['ElecPop'] = 0


    clusters_2.to_csv(os.path.join(workspace, "OnSSET_InputFile.csv"), index=False)

    print('Processing finished:', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("The extraction file is now ready for review & use in the workspace directory as 'OnSSET_InputFile.csv'!")

    return clusters

def dropdown_popup(options):
    selected_value = None

    def on_select():
        nonlocal selected_value
        selected_value = variable.get()
        window.destroy()

    # Use Toplevel instead of creating a new Tk instance
    window = tk.Toplevel()
    window.title("Choose an option")

    variable = tk.StringVar(window)
    variable.set(options[0])  # default value

    dropdown = tk.OptionMenu(window, variable, *options)
    dropdown.pack(padx=100, pady=10)

    button = tk.Button(window, text="OK", command=on_select)
    button.pack(pady=20, padx=40)

    # Update the window to calculate size
    window.update_idletasks()

    # Get screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Get window width and height
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    # Calculate x and y coordinates
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    # Set geometry
    window.geometry(f"+{x}+{y}")

    # Wait until this window is closed
    window.grab_set()
    window.wait_window()

    return selected_value


def select_pop_clusters(init_dir):
    messagebox.showinfo('OnSSET', 'Select the clusters')
    file = filedialog.askopenfilename(initialdir=init_dir,
        filetypes=(("vector", ["*.shp", "*.gpkg", "*.geojson", ".parquet"]), ("all files", "*.*")))

    try:
        clusters = gpd.read_file(file)
    except:
        clusters = gpd.read_parquet(file)

    options = clusters.columns.tolist()
    messagebox.showinfo('OnSSET', 'Select the column with population counts in the clusters')
    x = dropdown_popup(options)
    print('Population column: ' + x)

    return x, clusters, file

