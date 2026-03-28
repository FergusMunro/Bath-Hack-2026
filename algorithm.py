fuelmatrix = [
    [0, 2981, 2409, 4165, 2334],
    [2981, 0, 1, 1, 1],
    [1, 1, 0, 1, 1],
    [1, 1, 1, 0, 1],
    [1, 1, 1, 1, 0],
]

demandmatrix = [
    [0, 1, 1, 1, 1],
    [1, 0, 1, 1, 1],
    [1, 1, 0, 1, 1],
    [1, 1, 1, 0, 1],
    [1, 1, 1, 1, 0],
]

subsistutionCapacityMatrix = [
    [0, 1, 1, 1, 1],
    [1, 0, 1, 1, 1],
    [1, 1, 0, 1, 1],
    [1, 1, 1, 0, 1],
    [1, 1, 1, 1, 0],
]

subsitutionElasticityMatrix = [
    [0, 1, 1, 1, 1],
    [1, 0, 1, 1, 1],
    [1, 1, 0, 1, 1],
    [1, 1, 1, 0, 1],
    [1, 1, 1, 1, 0],
]

flightMatrix = [
    [0,0,0,0,0],
    [0,0,0,0,0],
    [0,0,0,0,0],
    [0,0,0,0,0],
    [0,0,0,0,0],
]


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

def minimizeDisrupted():

