from copy import deepcopy
from population import Individual
from problem import Problem


class Solution:
    truck_routes: list[list[tuple[int, int]]]
    drone_routes: list[list[list[tuple[int, int]]]]


"""
Approximate algorithm to split chromosome into truck routes
based on route distance travelled by truck
"""


def fair_split(chro, problem: Problem):
    # average distance from depot(0, 0)
    avg_dist = sum(problem.d[0]) / len(problem.d[0])

    # estimate total distance of all truck routes
    sum_dist = (problem.K - 1) * avg_dist
    sum_dist += problem.d[0][len(chro) - 1] + problem.d[len(chro) - 1][0]

    for i in range(1, len(chro)):
        sum_dist += problem.d[i - 1][i]

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
            and tmp_dist + problem.d[tmp_cust][chro[i]] + problem.d[chro[i]][0]
            > dist_per_route
        ):
            route.append((chro[i], problem.customer_list[chro[i]].u))
            tmp_dist = tmp_dist + problem.d[tmp_cust][chro[i]]
            tmp_cust = chro[i]
            i = i + 1
        if i < len(chro) and tmp_dist + problem.d[tmp_cust][chro[i]] + problem.d[
            chro[i]
        ][0] - dist_per_route < dist_per_route - (tmp_dist + problem.d[tmp_cust][0]):
            route.append((chro[i], problem.customer_list[chro[i]].u))
            tmp_dist = tmp_dist + problem.d[tmp_cust][chro[i]]
            tmp_cust = chro[i]
            i = i + 1
        routes.append(route)
    return routes


def repair_cap_by_truck(vio_route, routes, problem):
    removal = []
    rem_vol = problem.cal_route_volume(vio_route) - problem.Q
    # find postion for each node where it can be insered into
    for idx in range(len(vio_route)):
        if problem.check_truck_capacity(vio_route):
            return

        cust = vio_route[idx][0]
        vol = vio_route[idx][1]

        # iterate through non-violated routes to transfer freight from violated route
        for i in range(len(routes)):
            route = routes[i]
            left_cap = problem.Q - problem.cal_route_volume(route)

            # find in each route, where should be inserted
            taken = None

            for j in range(len(route) + 1):
                tmp_cust = route[j][0] if j < len(route) else 0
                tmp_prev_cust = route[j - 1][0] if j > 0 else 0
                if (
                    problem.cal_truck_route_time(vio_route) * problem.v
                    - problem.d[tmp_prev_cust][tmp_cust]
                    + problem.d[tmp_prev_cust][cust]
                    + problem.d[cust][tmp_cust]
                    <= problem.v * problem.T
                ):
                    taken = min(min(left_cap, vol), rem_vol)
                    left_cap -= taken
                    vol -= taken
                    rem_vol -= taken

                    if vol == 0 or left_cap == 0:
                        routes[i].insert(j, (cust, taken))
                        removal.append(idx)
                        break
                    else:
                        routes[i][1] = vol
            if vol == 0:
                break
        if rem_vol == 0:
            break

    for i in removal:
        vio_route.pop(i)


def repair_cap_by_drone(vio_route, drone_routes, problem: Problem):
    rem_vol = sum(node[1] for node in vio_route) - problem.Q

    reachable = []

    # check if there is any reachable node in route
    for idx in range(len(vio_route)):
        node = vio_route[idx]
        if problem.check_drone_energy_constraint([node]):
            reachable.append((idx, node))

    if not reachable:
        return

    while not problem.check_drone_time_constraint(drone_routes):
        # find route for each drone
        for i in range(problem.D):
            route = []
            tmp_cap = problem.tilde_Q
            tmp_cust = 0

            # greedily find the route for current frone
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
                        dist = problem.tilde_d[tmp_cust][vio_route[idx][0]]
                    elif dist > problem.tilde_d[tmp_cust][vio_route[idx][0]]:
                        nearest = idx
                        dist = problem.tilde_d[tmp_cust][vio_route[idx][0]]

                if not nearest:
                    break

                taken = min(min(tmp_cap, vio_route[nearest][1]), rem_vol)
                tmp_cap -= taken
                vio_route[nearest][1] -= taken
                rem_vol -= taken

                # if violated route's node got volume of 0, it is popped out
                if vio_route[nearest][1] == 0:
                    vio_route.pop(nearest)

                route.append((vio_route[nearest][0], taken))

                # the violated route become non-violated
                if rem_vol == 0:
                    break

            drone_routes[i].append(route)
            if rem_vol == 0:
                break


def repair_cap_by_lowering(vio_routes, routes, drone_routes, problem: Problem):
    rem_vol = 0


def repair_cap_by_vehicle(vio_routes, drone_routes, routes, problem: Problem):
    for i in range(len(vio_routes)):
        # resolve each route iteratively
        repair_cap_by_truck(vio_routes[i], routes, problem)

    for i in range(len(vio_routes)):
        if problem.check_truck_capacity(vio_routes[i]):
            repair_cap_by_drone(vio_routes[i], drone_routes, problem)

    repair_cap_by_lowering(vio_routes, routes, drone_routes, problem)


# greedily rearrange to route by finding the nearest customer to travel
def rearrange(route, problem):
    cpy_route = route.copy()
    tmp_route = []
    cur_cust = 0
    num_iter = len(route) - 1
    for _ in range(num_iter):
        nearest = None
        dist = 0
        for i in range(len(cpy_route)):
            if cpy_route[i][0] == cur_cust:
                continue
            if not nearest or dist > problem.d[cur_cust][cpy_route[i][0]]:
                nearest = i
                dist = problem.d[cur_cust][cpy_route[i][0]]

        tmp_route.append(cpy_route.pop(nearest))

    if problem.cal_truck_route_time(tmp_route) < problem.cal_truck_route_time(route):
        route = tmp_route


def relax_dist(routes, problem):
    for i in range(len(routes)):
        rearrange(routes[i], problem)


def repair_dist_by_truck(vio_route, routes, problem):
    removal = []
    for idx in range(len(vio_route)):
        for i in range(len(routes)):
            route = routes[i]

            # find in each route, where should be inserted
            for j in range(len(route) + 1):
                if problem.check_truck_time_constraint(
                    route[:j] + vio_route[idx] + route[j:]
                ):
                    routes[i].insert(j, vio_route[idx])
                    removal.append(idx)

                    if problem.check_truck_time_constraint(
                        [
                            vio_route[i]
                            for i in range(len(vio_route))
                            if i not in removal
                        ]
                    ):
                        for i in removal:
                            vio_route.pop(i)
                        return

                    break


def repair_dist_by_drone(vio_route, drone_routes, problem: Problem):
    reachable = []

    # check if there is any reachable node in route
    for idx in range(len(vio_route)):
        node = vio_route[idx]
        if problem.check_drone_energy_constraint([node]):
            reachable.append((idx, node))

    if not reachable:
        return

    # find the node with lowest volume to minimize drone usage
    vio_route.sort(key=lambda node: node[1])
    for i in range(len(vio_route)):
        cur_cust = vio_route[i][0]
        prev_cust = vio_route[i - 1][0] if i > 0 else 0
        next_cust = vio_route[i + 1][0] if i < len(vio_route) - 1 else 0
        if (
            problem.cal_truck_route_time(vio_route)
            - problem.d[cur_cust][prev_cust]
            - problem.d[cur_cust][next_cust]
            + problem.d[prev_cust][next_cust]
            <= problem.T * problem.v
        ) and vio_route[i] in reachable:
            vol = vio_route[i][1]
            drone_use = vol / problem.tilde_Q

    while not problem.check_drone_time_constraint(drone_routes):
        # find route for each drone
        for i in range(problem.D):
            route = []
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
                        dist = problem.tilde_d[tmp_cust][vio_route[idx][0]]
                    elif dist > problem.tilde_d[tmp_cust][vio_route[idx][0]]:
                        nearest = idx
                        dist = problem.tilde_d[tmp_cust][vio_route[idx][0]]

                if not nearest:
                    break

                if vio_route[nearest][1] == 0:
                    vio_route.pop(nearest)

                route.append((vio_route[nearest][0], 0))

            drone_routes[i].append(route)


def decode(indi: Individual, problem: Problem):
    chro = indi.chromosome

    if not chro:
        return None

    sol = Solution()

    routes = fair_split(chro, problem)

    relax_dist(routes, problem)

    vio_time_routes = []

    for route in routes:
        if problem.check_truck_time_constraint(route):
            vio_time_routes.append(route)
        # if problem.check_truck_capacity(route):
        #    vio_cap_routes.append(route)

    routes = [route for route in routes if route not in vio_time_routes]

    if not vio_time_routes:
        repair_dist_by_truck(vio_time_routes, routes, problem)

    drone_routes = []
    repair_dist_by_drone(vio_time_routes, drone_routes, problem)

    vio_cap_routes = []
    for route in routes:
        if problem.check_truck_capacity(route):
            vio_cap_routes.append(route)

    routes = [route for route in routes if route not in vio_cap_routes]

    if not vio_cap_routes:
        sol.truck_routes = routes
        sol.drone_routes = drone_routes

        return sol
    else:
        repair_cap_by_vehicle(vio_cap_routes, drone_routes, routes, problem)
        if vio_cap_routes:
            repair_cap_by_lowering(vio_cap_routes, routes, drone_routes, problem)

        sol.truck_routes = routes
        sol.drone_routes = drone_routes
        return sol
