################################# BACKTESTING VARIABLES #################################
# For trials to be independent of eachother, the sample has to be less than 10% of the population. 
# The population is the amount of stocks * the average amount of days the stock market is open in a year * the delta year: NUMBER_OF_STOCKS * (AVERAGE_AMOUNT_OF_DAYS_THE_MARKET_IS_OPEN_PER_A_YEAR * END_YEAR - START_YEAR)
# note: this assumes every stock in the list has exsisted since START_YEAR to END_YEAR
# But feel free to chagne the number below!
#10000
NUMBER_OF_TRIALS: int = 50
START_YEAR: int = 2010
END_YEAR: int = 2018
NUMBER_OF_SECONDS: int = 10 # 5 minutes candles
DELAY_AMOUNT_IN_MILISECONDS: float = 50

################################# SIGNAL VARIABLES #################################

#EMA#########################################
SHORT_EMA: int = 8 
LONG_EMA: int = 14
SHORT_EMA_MULTIPLIER: float = (2 / (SHORT_EMA + 1))
LONG_EMA_MULTIPLIER: float = (2 / (LONG_EMA + 1))

#CLOSES#######################################
MOST_AMOUNT_OF_PREVIOUS_CLOSES_NEEDED: int = max([SHORT_EMA, LONG_EMA])

################################# VARIABLES #################################
TAKE_PROFT_PERCT: float = .80 #MAYBE INCREASE TO .85
ROUNDING_AMOUNT: int = 2
################### SYMBOLS TO USE ######################
FILE: str = "symbols/tons_of_symbols"