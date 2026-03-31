# Flight Cutter
#### Helping airlines minimize impact to their operations during a crisis.

## Inspiration

The US-Iran war and the closing of the Strait of Hormuz have launched shockwaves across global supply chains, causing acute shortages of brent crude, liquified natural gas and diesel. Of particular note is the disruption of Jet Fuel, both in Asian and European markets. After April 11th, the final shipment will arrive in Europe, with Jet Fuel expected to become 40% scarcer [1], meaning airlines must begin making difficult decisions and begin limiting service.
## Our Solution

Our project aims to provide enterprise software for airline providers, allowing them to make an informed decision about which routes are least valuable and so should be cut. Given a fixed amount of jet fuel stored at an airport, as well as its local price, the algorithm will begin cutting existing routes until a fuel equilibrium is accomplished. We use a heuristic function that considers route profitability, the passenger demand of the route, and the ease of providing replacement services (for example rail). The information is available both visually, provided through a flight map that updates dynamically, and in csv format, to be used by the airline at a later date.
Implementation Details

Our algorithm for determining which routes to keep is a greedy search on a multiple knapsack problem. In this case, we are constrained by the available fuel available at each airport, and are seeking to optimize our custom heuristic function as follows. Give a path between source and destination airports i and j, we define the fuel cost as $f_{ij}$ and the heuristic $h_{ij}$ as

$$h_{ij} = \alpha \cdot \frac{\text{Route Profit - Profit of Least Profitable Route}}{\text{Difference Between Min and Max Profit}} + \\ \beta \cdot (1 - \text{Route's Ease of Replacement Factor}) + \gamma \cdot \frac{\text{Currently Unfilled Demand}}{\text{Route's Max Demand}}$$

We then choose the route to cut with the lowest $\frac{h_{if}}{f_{if}}$ where the destination is also below its fuel budget, unless all other routes are also below and in that case it is simply the minimum. The heuristic's three tunable parameters: $\alpha, \beta, \gamma$ allow the algorithm to prioritize different goals, namely profit, importance of routes (a flight from London to Glasgow is less 'essential' than a flight from London to Reykjavik as it is much easier to replace), and finally the demand of the route.

We implemented our interface in PyQt6. Our system aims to emulate a crisis-response software, starting at full operational capacity and allowing the user to input a reduction in available jet fuel, either localised at specific airport or across the entire network. Then, using the above algorithm, the least desirable routes are pruned and this is fed back to the user, both in a table on the right showing the cancelled flights, and visually on the network itself by changing the edge color based on the proportion of routes cut. The user can also tune the values of and \(\gamma), mentioned above, allowing them to set their strategic priorities. High-level and detailed information is made available to the user, with the total number of passengers disrupted as well as revenue impacts displayed, and also, for each cancelled flight, an estimation of the number of passengers switching to rail and the number forced to not travel is displayed.
## Result

Overall, I would say our project accomplished the goals it set out to do. Changing the heuristic parameters has an intuitive effect on the final result, and the reduction in routes is very easily digested by the user from the change in edge color. The user also has very fine control over the simulation, by being able to control individual price and availability of fuel, making it useful in the real world, but can also make higher level adjustments to gain a general overview of how a fuel shortage could impact their operations. Obvious improvement could be made to our search algorithm, for example optimal solutions exist to multi-knapsack problems, an improvement over our greedy search. Another area for improve would be to factor in more advanced fuel logistics, for example round-trip fuelling, where a plane carries fuel for the return journey, potentially saving money if the price at the destination is high but at the cost of additional weight and therefore fuel consumption.

## References
[1] European jet fuel supplies under threat as Iran war halts flows. Financial Times.
