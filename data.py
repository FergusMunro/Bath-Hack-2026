from inspect import indentsize
import numpy as np

max_cities = 5

fuelmatrix = np.loadtxt("Fuel_spent.csv", delimiter=",")[:max_cities, :max_cities]

routeMatrix = np.floor(
    np.loadtxt("Demand_thousands.csv", delimiter=",")[:max_cities, :max_cities] / 52
)
# we may stop using this and generate it instead

revenueMatrix = np.loadtxt("ticket_price.csv", delimiter=",")[:max_cities, :max_cities]


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

fuel_cost = np.ones(5)

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
    [  # odds of someone taking a replacememnt route
        [0, 0.75, 0.4, 0.001, 0.45],
        [0.75, 0, 0.001, 0.001, 0.001],
        [0.4, 0.001, 0, 0.60, 0.65],
        [0.001, 0.001, 0.60, 0, 0.20],
        [0.45, 0.001, 0.65, 0.20, 0],
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
