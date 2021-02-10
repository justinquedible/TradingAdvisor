# Justin Thanh Quach
# 47143732


import json
import urllib.parse
import urllib.request


class APIError(Exception):
    def __init__(self, errorType: str, statusCode=200):
        self.errorType = errorType
        self.statusCode = statusCode


def get_api_data(
    url: str, symbol: str, apiKey: str, function="TIME_SERIES_DAILY",
    dataLabel="Time Series (Daily)", otherParams=[("outputsize", "full")]) -> list:
    """Returns data from JSON response using given url. Defualt is daily stock info."""
    fullURL = _build_api_url(url, symbol, apiKey, function, otherParams)
    response = _get_data(fullURL)
    data = _store_data(response, dataLabel)
    return data


# Private Functions Below


def _build_api_url(
    baseURL: str, symbol: str, apiKey: str,
    function: str, otherParams: list) -> str:
    """Returns a complete URL for the API."""
    parameters = [
        ("symbol", symbol),
        ("apikey", apiKey),
        ("function", function)
        ]
    for param in otherParams:
        parameters.append(param)
    return f"{baseURL}/query?{urllib.parse.urlencode(parameters)}"


def _get_data(url: str) -> dict:
    """
    Searches URL and returns a dictionary of the parsed JSON response.
    Raises an httpError if status code is not 200.
    Raises a formatError if content is misformatted or missing.
    """
    response = None
    try:
        response = urllib.request.urlopen(url)
        jsonText = response.read().decode(encoding='utf-8')
        dataDict = json.loads(jsonText)
        _check_format(dataDict)
        return dataDict

    except urllib.error.HTTPError as e:
        raise APIError("NOT 200", e.code)

    except (AssertionError, json.decoder.JSONDecodeError):
        raise APIError("FORMAT")

    except urllib.error.URLError as e:
        raise APIError("NETWORK", 0)

    finally:
        if response != None:
            response.close()


def _store_data(dataDict: dict, label: str) -> list:
    """
    Turns data dictionary into a list of lists, with first element as the date, and the
    second element as a dictionary of stock info.
    """
    stockData = list(map(list, dataDict[label].items()))
    stockData.reverse()
    return stockData


def _check_format(dataDict: dict):
    """Raises an AssertionError if content is misformatted or missing."""
    assert type(dataDict) == dict
    assert "Meta Data" in dataDict
    if "Time Series (Daily)" in dataDict:
        for date in dataDict["Time Series (Daily)"]:
            assert len(date) == 10
            infoDict = dataDict["Time Series (Daily)"][date]
            assert "1. open" in infoDict
            assert "2. high" in infoDict
            assert "3. low" in infoDict
            assert "4. close" in infoDict
            assert "5. volume" in infoDict
            for val in infoDict.values():
                assert len(val) > 0
    if "Technical Analysis: TRANGE" in dataDict:
        for date in dataDict["Technical Analysis: TRANGE"]:
            assert len(date) == 10
            assert "TRANGE" in dataDict["Technical Analysis: TRANGE"][date]
            assert len(dataDict["Technical Analysis: TRANGE"][date]["TRANGE"]) > 0
    if "Technical Analysis: SMA" in dataDict:
        for date in dataDict["Technical Analysis: SMA"]:
            assert len(date) == 10
            assert "SMA" in dataDict["Technical Analysis: SMA"][date]
            assert len(dataDict["Technical Analysis: SMA"][date]["SMA"]) > 0