from __future__ import annotations
import random as r
import calendar, time, datetime, pytz
import requests
import numpy
import constants, variables, data_base

class BasicStockInfo:
    """Contains basic stock information"""
    symbol = str
    date = str
    previous_closes = list
    should_short: bool = False
    should_long: bool = False
    tick_data: list = []
    candle_stick_data: list = []
    current_tick = int
    _delayed_price = float

    def update_data(self, symbol: str, date: str):
        """Updates attributes that need to be initalized for signals to work."""
        self.symbol = symbol
        self.date = date
        self.get_previous_closes()

    def get_previous_closes(self):
        """Get previouses day's closes."""
        list_of_previous_closes: list = []
        request_url: str
        test_dict: dict
        number_of_erros: int = 0
        previous_date: str = self.reduce_date_by_one_day(self.date)
        while len(list_of_previous_closes) != variables.MOST_AMOUNT_OF_PREVIOUS_CLOSES_NEEDED:
            request_url = constants.STRING_FORMAT_FOR_GETTING_HISTORICAL_OPENS_AND_CLOSES.format(self.symbol, previous_date, constants.POLYGON_KEY)
            test_dict = requests.get(request_url).json()
            if test_dict["status"] == "OK":
                list_of_previous_closes.append(test_dict["close"])
            elif number_of_erros == 10:
                list_of_previous_closes = []
                break
            else:
                number_of_erros += 1
            previous_date = self.reduce_date_by_one_day(previous_date)
        self.previous_closes = [x for x in reversed(list_of_previous_closes)]

    @staticmethod
    def reduce_date_by_one_day(date: str) -> str:
        """Returns the previous day in 2020-05-27 format."""
        theday = datetime.date(*map(int, date.split('-')))
        prevday = theday - datetime.timedelta(days=1)
        return prevday.strftime('%Y-%m-%d')
    
    @property
    def delayed_price(self) -> None:
        for i in range(self.current_tick, len(self.tick_data)):
            if int(self.tick_data[i]["t"]) - int(self.tick_data[self.current_tick]["t"]) >= variables.DELAY_AMOUNT_IN_MILISECONDS * constants.MILI_NANO:
                self.current_tick = i
                return float(self.tick_data[i]["p"])
            elif i == len(self.tick_data) - 1:
                return float(self.tick_data[-1]["p"])

class CandleStick:
    """Contains attributes of a candle stick; low, high, average, open, close."""

    def __init__(self, l = float, h = float, a = float, o = float, c = float) -> None:
        self.l = l
        self.h = h
        self.a = a
        self.o = o
        self.c = c

class CandleSticks(CandleStick):
    """Contains current, previous, previous preivous candle stick.
    Should be inherited if a signal is dependent on candle sticks."""

    current_stick = CandleStick()
    previous_stick = CandleStick()
    previous_previous_stick = CandleStick()
    
    def update_candle_sticks(self, new_low: float, new_high: float, new_avg: float, new_open: float, new_close: float):
        """Needs to be called to update candlesticks."""
        self.previous_previous_stick = self.previous_stick
        self.previous_stick = self.current_stick
        self.current_stick = CandleStick(new_low, new_high, new_avg, new_open, new_close)

class TickData:
    """Contains data associated with a particular stock."""
    price = float
    volume = float

class Stock(BasicStockInfo, CandleSticks, TickData):
    """Contains infomation about the stock"""

class EMA(Stock):
    """Contains info about ema."""
    previous_short_ema = float
    current_short_ema = float
    previous_long_ema = float
    current_long_ema = float

    def short_signal(self):
        """"Returns true if a short ema signal is present."""
        try:
            another_sign: bool = round(self.previous_short_ema, variables.ROUNDING_AMOUNT) > round(self.previous_stick.c, variables.ROUNDING_AMOUNT)
            downwards_momentum: bool = round(self.current_short_ema, variables.ROUNDING_AMOUNT) < round(self.price, variables.ROUNDING_AMOUNT) 
            return downwards_momentum and another_sign
        except TypeError:
            return False
    
    def long_signal(self):
        """"Returns true if a long ema signal is present."""
        try:
            another_sign: bool = round(self.previous_short_ema, variables.ROUNDING_AMOUNT) < round(self.previous_stick.c, variables.ROUNDING_AMOUNT)
            upwards_momentum: bool = round(self.current_short_ema, variables.ROUNDING_AMOUNT) > round(self.price, variables.ROUNDING_AMOUNT) 
            return upwards_momentum and another_sign
        except TypeError:
            return False
    
    def update(self):
        """Updates ema attributes."""
        short_ema: float = (self.price * variables.SHORT_EMA_MULTIPLIER) + (self.current_short_ema * (1 - variables.SHORT_EMA_MULTIPLIER))
        long_ema: float = (self.price * variables.LONG_EMA_MULTIPLIER) + (self.current_long_ema * (1 - variables.LONG_EMA_MULTIPLIER))
        self.previous_short_ema, self.previous_long_ema = self.current_short_ema, self.current_long_ema
        self.current_short_ema, self.current_long_ema = short_ema, long_ema

    def first_calc(self):
        """Calculates first and updates first ema."""
        i: int = 0
        total: float = 0
        while i < len(self.previous_closes):
            total += self.previous_closes[i]
            if i == variables.SHORT_EMA - 1:
                self.current_short_ema = total/variables.SHORT_EMA
            i += 1
        self.current_long_ema = total/len(self.previous_closes)
        for j in range(variables.SHORT_EMA, len(self.previous_closes)):
            short_ema: float = (self.previous_closes[j] * variables.SHORT_EMA_MULTIPLIER) + (self.current_short_ema * (1 - variables.SHORT_EMA_MULTIPLIER))
            self.current_short_ema = short_ema
    
class Signals(EMA):
    """Inherits all the signals."""

    def update_signal(self):
        """Updates every signal. 
        Should be called every time price updates."""
        EMA.update(self)

        self.should_short = EMA.short_signal(self)
        self.should_long = EMA.long_signal(self)
    
    def first_calc_signal(self):
        """Calculates first attributes needed for each signal to work. 
        Should be called once, before streaming begins."""
        EMA.first_calc(self)

class AccountManager(Signals):
    qty: int = 0
    position_price = float
    max_profit_since_purchase = float

    def update(self):
        """Needs to be called every time price and signals update."""
        if self.qty != 0:
            self.update_max_profit_since_purchase()
            if (self.qty < 0 and self.should_end_short()) or (self.qty > 0 and self.should_end_long()):
                self.end_position()
            elif self.should_take_profit():
                self.end_position()
        else:
            if self.should_short:
                self.short()
            elif self.should_long:
                self.long()

    def should_take_profit(self) -> bool:
        """Returns true if we should take profit."""
        return self.price < variables.TAKE_PROFT_PERCT * self.max_profit_since_purchase

    def should_end_short(self) -> bool:
        """Returns true is we should end short position."""
        return round(self.current_short_ema, variables.ROUNDING_AMOUNT) > round(self.price, variables.ROUNDING_AMOUNT)
    
    def should_end_long(self) -> bool:
        """Returns true is we should end long position."""
        return round(self.current_short_ema, variables.ROUNDING_AMOUNT) < round(self.price, variables.ROUNDING_AMOUNT)

    def update_max_profit_since_purchase(self):
        profit = numpy.sign(self.qty) * (self.price - self.position_price)
        if profit > self.max_profit_since_purchase:
            self.max_profit_since_purchase = profit

    def short(self):
        self.qty = -1 * int(constants.MAX_CASH_TO_SPEND/self.delayed_price)
        self.position_price = self.delayed_price
        self.max_profit_since_purchase = 0
    
    def long(self):
        self.qty = int(constants.MAX_CASH_TO_SPEND/self.delayed_price)
        self.position_price = self.delayed_price
        self.max_profit_since_purchase = 0
    
    def end_position(self):
        data_base.NET_AMOUNT[-1] += (self.qty * (self.delayed_price - self.position_price))
        self.qty = 0

class BackTester(AccountManager):
    """Backtests differnet strategies."""
    beg_time_epoch = int
    end_time_epoch = int

    def simulate(self) -> None:
        """Entrypoint to start simulating."""
        for _ in range(0, variables.NUMBER_OF_TRIALS):
            self.trial()

    def trial(self) -> None:
        symbol_date: list = self.get_valid_stock_and_date()
        self.update_data(symbol_date[0], symbol_date[1])
        if not self.previous_closes:
            return self.trial()
        self.update_epoch()
        self.get_all_tick_data()
        self.convert_tick_data_to_time_intervals()
        self.convert_time_interval_to_candle_stick()
        data_base.NET_AMOUNT.append(0.0)
        self.first_calc_signal()
        self.pseudo_stream_data()

    def pseudo_stream_data(self) -> None:
        """Emulates market data streaming."""
        print("Streaming")
        print(self.symbol)
        print(self.date)
        i: int = 0
        for iter in range(len(self.tick_data)):
            self.current_tick = iter
            self.price = float(self.tick_data[iter]["p"])
            self.volume = float(self.tick_data[iter]["s"])
            candle: dict = self.candle_stick_data[i]
            if self.tick_data[iter] == candle["last_tick"]:
                self.update_candle_sticks(float(candle["l"]), float(candle["h"]), float(candle["a"]), float(candle["o"]), float(candle["c"]))
                i += 1
                Signals.update_signal(self)
                AccountManager.update(self)
            iter = self.current_tick
        if self.qty != 0:
            AccountManager.end_position(self)

    def convert_time_interval_to_candle_stick(self):
        """Converts result of convert_tick_data_to_time_intervals and creates candlesticks to be streamed."""
        all_candle_sticks = []
        for interval in self.candle_stick_data:
            if len(interval) > 0: 
                lists_of_price: list = [x["p"] for x in interval]
                open_price = lists_of_price[0]
                close_price = lists_of_price[-1]
                max_price = max(lists_of_price)
                min_price = min(lists_of_price)
                avg_price = sum(lists_of_price)/len(lists_of_price)
                all_candle_sticks.append({"o": open_price, "c": close_price, "h": max_price, "l": min_price, "a": avg_price, "last_tick": interval[-1]}) # open, close, high, low, average price, last time, last tick added
        self.candle_stick_data = all_candle_sticks

    def convert_tick_data_to_time_intervals(self):
        """Tick data is converted to time interval data.
        The length of the interval is determined by number of seconds in variables."""
        interval_data = []
        subset_of_data = []        
        i: int = 0
        j: int = 0
        while j < len(self.candle_stick_data):
            if int(self.candle_stick_data[j]["t"]) - int(self.candle_stick_data[i]["t"]) <= constants.NUMBER_OF_NANO:
                subset_of_data.append(self.candle_stick_data[j])
                j += 1
            else:
                interval_data.append(subset_of_data)
                subset_of_data = []
                i = j
        interval_data.append(subset_of_data)
        self.candle_stick_data = interval_data

    def get_data(self) -> dict:
        """Returns inital data for a given stock and date."""
        request_url: str = constants.STRING_FORMAT_FOR_GETTING_HISTORICAL_DATA.format(self.symbol, self.date, self.beg_time_in_epoch, self.end_time_epoch, constants.POLYGON_KEY)
        return requests.get(request_url).json()

    def get_all_tick_data(self):
        """Get all data for a stock at a specifed date."""
        results: list = []
        previous_data: dict = self.get_data()["results"]
        self.beg_time_in_epoch = previous_data[-1]["t"]
        while True:
            new_data: list = self.get_data()["results"]
            if previous_data == new_data:
                break
            else:
                for i in range(0, len(previous_data)):
                    results.append(previous_data[i])
                self.beg_time_in_epoch = results[-1]["t"]
            previous_data = new_data
        self.candle_stick_data, self.tick_data = results, results

    def get_valid_stock_and_date(self) -> list:
        """Returns a valid stock and date."""
        random_symbol: str = r.choice(data_base.SYMBOLS)
        random_date: str = self.get_random_date()
        request_url: str = constants.STRING_FORMAT_FOR_CHECKING_VALID_STOCK_AND_DATE.format(random_symbol, random_date, constants.POLYGON_KEY)
        test_dict: dict = requests.get(request_url).json()
        if not (self.this_is_a_new_stock_and_date(random_symbol, random_date) and test_dict["success"] and test_dict["results"] != []):
            return self.get_valid_stock_and_date()
        else:
            return [random_symbol, random_date]

    def update_epoch(self):
        """Converts date and time into epoch time."""
        def is_daylight_savings(dt=None, timezone="UTC") -> bool:
            """Returns true if date is in daylight savings time."""
            if dt is None:
                dt = datetime.datetime.utcnow()
            timezone = pytz.timezone(timezone)
            timezone_aware_date = timezone.localize(dt, is_dst=None)
            return timezone_aware_date.tzinfo._dst.seconds != 0

        def find_gmt(time: str) -> str:
            """Converts a time in est to gmt."""
            date_split: list = self.date.split("-")
            time_split: list = time.split(":")
            year: int = int(date_split[0])
            month: int = int(date_split[1])
            day: int = int(date_split[2])
            if is_daylight_savings(datetime.datetime(year, month, day), timezone = constants.TIME_ZONE):
                time_split[0] = str(int(time_split[0]) + constants.DAY_LIGHT_SAVINGS)
            else:
                time_split[0] = str(int(time_split[0]) + constants.NOT_DAY_LIGHT_SAVINGS)
            return ":".join(time_split)
        begging_time_gmt: str = find_gmt(constants.BEG_TIME_EST)
        end_time_gmt: str = find_gmt(constants.END_TIME_EST)
        self.beg_time_in_epoch = calendar.timegm(time.strptime(f"{self.date} {begging_time_gmt}", '%Y-%m-%d %H:%M:%S')) * constants.NANO_CONVERSION
        self.end_time_in_epoch = calendar.timegm(time.strptime(f"{self.date} {end_time_gmt}", '%Y-%m-%d %H:%M:%S')) * constants.NANO_CONVERSION

    def get_random_date(self) -> str:
        """Returns a random date in 2018-02-02 format."""
        random_year: str = str(r.randint(variables.START_YEAR, variables.END_YEAR))
        random_month: int = self.format_date(r.randint(constants.MIN_NUMBER_OF_MONTHS, constants.MAX_NUMBER_OF_MONTHS))
        random_day: int = self.format_date(r.randint(constants.MIN_NUMBER_OF_DAYS_IN_A_MONTH, constants.MAX_NUMBER_OF_DAYS_IN_A_MONTH))
        return f"{random_year}-{random_month}-{random_day}"

    @staticmethod
    def this_is_a_new_stock_and_date(random_stock: str, random_date: str) -> bool:
        """Returns true the stock and date has not been used."""
        return not [random_stock, random_date] in data_base.USED_STOCKS_AND_DATES

    @staticmethod
    def format_date(int_to_convert: int) -> str:
        """Converts numeric date into a string in proper formatting."""
        if int_to_convert < 10:
            return f"0{int_to_convert}"
        else:
            return f"{int_to_convert}"