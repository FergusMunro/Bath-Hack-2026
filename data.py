from inspect import indentsize
import numpy as np

max_cities = 10

flightCapacity = 0.186

fuelmatrix = np.loadtxt("Fuel_spent.csv", delimiter=",")[:max_cities, :max_cities]

routeMatrix = np.floor(
    (np.loadtxt("Demand_thousands.csv", delimiter=",")[:max_cities, :max_cities] / 52)
    + 1
)
# we may stop using this and generate it instead

revenueMatrix = (
    np.loadtxt("ticket_price.csv", delimiter=",")[:max_cities, :max_cities]
    * flightCapacity
    * 1000
)


def calculateFuelConsumptionAtTerminal():
    fuelConsumption = np.zeros(max_cities)
    for cityIndex in range(max_cities):

        for i in range(cityIndex):
            fuelConsumption[cityIndex] += (
                fuelmatrix[cityIndex, i] * routeMatrix[cityIndex, i]
            )

        for j in range(cityIndex + 1, max_cities, 1):
            fuelConsumption[cityIndex] += (
                fuelmatrix[j, cityIndex] * routeMatrix[j, cityIndex]
            )

    return fuelConsumption


fuel_availability = calculateFuelConsumptionAtTerminal()

fuel_cost = np.ones(max_cities)

"""
subsistutionCapacityMatrix = (
    np.array(
        [  # in thousands
            [0, 4100, 835, 1, 2900],
            [4100, 0, 1, 1, 1],
            [835, 1, 0, 700, 950],
            [1, 1, 700, 0, 85],
            [2900, 1, 950, 85, 0],
        ]
    )
    / 51
)
"""

subsitutionElasticityMatrix = np.array(
    [
        # Lon  Gla  Ams  Ber  Par  Rey  Mad  Ath  Rom  Pra
        [0.0, 0.7, 0.8, 0.7, 0.9, 0.3, 0.6, 0.4, 0.5, 0.7],  # London
        [0.7, 0.0, 0.6, 0.6, 0.7, 0.4, 0.5, 0.3, 0.4, 0.6],  # Glasgow
        [0.8, 0.6, 0.0, 0.9, 0.9, 0.3, 0.7, 0.5, 0.6, 0.8],  # Amsterdam
        [0.7, 0.6, 0.9, 0.0, 0.8, 0.2, 0.6, 0.6, 0.7, 0.9],  # Berlin
        [0.9, 0.7, 0.9, 0.8, 0.0, 0.2, 0.8, 0.5, 0.7, 0.8],  # Paris
        [0.3, 0.4, 0.3, 0.2, 0.2, 0.0, 0.2, 0.1, 0.2, 0.2],  # Reykjavik
        [0.6, 0.5, 0.7, 0.6, 0.8, 0.2, 0.0, 0.6, 0.8, 0.6],  # Madrid
        [0.4, 0.3, 0.5, 0.6, 0.5, 0.1, 0.6, 0.0, 0.9, 0.6],  # Athens
        [0.5, 0.4, 0.6, 0.7, 0.7, 0.2, 0.8, 0.9, 0.0, 0.7],  # Rome
        [0.7, 0.6, 0.8, 0.9, 0.8, 0.2, 0.6, 0.6, 0.7, 0.0],  # Prague
    ]
)


cities = [
    "London",
    "Glasgow",
    "Amsterdam",
    "Berlin",
    "Paris",
    "Madrid",
    "Reykjavik",
    "Rome",
    "Prague",
    "Athens",
]
