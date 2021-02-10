# Justin Thanh Quach
# 47143732


class TrueRange:
    def __init__(self, dataList: list, buyThresh: str, sellThresh: str):
        self.dataList = dataList
        self.buyThresh = buyThresh
        self.sellThresh = sellThresh
    

    def update_data(self) -> list:
        """Adds buy and sell strategy to dataList attribute and returns it."""
        for index in range(len(self.dataList)):
            if self._compare_thresh(index, self.buyThresh):
                self.dataList[index][1]["7. buy"] = "BUY"
            else:
                self.dataList[index][1]["7. buy"] = ""
            
            if self._compare_thresh(index, self.sellThresh):
                self.dataList[index][1]["8. sell"] = "SELL"
            else:
                self.dataList[index][1]["8. sell"] = ""
        return self.dataList


    def _compare_thresh(self, index: int, thresh: str) -> bool:
        """Returns True if true range reaches threshold, and False otherwise."""
        threshReach = False
        if self.dataList[index][1]["6. indicator"] == "":
            return threshReach
        if thresh.startswith("<"):
            if float(self.dataList[index][1]["6. indicator"]) < float(thresh[1:]):
                threshReach = True
        else:
            if float(self.dataList[index][1]["6. indicator"]) > float(thresh[1:]):
                threshReach = True
        return threshReach


class SimpleMovingAvg:
    def __init__(self, dataList: list, avgType: str):
        self.dataList = dataList
        self.avgType = avgType
    

    def update_data(self) -> list:
        """Adds buy and sell strategy to dataList attribute and returns it."""
        self._initialize_signals()
        if self.avgType == "P":
            self._add_signals("4. close")
        if self.avgType == "V":
            self._add_signals("5. volume")
        return self.dataList


    def _initialize_signals(self):
        """Sets all buy and sell fields to empty string."""
        for dataPoint in self.dataList:
            dataPoint[1]["7. buy"] = ""
            dataPoint[1]["8. sell"] = ""
    

    def _add_signals(self, label: str):
        """Adds appropriate signal to dataList attribute."""
        for index in range(1, len(self.dataList)):
            if self.dataList[index-1][1]["6. indicator"] == "":
                continue
            if (float(self.dataList[index][1]["6. indicator"]) < \
                float(self.dataList[index][1][label])) and \
                (float(self.dataList[index-1][1]["6. indicator"]) > \
                float(self.dataList[index-1][1][label])):
                self.dataList[index][1]["7. buy"] = "BUY"
            if (float(self.dataList[index][1]["6. indicator"]) > \
                float(self.dataList[index][1][label])) and \
                (float(self.dataList[index-1][1]["6. indicator"]) < \
                float(self.dataList[index-1][1][label])):
                self.dataList[index][1]["8. sell"] = "SELL"


class DirectionIndicator:
    def __init__(self, dataList: list, buyThresh: str, sellThresh: str):
        self.dataList = dataList
        self.buyThresh = buyThresh
        self.sellThresh = sellThresh
    

    def update_data(self) -> list:
        """Adds buy and sell strategy to dataList attribute and returns it."""
        self._initialize_signals()
        self._add_signals()
        return self.dataList


    def _initialize_signals(self):
        """Sets all buy and sell fields to empty string."""
        for dataPoint in self.dataList:
            dataPoint[1]["7. buy"] = ""
            dataPoint[1]["8. sell"] = ""
    

    def _add_signals(self):
        """Adds appropriate signal to dataList attribute."""
        for index in range(1, len(self.dataList)):
            if (int(self.dataList[index][1]["6. indicator"]) > int(self.buyThresh)) and \
                (int(self.dataList[index-1][1]["6. indicator"]) <= int(self.buyThresh)):
                self.dataList[index][1]["7. buy"] = "BUY"
            if (int(self.dataList[index][1]["6. indicator"]) < int(self.sellThresh)) and \
                (int(self.dataList[index-1][1]["6. indicator"]) >= int(self.sellThresh)):
                self.dataList[index][1]["8. sell"] = "SELL"