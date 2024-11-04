# Properties
column_name = "sciezka_zdjecie"
column_yaw = "azymut"
column_order = "fid"

#server
server_directory="python/plugins/PhotoViewer360/viewer"

# Panorama Viewer
IP = "127.0.0.1"
PORT = 1520



GPKP_COLUMNS_DELETE_LIST=('altitude',
                          'rotation')
GPKP_COLUMNS_ADD_LIST=('nr_drogi',
                       'nazwa_ulicy',
                       'numer_odcinka',
                       'kilometraz')
GPKP_COLUMNS_CHANGE_DICT={
                        "photo":'sciezka_zdjecie',
                        "filename":'nazwa_zdjecia',
                        "directory":"nazwa_folderu",
                        "direction": 'azymut',
                        "longitude": 'długosc geog',
                        "latitude": 'szerokosc geog',
                        "timestamp": 'data_wykonania'}

GPKG_FILTER_EXTENSTION="geoPackage(*.gpkg)"

