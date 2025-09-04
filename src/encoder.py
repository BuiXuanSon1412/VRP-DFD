from math import dist
from population import Problem, Individual, Solution

dist_mtx_truck: list[list[float]] = [[]]
dist3: list[list[list[float]]] = [[[]]]

dist_mtx_truck: list[list[float]] = [[]]
dist_mtx_truck3: list[list[list[float]]] = [[[]]]


dist_mtx_drone: list[list[float]] = [[]]

"""
Approximate algorithms to split the permuation of [1..n]
based on route distance travelled by truck
"""


def fair_split(chro, problem: Problem):
    # average distance from depot(0, 0)
    avg_dist = sum(dist_mtx_truck[0]) / len(dist_mtx_truck[0])

    # estimate total distance of all truck routes
    sum_dist = (problem.num_truck - 1) * avg_dist
    sum_dist += dist_mtx_truck[0][len(chro) - 1] + dist_mtx_truck[len(chro) - 1][0]

    for i in range(1, len(chro)):
        sum_dist += dist_mtx_truck[i - 1][i]

    # estimate average total distance of truck routes
    dist_per_route = sum_dist / problem.num_truck

    routes = []
    dists = []
    i = 0
    while i < len(chro):
        route = []
        tmp_dist = 0
        tmp_cust = 0
        while (
            i < len(chro)
            and tmp_dist
            + dist_mtx_truck[tmp_cust][chro[i]]
            + dist_mtx_truck[chro[i]][0]
            > dist_per_route
        ):
            route.append((chro[i], problem.upper_volume[chro[i]]))
            tmp_dist = tmp_dist + dist_mtx_truck[tmp_cust][chro[i]]
            tmp_cust = chro[i]
            i = i + 1
        if i < len(chro) and tmp_dist + dist_mtx_truck[tmp_cust][
            chro[i]
        ] + dist_mtx_truck[chro[i]][0] - dist_per_route < dist_per_route - (
            tmp_dist + dist_mtx_truck[tmp_cust][0]
        ):
            route.append((chro[i], problem.upper_volume[chro[i]]))
            tmp_dist = tmp_dist + dist_mtx_truck[tmp_cust][chro[i]]
            tmp_cust = chro[i]
            i = i + 1
        tmp_dist = tmp_dist + dist_mtx_truck[tmp_cust][0]
        routes.append(route)
        dists.append(tmp_dist)
    return routes


def optimal_removal(route):
    if not route:
        return None

    route.append(0)

    tmp = (
        dist_mtx_truck[0][route[1]]
        + dist_mtx_truck[route[1]][route[2]]
        - dist_mtx_truck[0][route[2]]
    )
    opt = 0
    for i in range(1, len(route) - 1):
        if (
            tmp
            < dist_mtx_truck[i - 1][i]
            + dist_mtx_truck[i][i + 1]
            - dist_mtx_truck[i - 1][i + 1]
        ):
            tmp = (
                dist_mtx_truck[i - 1][i]
                + dist_mtx_truck[i][i + 1]
                - dist_mtx_truck[i - 1][i + 1]
            )
            opt = i

    return opt


def optimal_insertion(route):
    if not route:
        return None

    route.append(0)

    tmp = (
        dist_mtx_truck[0][route[1]]
        + dist_mtx_truck[route[1]][route[2]]
        - dist_mtx_truck[0][route[2]]
    )
    opt = 0
    for i in range(1, len(route) - 1):
        if (
            tmp
            > dist_mtx_truck[i - 1][i]
            + dist_mtx_truck[i][i + 1]
            - dist_mtx_truck[i - 1][i + 1]
        ):
            tmp = (
                dist_mtx_truck[i - 1][i]
                + dist_mtx_truck[i][i + 1]
                - dist_mtx_truck[i - 1][i + 1]
            )
            opt = i

    return opt


def relax_dist(parts, problem: Problem):
    violated = []
    not_violated = []

    parts.sort(key=lambda part: part[0], reverse=True)
    # change position


def customer_in_range(range, problem: Problem):
    customers = []
    for customer in range(1, problem.num_customer):
        if 2 * dist_mtx_truck[0][customer] <= range:
            customers.append(customer)
    return customers


def relax_cap(violated_route, not_violated, problem: Problem):
    rem = sum(i[1] for i in violated_route[1]) - problem.truck_capacity

    # sorted_node = sorted(violated_route[1], key=lambda x: problem.unit_profit[x[0]])

    # take from customer with the lowest profit unit
    for node in violated_route[1]:
        # search in all non-violated routes to find the insertion index which does not violate time limit
        # also be the maximum inserted volume

        for route in not_violated:
            distance = route[0]
            path = route[1].copy()
            rem_cap = problem.truck_capacity - sum(i[1] for i in path)

            if not rem_cap:
                continue

            path.insert((0, 0))
            path.append((0, 0))

            id = 0
            taken = 0

            if (
                distance + dist3[0][node[0]][path[0]] - dist_mtx_truck[0][path[0]]
                <= problem.system_duration * problem.drone_speed
            ):
                tmp = min(node[1], rem_cap)
                if taken < tmp:
                    taken = tmp
                    id = 0
            for k in range(len(path)):
                if (
                    distance + dist3[0][node[0]][path[0]] - dist_mtx_truck[0][path[0]]
                    <= problem.system_duration * problem.drone_speed
                ):
                    tmp = min(node[1], rem_cap)
                    if taken <= tmp:
                        taken = tmp
                        id = k


def decode2(indi: Individual, problem: Problem):
    chro = indi.chromosome

    if not chro:
        return None

    sol = Solution()

    routes, dists = fair_split(chro, problem)

    max_truck_dist = problem.system_duration * problem.truck_speed
    max_drone_dist = problem.drone_duration * problem.drone_speed

    if all(route[0] <= max_truck_dist for route in routes):
        if all(
            (sum(i[1] for i in route[1]) <= problem.truck_capacity) for route in routes
        ):
            # no capacity and duration violation
            sol.truck_routes = [route[1] for route in routes]
            sol.drone_routes = []
            return sol
        else:
            # capacity violation
            not_violated = []
            violated = []

            for route in routes:
                volume = sum(i[1] for i in route[1])
                if volume <= problem.truck_capacity:
                    not_violated.append(route)
                else:
                    violated.append(route)

            # split volume for non-violated truck
            while violated:
                for route in violated:
                    # take the node with lowest
                    x = relax_cap(route, not_violated, problem)
                    if x:
                        violated.remove(route)

            # if drones possibly solve reduntant volume

    else:
        # relax_dist(parts, problem)
        # split freight to drones to satisfy system time limit

        # split freight for drone
        if all(
            (sum(i[1] for i in route[1]) <= problem.truck_capacity) for route in routes
        ):
            pass
        else:
            pass
