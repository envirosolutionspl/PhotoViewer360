from datetime import datetime

ENV_MENU_NAME = "EnviroSolutions"

DEFAULT_ENCODING = 'utf-8'

# url do sprawdzania połączenia z internetem
ULDK_URL = 'https://uldk.gugik.gov.pl/'

# kod układu współrzędnych
CRS= "2180"

# wersja Qt6
QT_VER = {
    6: "6."
}

# =============================
# Parametry do klasy NetworkUtils
TIMEOUT_MS = 5000
MAX_ATTEMPTS = 3
CANCEL_CHECK_MS = 500
HTTP_ERROR_THRESHOLD = 400

# Nazwy atrybutów
NETWORK_ATTRS = {
    'HTTP_STATUS': 'HttpStatusCodeAttribute',
    'HTTP_REASON': 'HttpReasonPhraseAttribute',
    'REDIRECT': 'RedirectPolicyAttribute',
    'TIMEOUT': 'TimeoutAttribute'
}

# RedirectPolicy
REDIRECT_POLICY_NAME = 'RedirectPolicy'
REDIRECT_POLICY_NO_LESS_SAFE = 'NoLessSafeRedirectPolicy'
DEFAULT_REDIRECT_POLICY = 1

# Wartości błędów i statusów
ERR_TIMEOUT = 'TimeoutError'
ERR_NONE = 'NoError'
ERR_CANCELED = 'OperationCanceledError'

# Komunikaty sieciowe
MSG_DOWNLOAD_CANCELED = "Pobieranie zostało anulowane."
MSG_NETWORK_ERROR = "Błąd sieciowy ({}) dla: {}"
MSG_HTTP_ERROR = "Błąd HTTP {}: {}"
MSG_EMPTY_CONTENT = "Serwer zwrócił pustą zawartość dla: {}"
MSG_TIMEOUT = "Przekroczono czas oczekiwania dla: {}"
MSG_FILE_WRITE_ERROR = "Błąd zapisu do pliku: {}"
MSG_JSON_DECODE_ERROR = "Błąd JSON: {}"
MSG_NO_CONNECTION = "Brak połączenia z internetem."
# =============================

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

FEED_SETTINGS_KEYS = {
    "SELECTED_INDUSTRY": "selected_industry",
    "SHOW_DIALOG": "showDialog",
}


# Properties
COLUMN_NAME = "sciezka_zdjecie"
COLUMN_YAW = "azymut"

# Server
SERVER_DIRECTORY = "/viewer"
VIEWER_FILES = {
    "VIEWER": "/viewer.html",
    "NONE": "/none.html",
    "BLANK": "/blank.html",
    "METADATA": "/file_metadata.html",
}
VIEWER_IMAGE_NAME = "image.jpg"

# Panorama Viewer
IP = "127.0.0.1"
PORT = 1520

TEMPORATORY_FILES_LIST = (
    'overwrite.gpkg',
    'duplicates.gpkg',
    'no_duplicates.gpkg'
)

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
    "longitude": 'dlugosc_geog',
    "latitude": 'szerokosc_geog',
    "timestamp": 'data_wykonania'
}

GPKG_FILTER_EXTENSION = "geoPackage(*.gpkg)"

DEFAULT_YAW_DEGREES = 310
HOTSPOT_BUFFER_RADIUS_M = 15
DUPLICATES_PREVIEW_LIMIT = 20

PROGRESS = {
    "IMPORT_START": 5,
    "IMPORT_AFTER_TOOL": 40,
    "IMPORT_ATTRIBUTES_DONE": 95,
    "DUPLICATES_BEFORE_MERGE": 96,
    "DUPLICATES_AFTER_MERGE": 98,
    "COMPLETE": 100,
}

# Images
IMAGE_PLUGIN_ICON = "/images/ikona_wtyczki.svg"
IMAGE_TARGET_ICON = "/images/target.png"
IMAGE_SMALL_CURSOR = "/images/small_celownik.png"

# CRS codes
CRS_EPSG_2180 = "EPSG:2180"
CRS_EPSG_4326 = "EPSG:4326"
CRS_2180_PROJ_OPERATION = (
    "+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad "
    "+step +proj=tmerc +lat_0=0 +lon_0=19 +k=0.9993 "
    "+x_0=500000 +y_0=-5300000 +ellps=GRS80"
)

EARTH_RADIUS_KM = 6373.0

QGIS_SETTINGS_KEYS = {
    "PARALLEL_RENDERING": "/qgis/parallel_rendering",
    "OPENCL_ENABLED": "/core/OpenClEnabled",
}

QGIS_FEED_MIN_VERSION_INT = 31000
