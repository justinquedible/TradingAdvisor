# Justin Thanh Quach
# 47143732


import datetime
import alpha_vantage_api_funcs as api
import indicators
import signal_strategies as signals
from collections import namedtuple


InputInfo = namedtuple("InputInfo", \
    ["apiKey", "url", "symbol", "startDate", "endDate", "strategy"])


def run_user_interface():
    """Runs the user interface."""
    try:
        userInput = _take_user_input()
        dataList = _trim_data_list(_make_data_list(
                userInput.url, userInput.symbol, userInput.apiKey),
            userInput.startDate, userInput.endDate)
        
        indicator, signal = _assign_classes(dataList, userInput.strategy)
        dataList = _add_indicator_data(
            indicator, userInput.url, userInput.symbol, userInput.apiKey)

        dataList = _add_signal_data(signal)

        _print_header(userInput.symbol, dataList, userInput.strategy)
        _print_table(dataList)
    
    except api.APIError as e:
        print("FAILED")
        print(e.statusCode)
        print(e.errorType)


def _take_user_input() -> InputInfo:
    """Takes in user input and returns InputInfo namedtuple."""
    apiPath = input()
    with open(apiPath, 'r') as f:
        apiKey = f.read()
    baseURL = input()
    symbol = input()
    startDate = _str_to_date(input())
    endDate = _str_to_date(input())
    strategy = input()
    return InputInfo(apiKey, baseURL, symbol, startDate, endDate, strategy)


def _str_to_date(date: str) -> datetime.date:
    """Takes in a string and returns a date object."""
    date = list(map(int, date.split(sep='-')))
    return datetime.date(date[0], date[1], date[2])


def _make_data_list(url: str, symbol: str, apiKey: str) -> list:
    """
    Generates the data as a list of lists. The first element of the list
    is a date object, and the second element is a dictionary that contains
    the stock prices and other information.
    """
    dataList = api.get_api_data(url, symbol, apiKey)
    for dataPoint in dataList:
        dataPoint[0] = _str_to_date(dataPoint[0])
    return dataList


def _trim_data_list(dataList: list, startDate: datetime.date,
    endDate: datetime.date) -> list:
    """
    Returns a new data list that contains data whose dates are within the
    given start and end dates.
    """
    trimData = []
    for dataPoint in dataList:
        if dataPoint[0] >= startDate and dataPoint[0] <= endDate:
            trimData.append(dataPoint)
    return trimData


def _assign_classes(dataList: list, strategy: str):
    """Assigns the right indicator class from the given strategy."""
    stratInfo = strategy.split()
    if stratInfo[0] == "TR":
        indicator = indicators.TrueRange(dataList)
        signal = signals.TrueRange(dataList, stratInfo[1], stratInfo[2])
    if strategy[0] == "M":
        days = int(stratInfo[1])
        indicator = indicators.SimpleMovingAvg(dataList, days, strategy[1])
        signal = signals.SimpleMovingAvg(dataList, strategy[1])
    if strategy[0] == "D":
        days = int(strategy.split()[1])
        indicator = indicators.DirectionIndicator(dataList, days, strategy[1])
        signal = signals.DirectionIndicator(dataList, stratInfo[2], stratInfo[3])
    return (indicator, signal)


def _add_indicator_data(
    indicator, url: str, symbol: str, apiKey: str) -> list:
    """Adds indicator data to main data list."""
    indicator.get_indicator_data(url, symbol, apiKey)
    return indicator.update_data()


def _add_signal_data(signal) -> list:
    """Adds signal strategy data to main data list."""
    return signal.update_data()


def _print_header(
    symbol: str, dataList: list, strategy: str) -> None:
    """Prints the header of the report."""
    print(symbol)
    print(len(dataList))
    print(strategy)


def _print_table(dataList: list) -> None:
    """Prints table with date, stock data, indicator, and signal."""
    print("Date\tOpen\tHigh\tLow\tClose\tVolume\tIndicator\tBuy?\tSell?")
    for dateInfo in dataList:
        date = dateInfo[0]
        info = dateInfo[1]
        print(f"{str(date)}\t{info['1. open']}\t{info['2. high']}\t{info['3. low']}\t", end='')
        print(f"{info['4. close']}\t{info['5. volume']}\t{info['6. indicator']}\t", end='')
        print(f"{info['7. buy']}\t{info['8. sell']}")


if __name__ == "__main__":
    run_user_interface()