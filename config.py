# Properties
COLUMN_NAME = "sciezka_zdjecie"
COLUMN_YAW = "azymut"

# Server
SERVER_DIRECTORY = "python/plugins/PhotoViewer360/viewer"

# Panorama Viewer
IP = "127.0.0.1"
PORT = 1520

GPKP_COLUMNS_DELETE_LIST = (
    'altitude',
    'rotation'
)

GPKP_COLUMNS_ADD_LIST = (
    'nr_drogi',
    'nazwa_ulicy',
    'numer_odcinka',
    'kilometraz'
)


GPKP_COLUMNS_CHANGE_DICT = {
    "photo": 'sciezka_zdjecie',
    "filename": 'nazwa_zdjecia',
    "directory": "nazwa_folderu",
    "direction": 'azymut',
    "longitude": 'długosc geog',
    "latitude": 'szerokosc geog',
    "timestamp": 'data_wykonania'
}

GPKG_FILTER_EXTENSION = "geoPackage(*.gpkg)"

FEED_URL = 'https://qgisfeed.envirosolutions.pl/'

INDUSTRIES = {
    "999": "Nie wybrano",
    "e": "Energetyka/OZE",
    "u": "Urząd",
    "td": "Transport/Drogi",
    "pg": "Planowanie/Geodezja",
    "wk": "WodKan",
    "s": "Środowisko",
    "rl": "Rolnictwo/Leśnictwo",
    "tk": "Telkom",
    "edu": "Edukacja",
    "i": "Inne",
    "it": "IT",
    "n": "Nieruchomości"
}
