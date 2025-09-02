import random


from data import Chromosome, Customer, Solution, Route, euclid_distance, time_travel
from config import Configuration


class Solver:
    def __init__(
        self,
        configuration,
        num_generation,
        population_size,
        elite_pct,
        crossover_pct,
        mutation_pct,
    ):
        self.configuration = configuration
        self.NUM_GENERATION = num_generation
        self.POPULATION_SIZE = population_size
        self.ELITE_PCT = elite_pct
        self.crossover_pct = crossover_pct
        self.mutation_pct = mutation_pct
        self.penalty_param: int

        self.optimal_solution: Solution

        self.node_selection_probs = []
        for customer_id in range(len(configuration.customers)):
            customer = configuration.customers[customer_id]
            self.node_selection_probs[customer_id] = (
                customer.profit
                * customer.lower_volume
                / euclid_distance(Customer(0, 0), customer)
            )
        self.node_selection_probs = [
            prob / sum(self.node_selection_probs) for prob in self.node_selection_probs
        ]

    def route(self, vehicle_type, vehicle_id, rem_time, unreached_customers):
        route = Route(vehicle_type, vehicle_id)
        rem_capacity = (
            self.configuration.drone_capacity
            if vehicle_type
            else self.configuration.truck_capacity
        )

        # depart from depot
        cur_customer_id = -1

        while True:
            next_customer_id = None
            # sample the next customer based on the calculated probability
            if cur_customer_id == -1:
                next_customer_id = random.choices(
                    range(len(self.configuration.customers)),
                    weights=self.node_selection_probs,
                    k=1,
                )[0]
            # greedy select the closest customer to delivery
            else:
                min_distance = None
                # find the closet customer
                for customer_id in range(len(self.configuration.customers)):
                    if customer_id != cur_customer_id:
                        distance = euclid_distance(
                            self.configuration.customers[customer_id],
                            self.configuration.customers[cur_customer_id],
                        )

                        if not min_distance or min_distance > distance:
                            min_distance = distance
                            next_customer_id = customer_id
            # travaling time from current customer to next customer
            # then go back to the depot
            travel_time = time_travel(
                self.configuration.customers[cur_customer_id],
                self.configuration.customers[next_customer_id],
                vehicle_type,
            ) + time_travel(
                self.configuration.customers[next_customer_id],
                Customer(0, 0),
                vehicle_type,
            )

            # is the next customer feasible for traveling time
            if travel_time <= rem_time:
                capacity = min(
                    rem_capacity,
                    self.configuration.customers[next_customer_id].lower_volume,
                )
                route.nodes.append(Route.Node(next_customer_id, capacity))
                rem_capacity = rem_capacity - capacity
                rem_time = rem_time - time_travel(
                    self.configuration.customers[cur_customer_id],
                    self.configuration.customers[next_customer_id],
                    vehicle_type,
                )
                cur_customer_id = next_customer_id
            else:
                break

            if rem_capacity == 0 or not unreached_customers:
                break
        return route

    def generate_chromosome(self):
        unreached_customers = []
        for customer in self.configuration.customers:
            if customer.lower_volume != 0:
                unreached_customers.append(customer)

        rem_time_drone = []
        for _ in range(self.configuration.num_drone):
            rem_time_drone.append(self.configuration.drone_time_limit)

        sol = Solution()

        # greedy occupation for truck
        for k in range(self.configuration.num_truck):
            if not unreached_customers:
                break
            route = self.route(
                False,
                k,
                self.configuration.system_time_limit,
                unreached_customers,
            )
            sol.truck_routes.append(route)

        # greedy occupation for drone
        tmp = None
        while True:
            for d in range(self.configuration.num_drone):
                time = min(rem_time_drone[d], self.configuration.drone_time_limit)
                route = self.route(True, d, time, unreached_customers)
                rem_time_drone[d] = rem_time_drone[d] - route.travel_time
                sol.drone_routes[d].append(route)

            if tmp and tmp == sol:
                break
            tmp = sol

            if not unreached_customers:
                break

        return sol

    def init_population(self) -> list[Chromosome]:
        P = []
        for _ in range(self.POPULATION_SIZE):
            pass
            # if random.randint(0, 1) == 0:
            #    sol = self.init_random_solution()
            # else:
            #    sol = self.init_with_permutation()
            #
            # P.append(Chromosome(sol))
        return P

    def crossover1(self, chro1: Chromosome, chro2: Chromosome):
        pivot1 = random.randint(0, len(chro1.genes) - 1)
        pivot2 = random.randint(0, len(chro2.genes) - 1)

        genes1 = chro2.genes[:pivot2] + chro1.genes[pivot1:]
        genes2 = chro1.genes[:pivot1] + chro2.genes[pivot2:]

        new_chro1 = Chromosome(genes1)
        new_chro2 = Chromosome(genes2)

        return new_chro1, new_chro2

    def crossover2(self, chro1: Chromosome, chro2: Chromosome):
        pass

    def mutate(self, chro: Chromosome):
        pass

    def educate(self, population: list[Chromosome]):
        for chro in population:
            pass

    def evaluate(self, population):
        for chro in population:
            sol = chro.decode()
            if sol.is_valid():
                if sol.profit.evaluate() > self.optimal_solution.evaluate():
                    self.optimal_solution = sol

    def update_operation_params(self):
        # Configuration.CROSSOVER_PCT =
        # Configuration.MUTATION_PCT =
        pass

    def sort(self, population, beta):
        fitness_population = []
        for chro in population:
            fitness = chro.decode().fitness()
            fitness_population.append((fitness, chro))
        fitness_population.sort()

        population.clear()

        for chro in fitness_population:
            population.append(chro)

    def control(self):
        pass

    def run(self):
        population = self.init_population()
        self.evaluate(population)

        iter = 0
        while iter != self.NUM_GENERATION:
            self.sort(population, 0)

            num_elite = self.POPULATION_SIZE * self.ELITE_PCT
            num_offspring = self.POPULATION_SIZE - num_elite

            new_population = population[:num_elite]

            while --num_offspring:
                chro1 = random.choice(population)
                chro2 = random.choice(population)

                if random.random() < self.crossover_pct:
                    # crossover operation 1

                    pass
                else:
                    # crossover operation 2
                    pass

                chro = random.choice(population)
                if random.random() < self.mutation_pct:
                    # mutation operation 1
                    pass
                else:
                    # mutation operation 2
                    pass

            self.control()
            population = new_population
            self.evaluate(population)
            iter = iter + 1
