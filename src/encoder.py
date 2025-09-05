from copy import deepcopy
import re
from sys import dont_write_bytecode
from population import Individual
from problem import Problem


class Solution:
    truck_routes: list[list[tuple[int, int]]]
    drone_routes: list[list[list[tuple[int, int]]]]


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
    sum_dist = (problem.K - 1) * avg_dist
    sum_dist += dist_mtx_truck[0][len(chro) - 1] + dist_mtx_truck[len(chro) - 1][0]

    for i in range(1, len(chro)):
        sum_dist += dist_mtx_truck[i - 1][i]

    # estimate average total distance of truck routes
    dist_per_route = sum_dist / problem.K

    routes = []
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
            route.append((chro[i], problem.customer_list[chro[i]].u))
            tmp_dist = tmp_dist + dist_mtx_truck[tmp_cust][chro[i]]
            tmp_cust = chro[i]
            i = i + 1
        if i < len(chro) and tmp_dist + dist_mtx_truck[tmp_cust][
            chro[i]
        ] + dist_mtx_truck[chro[i]][0] - dist_per_route < dist_per_route - (
            tmp_dist + dist_mtx_truck[tmp_cust][0]
        ):
            route.append((chro[i], problem.customer_list[chro[i]].u))
            tmp_dist = tmp_dist + dist_mtx_truck[tmp_cust][chro[i]]
            tmp_cust = chro[i]
            i = i + 1
        routes.append(route)
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


def repair_cap_by_truck(vio_route, routes, problem):
    # find postion for each node where it can be insered into
    for idx in range(len(vio_route)):
        if problem.check_truck_capacity(vio_route):
            return

        cust = vio_route[idx][0]
        vol = vio_route[idx][1]

        for i in range(len(routes)):
            route = routes[i]
            left_cap = problem.cal_route_volume(route) - problem.Q

            # find in each route, where should be inserted
            taken = None
            for j in range(len(route) + 1):
                tmp_cust = route[j][0] if j < len(route) else 0
                tmp_prev_cust = route[j - 1][0] if j > 0 else 0
                if (
                    problem.cal_route_truck_time(vio_route)
                    - dist_mtx_truck[tmp_prev_cust][tmp_cust]
                    + dist_mtx_truck[tmp_prev_cust][cust]
                    + dist_mtx_truck[cust][tmp_cust]
                    <= problem.v * problem.T
                ):
                    if vol > left_cap:
                        taken = left_cap
                        vol -= taken
                        routes[i].insert(j, (cust, taken))
                        vio_route[idx][1] = vol
                    else:
                        routes[i].insert(j, (cust, vol))
                        vio_route.pop(idx)


def repair_cap_by_drone(
    vio_route, drone_routes, routes, problem: Problem
) -> list[list[tuple[int, int]]]:
    rem_vol = sum(node[1] for node in vio_route) - problem.Q

    reachable = []

    # check if there is any reachable node in route
    for idx in range(len(vio_route)):
        node = vio_route[idx]
        if problem.check_drone_energy_constraint([node]):
            reachable.append((idx, node))

    if not reachable:
        return drone_routes

    while not problem.check_drone_time_constraint(drone_routes):
        # find route for each drone
        for i in range(problem.D):
            route = []
            tmp_cap = problem.tilde_Q
            tmp_cust = 0

            while True:
                nearest = None
                dist = 0
                for idx in range(len(vio_route)):
                    if tmp_cust == vio_route[idx][0]:
                        continue
                    # check validity of selection with drone constraints
                    tmp_route = [route[:], vio_route[idx]]
                    tmp_drone_routes = deepcopy(drone_routes)
                    tmp_drone_routes[i].append(tmp_route)

                    if not problem.check_drone_time_constraint(
                        tmp_drone_routes
                    ) or not problem.check_drone_energy_constraint(tmp_route):
                        continue

                    if not nearest:
                        nearest = idx
                        dist = dist_mtx_drone[tmp_cust][vio_route[idx][0]]
                    elif dist > dist_mtx_drone[tmp_cust][vio_route[idx][0]]:
                        nearest = idx
                        dist = dist_mtx_drone[tmp_cust][vio_route[idx][0]]

                if not nearest:
                    break

                tmp_vol = min(tmp_cap, vio_route[nearest][1])
                tmp_cap -= tmp_vol
                vio_route[nearest][1] -= tmp_vol
                rem_vol -= tmp_vol

                if vio_route[nearest][1] == 0:
                    vio_route.pop(nearest)

                route.append((vio_route[nearest][0], tmp_vol))

                if rem_vol <= 0:
                    break

            drone_routes[i].append(route)
            if rem_vol <= 0:
                return drone_routes
    return drone_routes


def repair_cap_by_lowering(problem: Problem):
    pass


def relax_cap(vio_cap_routes, drone_routes, routes, problem: Problem):
    vio = False

    for i in range(len(vio_cap_routes)):
        # resolve each route iteratively
        repair_cap_by_truck(vio_cap_routes[i], routes, problem)

        if problem.check_truck_capacity(vio_cap_routes[i]):
            repair_cap_by_drone(vio_cap_routes[i], drone_routes, routes, problem)

        if problem.check_truck_capacity(vio_cap_routes[i]):
            pass

    repair_cap_by_lowering(problem)


def decode2(indi: Individual, problem: Problem):
    chro = indi.chromosome

    if not chro:
        return None

    sol = Solution()

    routes = fair_split(chro, problem)

    vio_dist_routes = []
    vio_cap_routes = []

    for route in routes:
        if problem.check_truck_time_constraint(route):
            vio_dist_routes.append(route)
        if problem.check_truck_capacity(route):
            vio_cap_routes.append(routes.pop(route))

    routes = [
        route
        for route in routes
        if route not in vio_cap_routes and route not in vio_dist_routes
    ]

    if not vio_dist_routes:
        if not vio_cap_routes:
            sol.truck_routes = routes
            sol.drone_routes = []
            return sol
        else:
            drone_routes = []
            relax_cap(vio_cap_routes, drone_routes, routes, problem)

    else:
        pass
