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

    def calculateHeuristic(self, numFlights, minProfit, maxProfit):

        unfilledDemmand = (
            self.DEMAND - numFlights * flightCapacity
        ) / self.DEMAND  # need to normalize

        profit_norm = (self.getProfit() - minProfit) / (maxProfit - minProfit)

        heuristic = (
            alpha * profit_norm
            + beta * self.easeOfReplacement
            + gamma * unfilledDemmand
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


def initializeTerminals():

    terminals = np.empty(num_cities, dtype=object)
    for i, city in enumerate(cities):
        terminals[i] = Terminal(
            name=city, fuelCost=1.0, fuelAvailability=5000
        )  # adjust fuelAvailability as needed
    return terminals


def initalizeFlightPaths(terminals):

    flight_paths = np.empty((num_cities, num_cities), dtype=object)

    for i in range(num_cities):
        for j in range(i):
            start_terminal = terminals[i]
            end_terminal = terminals[j]
            fuel_use = fuelmatrix[i, j]
            revenue = 1000  # NOTE: temporary
            demand = demandmatrix[i, j]

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
    return flight_paths


def calculateFuelCost(cityIndex, flight_paths):
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


def getMinMaxProfit(flight_paths):
    minP = 999999
    maxP = -9999
    for i in range(num_cities):
        for j in range(i):
            minP = min(flight_paths[i, j].getProfit(), minP)
            maxP = max(flight_paths[i, j].getProfit(), maxP)
        for k in range(i + 1, num_cities, 1):
            minP = min(flight_paths[k, i].getProfit(), minP)

            maxP = max(flight_paths[k, i].getProfit(), maxP)
    return minP, maxP


def calculateTotalProfit(routeMatrix, flight_paths):
    totalProfit = 0

    for i in range(num_cities):
        for j in range(i):
            numFlights = routeMatrix[i][j]

            if numFlights <= 0:
                continue

            path = flight_paths[i, j]

            # profit per flight * number of flights
            totalProfit += numFlights * path.getProfit()

    return totalProfit


def minimizeDisrupted(routeMatrix, terminals, flight_paths, minProfit, maxProfit):

    fuelArray = np.zeros(num_cities)
    for i in range(num_cities):
        fuelArray[i] = (
            calculateFuelCost(i, flight_paths) - terminals[i].fuelAvailability
        )
    # now our goal is to find the way to find the optimal way to make these zero

    while (fuelArray > 0).any():

        for i in range(num_cities):

            # if this guy is already below fuel budget then don't need to do anything
            if fuelArray[i] < 0:
                continue

            heuristics = np.zeros(num_cities)
            for k in range(i):
                heuristics[k] += flight_paths[i, k].calculateHeuristic(
                    routeMatrix[i][k], minProfit, maxProfit
                )

            for k in range(i + 1, num_cities, 1):
                heuristics[k] = flight_paths[k, i].calculateHeuristic(
                    routeMatrix[k][i], minProfit, maxProfit
                )

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
                fuelArray[removeFlight] -= flight_paths[
                    i, removeFlight
                ].getTotalFuelUse()
            else:
                routeMatrix[removeFlight][i] -= 1
                fuelArray[i] -= flight_paths[removeFlight, i].fuelUse
                fuelArray[removeFlight] -= flight_paths[
                    removeFlight, i
                ].getTotalFuelUse()
    return routeMatrix


def doAnalysis():
    terminals = initializeTerminals()
    flight_paths = initalizeFlightPaths(terminals)

    minProfit, maxProfit = getMinMaxProfit(flight_paths)

    routeMatrix = [
        [0, 0, 0, 0, 0],
        [20, 0, 0, 0, 0],
        [20, 30, 0, 0, 0],
        [25, 25, 30, 41, 0],
        [40, 23, 5, 18, 4],
    ]

    backup = copy.deepcopy(routeMatrix)

    oldProfit = calculateTotalProfit(routeMatrix, flight_paths)

    minimizeDisrupted(routeMatrix, terminals, flight_paths, minProfit, maxProfit)
    newProfit = calculateTotalProfit(routeMatrix, flight_paths)

    diff = np.array(backup) - np.array(routeMatrix)
    return (diff, oldProfit - newProfit)

    print(f"Change in revenue: {oldProfit- newProfit}")
    # flights removed
    # revenue earned


doAnalysis()
