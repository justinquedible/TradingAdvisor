# Justin Thanh Quach
# 47143732


import alpha_vantage_api_funcs as api


class TrueRange:
    def __init__(self, dataList: list):
        self.indicatorData = []
        self.dataList = dataList
    

    def get_indicator_data(self, url: str, symbol: str, apiKey: str) -> None:
        """Assigns list of indicator values to indicatorData attribute."""
        self.indicatorData = api.get_api_data(
            url, symbol, apiKey, function="TRANGE", dataLabel="Technical Analysis: TRANGE",
            otherParams=[("interval", "daily")])


    def update_data(self) -> list:
        """Adds true range indicator data as percentage to dataList attribute and returns it."""
        self.dataList[0][1]["6. indicator"] = ""
        for dataPointIndex in range(1, len(self.dataList)):
            for indicatorPoint in self.indicatorData:
                if str(self.dataList[dataPointIndex][0]) == indicatorPoint[0]:
                    indicatorVal = float(indicatorPoint[1]["TRANGE"]) / \
                        float(self.dataList[dataPointIndex - 1][1]["4. close"]) * 100
                    self.dataList[dataPointIndex][1]["6. indicator"] = f"{indicatorVal:.4f}"
        return self.dataList


class SimpleMovingAvg:
    def __init__(self, dataList: list, days: int, avgType: str):
        self.indicatorData = []
        self.dataList = dataList
        self.days = days
        self.avgType = avgType
    

    def get_indicator_data(self, url: str, symbol: str, apiKey: str) -> None:
        """Assigns list of indicator values to indicatorData attribute."""
        if self.avgType == "P":
            self.indicatorData = api.get_api_data(
                url, symbol, apiKey, function="SMA", dataLabel="Technical Analysis: SMA",
                otherParams=[("interval", "daily"), ("time_period", str(self.days)),
                ("series_type", "close")])

        if self.avgType == "V":
            for dataPointIndex in range(self.days-1, len(self.dataList)):
                volSum = 0
                for index in range(dataPointIndex, dataPointIndex-self.days, -1):
                    volSum += int(self.dataList[index][1]["5. volume"])
                volAvg = volSum / self.days
                dataPoint = [str(self.dataList[dataPointIndex][0]), {"SMA": f"{volAvg:.4f}"}]
                self.indicatorData.append(dataPoint)

    
    def update_data(self) -> list:
        """Adds simple moving average indicator data to dataList attribute and returns it."""
        for i in range(self.days-1):
            self.dataList[i][1]["6. indicator"] = ""
        for dataPointIndex in range(self.days-1, len(self.dataList)):
            for indicatorPoint in self.indicatorData:
                if str(self.dataList[dataPointIndex][0]) == indicatorPoint[0]:
                    indicatorVal = indicatorPoint[1]["SMA"]
                    self.dataList[dataPointIndex][1]["6. indicator"] = indicatorVal
        return self.dataList


class DirectionIndicator:
    def __init__(self, dataList: list, days: int, dirType: str):
        self.indicatorData = []
        self.dataList = dataList
        self.days = days
        self.dirType = dirType
    

    def get_indicator_data(self, url: str, symbol: str, apiKey: str) -> None:
        """Assigns list of indicator values to indicatorData attribute."""
        if self.dirType == "P":
            self._calculate_indicator_data("4. close")
        if self.dirType == "V":
            self._calculate_indicator_data("5. volume")
            

    def update_data(self) -> list:
        """Adds directional indicator data to dataList attribute and returns it."""
        for dataPointIndex in range(len(self.dataList)):
            self.dataList[dataPointIndex][1]["6. indicator"] = \
                self.indicatorData[dataPointIndex][1]["DI"]
        return self.dataList
    

    def _calculate_indicator_data(self, label: str) -> None:
        indicatorVal = 0
        self.indicatorData.append([str(self.dataList[0][0]), {"DI": "0"}])
        for dataPointIndex in range(1, len(self.dataList)):
            if dataPointIndex <= self.days:
                if float(self.dataList[dataPointIndex][1][label]) < \
                    float(self.dataList[dataPointIndex-1][1][label]):
                    indicatorVal -= 1
                elif float(self.dataList[dataPointIndex][1][label]) > \
                    float(self.dataList[dataPointIndex-1][1][label]):
                    indicatorVal += 1
            else:
                if (float(self.dataList[dataPointIndex][1][label]) < \
                    float(self.dataList[dataPointIndex-1][1][label])) and \
                    (float(self.dataList[dataPointIndex-self.days][1][label]) > \
                    float(self.dataList[dataPointIndex-self.days-1][1][label])):
                    indicatorVal -= 2
                elif (float(self.dataList[dataPointIndex][1][label]) > \
                    float(self.dataList[dataPointIndex-1][1][label])) and \
                    (float(self.dataList[dataPointIndex-self.days][1][label]) < \
                    float(self.dataList[dataPointIndex-self.days-1][1][label])):
                    indicatorVal += 2
            if indicatorVal > 0:
                self.indicatorData.append(
                    [str(self.dataList[dataPointIndex][0]), {"DI": f"+{indicatorVal}"}])
            else:
                self.indicatorData.append(
                    [str(self.dataList[dataPointIndex][0]), {"DI": f"{indicatorVal}"}])