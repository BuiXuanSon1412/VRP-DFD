from data import Customer


class Configuration:
    truck_speed: float
    drone_speed: float

    customers: list[Customer]

    truck_capacity: int
    drone_capacity: int

    drone_time_limit: int
    system_time_limit: int

    num_truck: int
    num_drone: int

    @staticmethod
    def load_params(filename):
        pass
