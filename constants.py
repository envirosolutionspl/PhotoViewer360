from datetime import datetime

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
STATUS_SUCCESS = 'brak_bledow'
STATUS_CANCELED = 'anulowano'

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

# minimalny rozmiar pliku do pobrania danych (~9KB)
MIN_FILE_SIZE = 9000

CURRENT_YEAR = datetime.now().year
MIN_YEAR_BUILDINGS_3D = 1970
OKRES_DOSTEPNYCH_DANYCH_LOD = range(MIN_YEAR_BUILDINGS_3D, CURRENT_YEAR + 1)

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


# Properties
COLUMN_NAME = "sciezka_zdjecie"
COLUMN_YAW = "azymut"

# Server
SERVER_DIRECTORY = "/viewer"

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
