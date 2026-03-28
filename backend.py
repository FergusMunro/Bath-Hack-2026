import numpy as np # type: ignore

from data import *

alpha = 1
beta = 1


class FlightPath:  # circular flight path
    def __init__(self, start, end, fuelUse, revenue, easeOfReplacement):
        self.start = start
        self.end = end
        self.fuelUse = fuelUse
        self.revenue = revenue
        self.easeOfReplacement = easeOfReplacement

    def getProfit(self):
        profit = 0
        cost = path.fuelUse * (self.start.fuelCost + self.end.fuelCost)
        profit += path.revenue - cost
        return profit

    def getTotalFuelUse(self):
        return 2 * self.fuelUse


class Terminal:
    def __init__(self, name, fuelCost, fuelAvailability):
        self.name = name
        self.fuelCost = fuelCost
        self.fuelAvailability = fuelAvailability


# heuristic: alpha *  profit / normalProfit + beta * passangersServed / maxPassangers

cities = ["London", "Glasgow", "Amsterdam", "Berlin", "Paris"]

num_cities = len(cities)

terminals = np.empty(num_cities, dtype=object)
for i, city in enumerate(cities):
    terminals[i] = Terminal(
        name=city, fuelCost=1.0, fuelAvailability=5000
    )  # adjust fuelAvailability as needed


flight_paths = np.empty((num_cities, num_cities), dtype=object)

for i in range(num_cities):
    for j in range(i):
        start_terminal = terminals[i]
        end_terminal = terminals[j]
        fuel_use = fuelmatrix[i, j]
        # Revenue proportional to demand
        revenue = demandmatrix[i, j] * 1000  # scale to realistic number
        # Ease of replacement: 1 = easy to replace, 0 = hard to replace
        easeOfReplacement = subsitutionElasticityMatrix[i, j]
        path = FlightPath(
            start=start_terminal,
            end=end_terminal,
            fuelUse=fuel_use,
            revenue=revenue,
            easeOfReplacement=easeOfReplacement,
        )
        flight_paths[i, j] = path


routeMatrix = [
    [0, 0, 0, 0, 0],
    [20, 0, 0, 0, 0],
    [20, 30, 0, 0, 0],
    [25, 25, 30, 41, 0],
    [40, 23, 5, 18, 4],
]


def calculateFuelCost(cityIndex):
    fuel = 0
    for i in range(cityIndex):
        fuel += flight_paths[cityIndex, i].getTotalFuelUse()
    for j in range(cityIndex + 1, num_cities, 1):
        fuel += flight_paths[j, cityIndex].getTotalFuelUse()
    return fuel


def calculateHeuristic(flight_path):

    profit_norm = flight_path.getProfit()
    heuristic = alpha * profit_norm + beta * flight_path.easeOfReplacement
    return heuristic


def getMin(arr, excluded):

    min = 0
    index = 0
    for i in range(len(arr)):
        if i in excluded:
            pass
        else:
            if arr[i] < min:
                min = arr[i]
                index = i
    return index


def minimizeDisrupted(routeMatrix):

    fuelArray = np.zeros(num_cities)
    for i in range(num_cities):
        fuelArray[i] = calculateFuelCost(i) - terminals[i].fuelAvailability
    # now our goal is to find the way to find the optimal way to make these zero

    while (fuelArray > 0).any():

        for i in range(num_cities):

            # if this guy is already below budget then chill out
            if fuelArray[i] < 0:
                continue

            heuristics = np.zeros(num_cities)
            for k in range(i):
                heuristics[k] += flight_paths[i, k].getTotalFuelUse()

            for k in range(i + 1, num_cities, 1):
                heuristics[k] = flight_paths[k, i].getTotalFuelUse()

            excluded = [i]
            while True:
                rem = getMin(heuristics, excluded)

                if fuelArray[rem] < 0:
                    excluded.append(rem)
                else:
                    pass

            removeFlight = np.argmin(heuristics)
            if removeFlight < i:
                routeMatrix[i][removeFlight] -= 1
                fuelArray[i] -= flight_paths[i, removeFlight].fuelUse
                fuelArray[removeFlight] -= flight_paths[i, removeFlight].fuelUse
            else:
                routeMatrix[removeFlight][i] -= 1
                fuelArray[i] -= flight_paths[removeFlight, i].fuelUse
                fuelArray[removeFlight] -= flight_paths[removeFlight, i].fuelUse
    print(fuelArray)


minimizeDisrupted(routeMatrix)
