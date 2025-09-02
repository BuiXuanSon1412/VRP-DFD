from config import Configuration
from solver import Solver


def read_input():
    pass


filename = "./data"
configuration = Configuration()
configuration.load_params(filename)

solver = Solver(configuration, num_generation=)
solver.run()
