class BackEndData:
    def __init__(self, diff, profit_loss, train_matrix, unable_matrix):

        self.cityDict = {
            "London": 0,
            "Glasgow": 1,
            "Amsterdam": 2,
            "Berlin": 3,
            "Paris": 4,
            "Madrid": 5,
            "Reykjavik": 6,
            "Rome": 7,
            "Prague": 8,
            "Athens": 9,
        }

        self.diff = diff
        self.profit_loss = profit_loss
        self.train_matrix = train_matrix
        self.unable_to_find_transport_matrix = unable_matrix

    def getCancelledFlights(self, dist1, dist2):
        i = self.cityDict[dist1]
        j = self.cityDict[dist2]

        if i < j:
            return self.diff[j, i]
        else:
            return self.diff[i, j]

    def getLostProfit(self):
        return self.profit_loss

    def getDivertedToTrain(self, dist1, dist2):
        i = self.cityDict[dist1]
        j = self.cityDict[dist2]

        if i < j:
            return self.train_matrix[j, i]
        else:
            return self.train_matrix[i, j]

    def getUnableToFindTransport(self, dist1, dist2):
        i = self.cityDict[dist1]
        j = self.cityDict[dist2]

        if i < j:
            return self.unable_to_find_transport_matrix[j, i]
        else:
            return self.unable_to_find_transport_matrix[i, j]
