import math
import random
import copy
import heapq


class Individual:
    def __init__(self, chromosome=None):
        self.chromosome = chromosome
        self.objectives = None  # Objectives vector

        self.domination_count = None  # be dominated
        self.dominated_solutions = None  # dominate
        self.crowding_distance = None
        self.rank = None

    def gen_random(self, problem, create_solution):
        self.chromosome = create_solution(problem)

    # Dominate operator
    def dominates(self, other_individual):
        tolerance = 0
        and_condition = True
        or_condition = False
        # for first, second in zip(self.objectives, other_individual.objectives):
        #    and_condition = and_condition and (first <= second + tolerance)
        #    or_condition = or_condition or (first < second - tolerance)
        return and_condition and or_condition

    def repair(self):
        # for i in range(len(self.chromosome)):
        pass


class Problem:
    num_customer: int

    unit_profit: list[int]
    lower_volume: list[int]
    upper_volume: list[int]
    x: list[float]
    y: list[float]

    num_truck: int
    num_drone: int

    truck_capacity: int
    drone_capacity: int

    truck_speed: int
    drone_speed: int

    system_duration: float
    drone_duration: float


class Route:
    customers: list[tuple[int, int]]


class Solution:
    truck_routes: list[Route]
    drone_routes: list[list[Route]]


def euclide_distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))


def travel_time(x1, y1, x2, y2, vehicle_type, problem):
    return euclide_distance(x1, y1, x2, y2) / (
        problem.drone_speed if vehicle_type else problem.truck_speed
    )


def check_duration(
    cur_customer_id,
    next_customer_id,
    rem_duration,
    drone_sys_time,
    vehicle_type,
    vehicle_id,
    problem,
):
    # check vehicle remaining time
    cur_to_next = travel_time(
        problem.x[cur_customer_id],
        problem.y[cur_customer_id],
        problem.x[next_customer_id],
        problem.y[next_customer_id],
        vehicle_type,
        problem,
    )
    next_to_depot = travel_time(
        problem.x[next_customer_id],
        problem.y[next_customer_id],
        problem.x[0],
        problem.y[0],
        vehicle_type,
        problem,
    )

    if rem_duration < cur_to_next + next_to_depot or (
        vehicle_type and drone_sys_time[vehicle_id] < cur_to_next + next_to_depot
    ):
        return False, cur_to_next

    return True, cur_to_next


def decode1(individual: Individual, problem: Problem):
    chromosome = individual.chromosome  # chromosome = [(customer_id, volume)]

    if not chromosome:
        return

    drone_sys_time = [problem.system_duration] * problem.num_drone

    solution = Solution()

    vehicle_id = 0
    vehicle_type = False

    i = 0

    while i < len(chromosome):
        # update route identifier by (vehicle_id, vehicle_type) after each route
        if i != 0:
            if not vehicle_type and vehicle_id == problem.num_truck:
                vehicle_id = 0
                vehicle_type = True
            elif vehicle_type and vehicle_id == problem.num_drone:
                vehicle_id = 0

        route = Route()
        rem_duration = (
            problem.drone_duration if vehicle_type else problem.system_duration
        )
        rem_capacity = (
            problem.drone_capacity if vehicle_type else problem.truck_capacity
        )

        cur_customer_id = 0  # depot identifier

        while True:
            next_customer_id = chromosome[i][0]
            volume = chromosome[i][1]

            feasible, cur_to_next = check_duration(
                cur_customer_id,
                next_customer_id,
                rem_duration,
                drone_sys_time,
                vehicle_type,
                vehicle_id,
                problem,
            )
            if feasible:
                # take volume as remaining capacity or volume in currrent gene
                taken = min(rem_capacity, volume)
                volume = volume - taken
                rem_capacity = rem_capacity - taken

                rem_duration = rem_duration - cur_to_next
                route.customers.append((next_customer_id, taken))
                # reach vehicle's capacity
                if rem_capacity == 0:
                    # there still remains freight in the current element
                    if volume > 0:
                        chromosome[i] = (next_customer_id, taken)
                        chromosome.insert(i + 1, (next_customer_id, volume))

                    if vehicle_type:
                        solution.drone_routes[vehicle_id].append(route)
                    else:
                        solution.truck_routes.append(route)

                    vehicle_id = vehicle_id + 1
                    break
                cur_customer_id = next_customer_id

            else:  # can not go to next_customer_id because of remaining duration
                # when drone is not at depot
                if cur_customer_id != 0 and vehicle_type:
                    drone_sys_time[vehicle_id] -= travel_time(
                        problem.x[cur_customer_id],
                        problem.y[cur_customer_id],
                        problem.x[0],
                        problem.y[0],
                        vehicle_type,
                        problem,
                    )
                    if vehicle_type:
                        solution.drone_routes[vehicle_id].append(route)
                    else:
                        solution.truck_routes.append(route)

                vehicle_id = vehicle_id + 1
                break

    return solution


def crossover1(problem: Problem, indi1: Individual, indi2: Individual):
    if not indi1.chromosome or not indi2.chromosome:
        return None

    chro1 = indi1.chromosome
    chro2 = indi2.chromosome

    pivot = random.randint(0, min(len(chro1), len(chro2)) - 1)

    new_indi1 = Individual()
    new_indi1.chromosome = copy.deepcopy(chro1)
    new_indi1.chromosome[:pivot] = chro2[:pivot]

    new_indi2 = Individual()
    new_indi2.chromosome = copy.deepcopy(chro2)
    new_indi2.chromosome[:pivot] = chro1[:pivot]

    return new_indi1, new_indi2


def crossover2(problem: Problem, indi1: Individual, indi2: Individual):
    if not indi1.chromosome or not indi2.chromosome:
        return None

    chro1 = indi1.chromosome
    chro2 = indi2.chromosome

    size = random.randint(1, min(len(chro1), len(chro2)))
    pivot = random.randint(0, min(len(chro1), len(chro2)) - 1)

    new_indi1 = Individual()
    new_indi1.chromosome = copy.deepcopy(chro1)
    new_indi1.chromosome[pivot : pivot + size] = chro2[pivot : pivot + size]

    new_indi2 = Individual()
    new_indi2.chromosome = copy.deepcopy(chro2)
    new_indi2.chromosome[pivot : pivot + size] = chro1[pivot : pivot + size]

    return new_indi1, new_indi2


def mutation_operation1(indi: Individual):
    if not indi.chromosome:
        return

    chro_len = len(indi.chromosome)
    mutation_len = random.randint(1, max(1, (int)(chro_len / 10)))

    pivot1 = random.randint(0, chro_len - 1 - 2 * mutation_len)
    pivot2 = random.randint(
        pivot1 + mutation_len,
        min(chro_len - 1 - mutation_len, pivot1 + 2 * mutation_len),
    )

    tmp_chro = indi.chromosome[pivot1 : pivot1 + mutation_len]
    indi.chromosome[pivot1 : pivot1 + mutation_len] = indi.chromosome[
        pivot2 : pivot2 + mutation_len
    ]
    indi.chromosome[pivot2 : pivot2 + mutation_len] = tmp_chro


def mutation_operation2(indi: Individual):
    if not indi.chromosome:
        return

    chro_len = len(indi.chromosome)
    mutation_len = random.randint(1, max(1, (int)(chro_len / 10)))

    pivot1 = random.randint(0, chro_len - 1 - 2 * mutation_len)
    pivot2 = random.randint(
        pivot1 + mutation_len,
        min(chro_len - 1 - mutation_len, pivot1 + 2 * mutation_len),
    )

    indi.chromosome[pivot1 : pivot1 + mutation_len].reverse()
    indi.chromosome[pivot2 : pivot2 + mutation_len].reverse()

    tmp_chro = indi.chromosome[pivot1 : pivot1 + mutation_len]
    indi.chromosome[pivot1 : pivot1 + mutation_len] = indi.chromosome[
        pivot2 : pivot2 + mutation_len
    ]
    indi.chromosome[pivot2 : pivot2 + mutation_len] = tmp_chro
