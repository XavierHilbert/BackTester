import variables

################################# KEYS, URLS, ETC. #################################
POLYGON_ENDPOINT: str = ""
POLYGON_KEY: str = ""
STRING_FORMAT_FOR_GETTING_HISTORICAL_OPENS_AND_CLOSES: str = "https://api.polygon.io/v1/open-close/{}/{}?apiKey={}"

################################# BACKTESTING CONSTANTS #################################
SIGINFICANCE: float = .01
MAX_CASH_TO_SPEND: float = 10000.0
MAX_NUMBER_OF_DAYS_IN_A_MONTH: int = 31
MIN_NUMBER_OF_DAYS_IN_A_MONTH: int = 1
MIN_NUMBER_OF_MONTHS: int = 1
MAX_NUMBER_OF_MONTHS: int = 12
NANO_CONVERSION: int = 10**9
MILI_NANO: int = 10**6
NUMBER_OF_NANO: int = variables.NUMBER_OF_SECONDS * NANO_CONVERSION
TIME_ZONE: str = "US/Eastern"
BEG_TIME_EST: str = "9:30:00"
END_TIME_EST: str = "16:00:00"
DAY_LIGHT_SAVINGS: int = 4
NOT_DAY_LIGHT_SAVINGS: int = 5
STRING_FORMAT_FOR_CHECKING_VALID_STOCK_AND_DATE: str = "https://api.polygon.io/v2/ticks/stocks/trades/{}/{}?&apiKey={}"
STRING_FORMAT_FOR_GETTING_HISTORICAL_DATA: str = "https://api.polygon.io/v2/ticks/stocks/trades/{}/{}?timestamp={}&timestampLimit={}&apiKey={}"

############################## READING CONSTANTS #############################################
ENCODING: str = "utf8"
READ_TYPE: str = "r"
