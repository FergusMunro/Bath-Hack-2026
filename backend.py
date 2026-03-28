import numpy as np
import copy

from data import *

alpha = 1
beta = 1
gamma = 1

flightCapacity = 0.186


class FlightPath:  # circular flight path
    def __init__(self, start, end, fuelUse, revenue, easeOfReplacement, demand):
        self.start = start
        self.end = end
        self.fuelUse = fuelUse
        self.revenue = revenue
        self.easeOfReplacement = easeOfReplacement
        self.DEMAND = demand

    def getProfit(self):
        profit = 0
        cost = self.fuelUse * (self.start.fuelCost + self.end.fuelCost)
        profit += self.revenue - cost
        return profit

    def getTotalFuelUse(self):
        return 2 * self.fuelUse

    def calculateHeuristic(self, numFlights):

        unfilledDemmand = numFlights * flightCapacity - self.DEMAND  # need to normalize

        profit_norm = self.getProfit()  # need to normalize
        unfilled_demand_norm = 0
        heuristic = (
            alpha * profit_norm
            + beta * self.easeOfReplacement
            + gamma * unfilled_demand_norm
        )

        return heuristic / self.getTotalFuelUse()


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
        revenue = 1000  # scale to realistic number
        demand = demandmatrix[i, j]

        # Ease of replacement: 1 = easy to replace, 0 = hard to replace
        easeOfReplacement = subsitutionElasticityMatrix[i, j]
        path = FlightPath(
            start=start_terminal,
            end=end_terminal,
            fuelUse=fuel_use,
            revenue=revenue,
            easeOfReplacement=easeOfReplacement,
            demand=demand,
        )
        flight_paths[i, j] = path


routeMatrix = [
    [0, 0, 0, 0, 0],
    [20, 0, 0, 0, 0],
    [20, 30, 0, 0, 0],
    [25, 25, 30, 41, 0],
    [40, 23, 5, 18, 4],
]


backup = copy.deepcopy(routeMatrix)


def calculateFuelCost(cityIndex):
    fuel = 0
    for i in range(cityIndex):
        fuel += flight_paths[cityIndex, i].getTotalFuelUse()
    for j in range(cityIndex + 1, num_cities, 1):
        fuel += flight_paths[j, cityIndex].getTotalFuelUse()
    return fuel


def getMin(arr, excluded):
    excluded = set(excluded)
    return min(
        (i for i in range(len(arr)) if i not in excluded),
        key=lambda i: arr[i],
        default=-1,
    )


def getMaxProfit():
    minP = 999999
    maxP = -9999
    for i in range(num_cities):
        for j in range(i):
            minP = min(flight_paths[i, j], minP)
        for k in range(i + 1, num_cities, 1):
            minP = min(flight_paths[k, i])


def minimizeDisrupted(routeMatrix):

    fuelArray = np.zeros(num_cities)
    for i in range(num_cities):
        fuelArray[i] = calculateFuelCost(i) - terminals[i].fuelAvailability
    # now our goal is to find the way to find the optimal way to make these zero

    while (fuelArray > 0).any():

        for i in range(num_cities):

            # if this guy is already below fuel budget then don't need to do anything
            if fuelArray[i] < 0:
                continue

            heuristics = np.zeros(num_cities)
            for k in range(i):
                heuristics[k] += flight_paths[i, k].calculateHeuristic(
                    routeMatrix[i][k]
                )

            for k in range(i + 1, num_cities, 1):
                heuristics[k] = flight_paths[k, i].calculateHeuristic(routeMatrix[k][i])

            excluded = [i]
            while True:
                removeFlight = getMin(heuristics, excluded)

                if fuelArray[removeFlight] < 0:
                    excluded.append(removeFlight)
                else:
                    if removeFlight == -1:
                        excluded = [i]
                        removeFlight = getMin(heuristics, excluded)
                    break

            if removeFlight < i:
                routeMatrix[i][removeFlight] -= 1
                fuelArray[i] -= flight_paths[i, removeFlight].fuelUse
                fuelArray[removeFlight] -= flight_paths[i, removeFlight].fuelUse
            else:
                routeMatrix[removeFlight][i] -= 1
                fuelArray[i] -= flight_paths[removeFlight, i].fuelUse
                fuelArray[removeFlight] -= flight_paths[removeFlight, i].fuelUse
    diff = np.array(backup) - np.array(routeMatrix)

    for i in range(num_cities):
        for j in range(i):
            if diff[i][j] > 0:
                print(f"{cities[i]} ↔ {cities[j]}: removed {diff[i][j]} flights")


minimizeDisrupted(routeMatrix)
