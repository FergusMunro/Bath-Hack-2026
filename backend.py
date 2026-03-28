import numpy as np
import copy

from backendDataClass import BackEndData
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
        terminals[i] = Terminal(name=city, fuelCost=1.0, fuelAvailability=500000)
    return terminals


def initalizeFlightPaths(terminals):

    flight_paths = np.empty((num_cities, num_cities), dtype=object)

    for i in range(num_cities):
        for j in range(i):
            start_terminal = terminals[i]
            end_terminal = terminals[j]
            fuel_use = fuelmatrix[i, j]
            revenue = revenueMatrix[i, j]
            demand = routeMatrix[i][j] * flightCapacity

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


def calculateFuelCost(cityIndex, flight_paths, routeMatrix):
    fuel = 0
    for i in range(cityIndex):
        fuel += flight_paths[cityIndex, i].fuelUse * routeMatrix[cityIndex, i]

    for j in range(cityIndex + 1, num_cities, 1):
        fuel += flight_paths[j, cityIndex].fuelUse * routeMatrix[j, cityIndex]
    return fuel


def getMin(arr, excluded):
    min_val = None
    min_idx = -1

    excluded = set(excluded)
    for i, val in enumerate(arr):
        if i in excluded:
            continue
        if min_val is None or val < min_val:
            min_val = val
            min_idx = i

    return min_idx


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
            calculateFuelCost(i, flight_paths, routeMatrix)
            - terminals[i].fuelAvailability
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

            flights_available = np.zeros(num_cities, dtype=int)
            for k in range(num_cities):
                if k < i:
                    flights_available[k] = routeMatrix[i][k]
                elif k > i:
                    flights_available[k] = routeMatrix[k][i]
                else:
                    flights_available[k] = 0  # no self-flight

            while True:

                removeFlight = getMin(heuristics, excluded)
                if removeFlight == -1:
                    excluded = [i] + [
                        idx
                        for idx in range(num_cities)
                        if flights_available[idx] <= 0 or idx == i
                    ]

                    removeFlight = getMin(heuristics, excluded)
                    break

                if fuelArray[removeFlight] < 0 or flights_available[removeFlight] <= 0:
                    excluded.append(removeFlight)
                else:
                    break

            if removeFlight == -1:
                continue

            if removeFlight < i:
                routeMatrix[i][removeFlight] -= 1
                fuelArray[i] -= flight_paths[i, removeFlight].fuelUse
                fuelArray[removeFlight] -= flight_paths[i, removeFlight].fuelUse
            else:
                routeMatrix[removeFlight][i] -= 1
                fuelArray[i] -= flight_paths[removeFlight, i].fuelUse
                fuelArray[removeFlight] -= flight_paths[removeFlight, i].fuelUse
    return routeMatrix


def calculateFuelConsumptionAtTerminal(flight_paths, routeMatrix):
    fuelConsumption = np.zeros(num_cities)
    for i in range(num_cities):

        fuelConsumption[i] = calculateFuelCost(i, flight_paths, routeMatrix)
    return fuelConsumption


def doAnalysis():
    terminals = initializeTerminals()
    flight_paths = initalizeFlightPaths(terminals)

    maxConsumption = calculateFuelConsumptionAtTerminal(flight_paths, routeMatrix)

    minProfit, maxProfit = getMinMaxProfit(flight_paths)

    backup = copy.deepcopy(routeMatrix)

    oldProfit = calculateTotalProfit(routeMatrix, flight_paths)

    planeShedule = copy.deepcopy(routeMatrix)
    print(planeShedule)

    minimizeDisrupted(planeShedule, terminals, flight_paths, minProfit, maxProfit)
    newProfit = calculateTotalProfit(planeShedule, flight_paths)

    diff = np.array(backup) - np.array(planeShedule)
    trainMatrix = np.zeros((num_cities, num_cities))
    unableToFindTransportMatrix = np.zeros((num_cities, num_cities))

    for i in range(num_cities):
        for j in range(i):

            cant_take_plane = (
                flight_paths[i][j].DEMAND - planeShedule[i][j] * flightCapacity
            )

            trainMatrix[i, j] = cant_take_plane * subsitutionElasticityMatrix[i, j]
            unableToFindTransportMatrix[i, j] = cant_take_plane - trainMatrix[i, j]

    print(backup)
    print("----")
    print(planeShedule)
    return BackEndData(
        diff, oldProfit - newProfit, trainMatrix, unableToFindTransportMatrix
    )


doAnalysis()
