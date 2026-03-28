import numpy as np

total_cities = 5

fuelmatrix = np.array(
    [  # in litres
        [0, 2981, 2409, 4165, 2334],
        [2981, 0, 3538, 5013, 4065],
        [2409, 3538, 0, 3100, 2494],
        [4165, 5013, 3100, 0, 4015],
        [2334, 4065, 2494, 4015, 0],
    ]
)

demandmatrix = np.array(
    [  # in thousands
        [0, 3800, 4200, 1900, 3500],
        [3800, 0, 650, 80, 450],
        [4200, 650, 0, 1400, 750],
        [1900, 80, 1400, 0, 1600],
        [3500, 450, 750, 1600, 0],
    ]
)

subsistutionCapacityMatrix = np.array(
    [  # in thousands
        [0, 4100, 835, 1, 2900],
        [4100, 0, 1, 1, 1],
        [835, 1, 0, 700, 950],
        [1, 1, 700, 0, 85],
        [2900, 1, 950, 85, 0],
    ]
)

subsitutionElasticityMatrix = np.array(
    [  # odds of someone taking a replacememnt route
        [0, 0.75, 0.4, 0.001, 0.45],
        [0.75, 0, 0.001, 0.001, 0.001],
        [0.4, 0.001, 0, 0.60, 0.65],
        [0.001, 0.001, 0.60, 0, 0.20],
        [0.45, 0.001, 0.65, 0.20, 0],
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
