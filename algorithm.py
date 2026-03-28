import numpy as np

total_cities = 5

fuelmatrix = np.array(
    [
        [0, 2981, 2409, 4165, 2334],
        [2981, 0, 1, 1, 1],
        [1, 1, 0, 1, 1],
        [1, 1, 1, 0, 1],
        [1, 1, 1, 1, 0],
    ]
)

demandmatrix = np.array(
    [
        [0, 1, 1, 1, 1],
        [1, 0, 1, 1, 1],
        [1, 1, 0, 1, 1],
        [1, 1, 1, 0, 1],
        [1, 1, 1, 1, 0],
    ]
)

subsistutionCapacityMatrix = np.array(
    [
        [0, 1, 1, 1, 1],
        [1, 0, 1, 1, 1],
        [1, 1, 0, 1, 1],
        [1, 1, 1, 0, 1],
        [1, 1, 1, 1, 0],
    ]
)

subsitutionElasticityMatrix = np.array(
    [
        [0, 1, 1, 1, 1],
        [1, 0, 1, 1, 1],
        [1, 1, 0, 1, 1],
        [1, 1, 1, 0, 1],
        [1, 1, 1, 1, 0],
    ]
)

flightMatrix = np.array(
    [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]
)

planeCapacity = 0.186


def calculateDemandSubstitution(
    unfilledDemand, substitutionCapacity, substitutionElasticity
):
    # chat gpt made this beause i don't know economics
    if unfilledDemand <= 0 or substitutionCapacity <= 0:
        return 0, unfilledDemand

    fraction = (substitutionCapacity / unfilledDemand) ** substitutionElasticity

    fraction = min(fraction, 1.0)

    switchedPassengers = fraction * unfilledDemand
    disruptedPassengers = unfilledDemand - switchedPassengers

    return switchedPassengers, disruptedPassengers


def minimizeDisrupted(totalFuel):

    remainingFuel = totalFuel

    while remainingFuel > 0:

        heuristicMatrix = np.zeros((total_cities, total_cities))

        for source in range(total_cities):

            for destination in range(total_cities):
                if source == destination:
                    continue

                currentlyServiced = flightMatrix[source][destination] * planeCapacity

                _, disrupted = calculateDemandSubstitution(
                    demandmatrix[source][destination] - currentlyServiced,
                    subsistutionCapacityMatrix[source][destination],
                    subsitutionElasticityMatrix[source][destination],
                )

                _, new_disrupted = calculateDemandSubstitution(
                    demandmatrix[source][destination]
                    - currentlyServiced
                    - planeCapacity,
                    subsistutionCapacityMatrix[source][destination],
                    subsitutionElasticityMatrix[source][destination],
                )

                heuristicMatrix[source, destination] = (
                    disrupted - new_disrupted
                ) / fuelmatrix[source][destination]

        best_flight = np.unravel_index(
            np.argmax(heuristicMatrix), (total_cities, total_cities)
        )
        print(heuristicMatrix)
        print(best_flight)

        flightMatrix[best_flight] = flightMatrix[best_flight] + 1
        remainingFuel = remainingFuel - fuelmatrix[best_flight]


minimizeDisrupted(100)
