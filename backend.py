import numpy as np

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
    for j in range(cityIndex + 1, num_cities - 1, 1):
        fuel += flight_paths[j, cityIndex].getTotalFuelUse()


def calculateHeuristic(flight_path):

    profit_norm = flight_path.getProfit()
    heuristic = alpha * profit_norm + beta * flight_path.easeOfReplacement
    return heuristic


def minimizeDisrupted(routeMatrix):

    fuelArray = np.zeros(num_cities)
    print(fuelArray)
    for i in range(num_cities):
        fuelArray[i] = calculateFuelCost(i)


minimizeDisrupted(routeMatrix)
