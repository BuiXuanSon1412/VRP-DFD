import math

from config import Configuration


class Customer:
    lower_volume: int
    upper_volume: int
    profit: int

    x: float
    y: float

    def __init__(self, x, y):
        self.x = x
        self.y = y


def euclid_distance(a: Customer, b: Customer):
    return math.sqrt((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y))


def time_travel(a: Customer, b: Customer, vehicle_type: bool):
    return euclid_distance(a, b) / (
        Configuration.truck_speed if not vehicle_type else Configuration.drone_speed
    )


class Route:
    class Node:
        customer_id: int
        volume: int

        def __init__(self, customer_id, volume):
            self.customer_id = customer_id
            self.volume = volume

    vehicle_type: bool
    vehicle_id: int

    nodes: list[Node]
    travel_time: float

    def __init__(self, vehicle_type, vehicle_id):
        self.vehicle_type = vehicle_type
        self.vehicle_id = vehicle_id


class Solution:
    truck_routes: list[Route]
    drone_routes: list[list[Route]]
    customer_volume: list[int]

    def __init__(self):
        pass

    def is_valid(self):
        return False

    def evaluate(self):
        # calculate customer_volume and return total profit
        for truck_route in self.truck_routes:
            for node in truck_route.nodes:
                self.customer_volume[node.customer_id] += node.volume

        for drone_route in self.drone_routes:
            for route in drone_route:
                for node in route.nodes:
                    self.customer_volume[node.customer_id] += node.volume

        profit = 0
        for customer_id in range(len(Configuration.customers)):
            profit += (
                self.customer_volume[customer_id]
                * Configuration.customers[customer_id].profit
            )

        return profit

    def penalty(self):
        if self.is_valid():
            return 0

    def fitness(self, beta):
        profit = self.evaluate()

        penalty = 0
        for customer_id in range(len(Configuration.customers)):
            penalty += max(
                self.customer_volume[customer_id]
                - Configuration.customers[customer_id].lower_volume,
                0,
            )

        return profit + beta * penalty


class Chromosome:
    def __init__(self, genes):
        self.genes = genes

    def encode(self, sol: Solution):
        for truck_route in sol.truck_routes:
            for node in truck_route.nodes:
                self.genes.append((node.customer_id, node.volume))

        for drone_route in sol.drone_routes:
            for route in drone_route:
                for node in route.nodes:
                    self.genes.append((node.customer_id, node.volume))

    def decode(self) -> Solution:
        sol = Solution()

        for gene in self.genes:
            customer_id = gene.customer_id
            volume = gene.volume

        return sol
