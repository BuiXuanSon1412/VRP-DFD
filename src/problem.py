class Customer:
    def __init__(self, lower_demand, upper_demand, profit_unit, service_time, x, y):
        self.l = lower_demand
        self.u = upper_demand
        self.w = profit_unit
        self.t = service_time
        self.x = x
        self.y = y
        
class Problem:
    def __init__(self, customer_list, number_of_trucks, number_of_drones, distance_matrix_truck,
                distance_matrix_drone, truck_capacity, drone_capacity, drone_energy,
                speed_of_truck, speed_of_drone, launch_time, land_time, system_time,
                energy_consumption_rate, weight_of_drone):
        self.customer_list = customer_list
        self.K = number_of_trucks
        self.D = number_of_drones
        self.d = distance_matrix_truck
        self.tilde_d = distance_matrix_drone
        self.Q = truck_capacity
        self.tilde_Q = drone_capacity
        self.E = drone_energy
        self.v = speed_of_truck
        self.tilde_v = speed_of_drone
        self.tau_l = launch_time
        self.tau_r = land_time
        self.T = system_time
        self.lbda = energy_consumption_rate
        self.tilde_qo = weight_of_drone

    def check_truck_capacity(self, route):
        total = 0
        for customer in route:
            total = total + customer[1]
        if total <= self.Q:
            return True
        else:
            return False

    def check_drone_capacity(self, route):
        total = 0
        for customer in route:
            total = total + customer[1]
        if total <= self.tilde_Q:
            return True
        else:
            return False

        
    def cal_truck_route_time(self, route):
        total_time = 0
        if len(route) == 0:
            return 0
        total_time = total_time + self.d[0][route[0][0]]/self.v + self.customer_list[route[0][0]].t
        for i in range(len(route) - 1):
            total_time = total_time + self.d[route[i][0]][route[i+1][0]]/self.v + self.customer_list[route[i+1][0]].t
        total_time = total_time + self.d[route[-1][0]][0]/self.v
        return total_time
    
    def check_truck_time_constraint(self, route):
        total_time = self.cal_truck_route_time(route)
        if total_time <= self.T:
            return True
        else:
            return False

    def cal_drone_route_time(self, route):
        total_time = 0
        if len(route) == 0:
            return 0
        total_time = total_time + self.tau_l + self.tilde_d[0][route[0][0]]/self.tilde_v + self.tau_r + self.customer_list[route[0][0]].t
        for i in range(len(route) - 1):
            total_time = total_time + self.tau_l + self.tilde_d[route[i][0]][route[i+1][0]]/self.tilde_v + self.tau_r + self.customer_list[route[i+1][0]].t
        total_time = total_time + self.tau_l + self.tilde_d[route[-1][0]][0]/self.tilde_v + self.tau_r
        return total_time
    
    def check_drone_time_constraint(self, multi_route):
        total_time = 0
        for route in multi_route:
            total_time = total_time + self.cal_drone_route_time(route)
        if total_time <= self.T:
            return True
        else:
            return False

    def cal_drone_route_energy(self, route):
        total_energy = 0
        if len(route) == 0:
            return 0
        total_demand = 0
        for customer in route:
            total_demand = total_demand + customer[1]

        total_energy = total_energy + self.lbda*(self.tilde_qo + total_demand)*self.tilde_d[0][route[0][0]]/self.tilde_v 
        total_demand = total_demand - route[0][1]
        total_energy = total_energy + self.lbda* total_demand * self.customer_list[route[0][0]].t
        for i in range(len(route) - 1):
            total_energy = total_energy + self.lbda*(self.tilde_qo + total_demand)*self.tilde_d[route[i][0]][route[i+1][0]]/self.tilde_v
            total_demand = total_demand - route[i+1][1]
            total_energy = total_energy + self.lbda* total_demand * self.customer_list[route[i+1][0]].t

        total_energy = total_energy + self.lbda*(self.tilde_qo + total_demand)*self.tilde_d[route[-1][0]][0]/self.tilde_v 
        return total_energy
    
    def check_drone_energy_constraint(self, route):
        total_energy = self.cal_drone_route_energy(route)
        if total_energy <= self.E:
            return True
        else:
            return False
        

