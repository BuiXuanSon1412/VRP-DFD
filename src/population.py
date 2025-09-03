import math
import random


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


class Channel:
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
    drone_route: list[list[Route]]


def euclide_distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))


def travel_time(x1, y1, x2, y2, vehicle_type, channel):
    return euclide_distance(x1, y1, x2, y2) / (
        channel.drone_speed if vehicle_type else channel.truck_speed
    )


def check_duration(
    cur_customer_id,
    next_customer_id,
    rem_duration,
    drone_sys_time,
    vehicle_type,
    vehicle_id,
    channel,
):
    # check vehicle remaining time
    cur_to_next = travel_time(
        channel.x[cur_customer_id],
        channel.y[cur_customer_id],
        channel.x[next_customer_id],
        channel.y[next_customer_id],
        vehicle_type,
        channel,
    )
    next_to_depot = travel_time(
        channel.x[next_customer_id],
        channel.y[next_customer_id],
        channel.x[0],
        channel.y[0],
        vehicle_type,
        channel,
    )

    if rem_duration < cur_to_next + next_to_depot or (
        vehicle_type and drone_sys_time[vehicle_id] < cur_to_next + next_to_depot
    ):
        return False, cur_to_next

    return True, cur_to_next


def decode(individual: Individual, channel: Channel):
    chromosome = individual.chromosome  # chromosome = [(customer_id, volume)]

    if not chromosome:
        return

    drone_sys_time = [channel.system_duration] * channel.num_drone

    solution = None

    vehicle_id = 0
    vehicle_type = False

    i = 0

    while i < len(chromosome):
        # update route identifier by (vehicle_id, vehicle_type) after each route
        if i != 0:
            if not vehicle_type and vehicle_id == channel.num_truck:
                vehicle_id = 0
                vehicle_type = True
            elif vehicle_type and vehicle_id == channel.num_drone:
                vehicle_id = 0

        route = Route()
        rem_duration = (
            channel.drone_duration if vehicle_type else channel.system_duration
        )
        rem_capacity = (
            channel.drone_capacity if vehicle_type else channel.truck_capacity
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
                channel,
            )
            if feasible:
                # take volume as remaining capacity or volume in currrent gene
                taken = min(rem_capacity, volume)
                volume = volume - taken
                rem_capacity = rem_capacity - taken

                rem_duration = rem_duration - cur_to_next
                # reach vehicle's capacity
                if rem_capacity == 0:
                    # there still remains freight in the current element
                    if volume > 0:
                        chromosome[i] = (next_customer_id, taken)
                        chromosome.insert(i + 1, (next_customer_id, volume))
                    vehicle_id = vehicle_id + 1
                    break
                route.customers.append((next_customer_id, taken))
                cur_customer_id = next_customer_id

            else:  # can not go to next_customer_id because of remaining duration
                # when drone is not at depot
                if cur_customer_id != 0 and vehicle_type:
                    drone_sys_time[vehicle_id] -= travel_time(
                        channel.x[cur_customer_id],
                        channel.y[cur_customer_id],
                        channel.x[0],
                        channel.y[0],
                        vehicle_type,
                        channel,
                    )
                vehicle_id = vehicle_id + 1
                break

    return solution


def crossover1(channel: Channel, indi1: Individual, indi2: Individual):
    pass


def crossover2(channel: Channel, indi1: Individual, indi2: Individual):
    pass


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

    new_indi = Individual()
    new_indi.chromosome = []
    for i in range(0, pivot1):
        new_indi.chromosome.append(indi.chromosome[i])

    for i in range(pivot2, pivot2 + mutation_len):
        new_indi.chromosome.append(indi.chromosome[i])

    for i in range(pivot1 + mutation_len, pivot2):
        new_indi.chromosome.append(indi.chromosome[i])

    for i in range(pivot1, pivot1 + mutation_len):
        new_indi.chromosome.append(indi.chromosome[i])

    for i in range(pivot2 + mutation_len, chro_len):
        new_indi.chromosome.append(indi.chromosome[i])

    return new_indi


def mutation_operation2():
    pass


def crossover(channel: Channel, indi1: Individual, indi2: Individual):
    pass
