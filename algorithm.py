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

demandmatrix = (
    np.array(
        [  # in thousands
            [0, 3800, 4200, 1900, 3500],
            [3800, 0, 650, 80, 450],
            [4200, 650, 0, 1400, 750],
            [1900, 80, 1400, 0, 1600],
            [3500, 450, 750, 1600, 0],
        ]
    )
    / 51
)

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


planeCapacity = 0.186

fuel_for_all_flights = 908300000 / 51

num_planes_to_add = 1


def calculateDemandSubstitution(
    unfilledDemand, substitutionCapacity, substitutionElasticity
):
    # Step 1: Compute potential demand willing to switch
    potentialSwitch = unfilledDemand * substitutionElasticity

    # Step 2: Apply capacity constraint
    switchedPassengers = min(potentialSwitch, substitutionCapacity)

    # Step 3: Remaining unmet demand
    disruptedPassengers = unfilledDemand - switchedPassengers

    return switchedPassengers, disruptedPassengers


def minimizeDisrupted(totalFuel):

    remainingFuel = totalFuel

    while remainingFuel > 0:

        heuristicMatrix = np.zeros((total_cities, total_cities))

        for source in range(total_cities):

            for destination in range(total_cities):
                if source == destination:
                    heuristicMatrix[source, destination] = 0

                    continue

                currentlyServiced = flightMatrix[source, destination] * planeCapacity

                # if all passangers serviced then stop
                currentlyUnserviced = (
                    demandmatrix[source][destination] - currentlyServiced
                )

                if currentlyUnserviced <= 0:
                    heuristicMatrix[source, destination] = 0
                    continue

                _, disrupted = calculateDemandSubstitution(
                    currentlyUnserviced,
                    subsistutionCapacityMatrix[source][destination],
                    subsitutionElasticityMatrix[source][destination],
                )

                _, new_disrupted = calculateDemandSubstitution(
                    max(
                        0,
                        currentlyUnserviced - planeCapacity * num_planes_to_add,
                    ),
                    subsistutionCapacityMatrix[source][destination],
                    subsitutionElasticityMatrix[source][destination],
                )

                heuristicMatrix[source, destination] = (
                    (disrupted - new_disrupted) * disrupted
                ) / fuelmatrix[source][destination]

        best_flight = np.unravel_index(
            np.argmax(heuristicMatrix), (total_cities, total_cities)
        )

        flightMatrix[best_flight] = flightMatrix[best_flight] + num_planes_to_add
        remainingFuel = remainingFuel - fuelmatrix[best_flight] * num_planes_to_add
    print("flight plan")
    print(flightMatrix)

    print("passangers taking trains")
    trainMatrix = np.zeros((total_cities, total_cities))
    missedMatrix = np.zeros((total_cities, total_cities))

    for source in range(total_cities):

        for destination in range(total_cities):
            if source == destination:

                continue

            currentlyServiced = flightMatrix[source, destination] * planeCapacity

            # if all passangers serviced then stop
            currentlyUnserviced = demandmatrix[source][destination] - currentlyServiced

            trainMatrix[source, destination], missedMatrix[source, destination] = (
                calculateDemandSubstitution(
                    currentlyUnserviced,
                    subsistutionCapacityMatrix[source][destination],
                    subsitutionElasticityMatrix[source][destination],
                )
            )

    print((trainMatrix * 1000).tolist())

    print("passangers not able to find transport")
    print((missedMatrix * 1000).tolist())


minimizeDisrupted(fuel_for_all_flights * 0.6)
