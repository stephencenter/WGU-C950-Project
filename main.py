# Stephen Center ID#001168251

import csv
import datetime

class Package:
    def __init__(self, pkg_id, address, city, state, zipcode, deadline, mass):
        self.package_id = pkg_id
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.deadline = deadline
        self.mass = mass
        self.delivery_status = 0
        self.delivery_time = None
    
class HashMap:
    def __init__(self, size):
        self.size = size
        self.bucket_list = [[] for _ in range(size)]
        
    def has_key(self, key):
        hashed_key = hash(key) % self.size
        bucket = self.bucket_list[hashed_key]
        
        for kvp in enumerate(bucket):
            if kvp[0] == key:
                return True
                
        return False
        
    def insert_val(self, key, value):
        hashed_key = hash(key) % self.size
        self.bucket_list[hashed_key].append((key, value))
        
    def get_val(self, key):
        hashed_key = hash(key) % self.size
        bucket = self.bucket_list[hashed_key]
       
        for kvp in bucket:
            if kvp[0] == key:
                return kvp[1];
                
        raise KeyError(f"Key '{key}' not found in HashMap")
   
class DeliveryRoute:
    def __init__(self, package_order, distance_list):
        self.package_order = package_order
        self.distance_list = distance_list
    
class Truck:
    def __init__(self, name, route):
        self.name = name
        self.route = route
        self.speed = 18
        self.departure_time = None
        self.distance_traveled = 0
        self.time_finished = 0
    
    def calculate_package_statuses(self, package_map):
        total_necessary = 0
        for index, pkg_id in enumerate(self.route.package_order):
            total_necessary += self.route.distance_list[index]
            the_package = package_map.get_val(pkg_id)
            
            if self.distance_traveled == 0:
                the_package.delivery_status = 0
                
            elif self.distance_traveled < total_necessary:
                the_package.delivery_status = 1
                
            else:
                the_package.delivery_status = 2
                the_package.delivery_time = total_necessary/self.speed
                
                print(f"Package #{the_package.package_id} delivered at {round(the_package.delivery_time, 1)} hours")
            
    def is_route_finished(self):
        return not (self.distance_traveled < sum(self.route.distance_list))
        
    def calculate_distance_traveled(self, hours_passed):
        if self.departure_time is None:
            return
            
        total_necessary = sum(self.route.distance_list)
        self.distance_traveled = max(0, min(total_necessary, self.speed*(hours_passed - self.departure_time)))
        self.distance_traveled = round(self.distance_traveled, 1)
    
    def calculate_time_finished(self):
        if self.departure_time is None:
            return
        self.time_finished = self.distance_traveled/self.speed + self.departure_time
        
    def get_total_delivered(self, package_map):
        total = 0
        for pkg_id in self.route.package_order:
            the_package = package_map.get_val(pkg_id)
            if the_package.delivery_status == 2:
                total += 1
        
        return total
        
    def print_status(self, package_map):
        total_delivered = self.get_total_delivered(package_map)
        total_packages = len(self.route.package_order)
        
        distance_required = round(sum(self.route.distance_list), 1)
        print(f"{self.name}: {self.distance_traveled} out of {distance_required} miles traveled, {total_delivered} out of {total_packages} packages delivered")
        
def load_distance_data():
    distances_path = "distances.csv"

    with open(distances_path) as f:
        return [x for x in csv.reader(f)]

def load_package_data():
    packages_path = "packages.csv"

    with open(packages_path) as f:
        return [x for x in csv.reader(f)][1:]
    
def create_distance_hashmap(distance_data):
    num_locations = len(distance_data[0]) - 1
    distance_map = HashMap(num_locations)
    
    for num, point_a in enumerate(distance_data[0]):
        if point_a == '':
            continue
            
        for row in distance_data:
            point_b = row[0]
            
            if point_b == '' or row[num] == '':
                continue
                
            distance = float(row[num])
            
            if not distance_map.has_key(point_a):
                distance_map.insert_val(point_a, HashMap(num_locations))
            
            distance_map.get_val(point_a).insert_val(point_b, distance)
            
            if not distance_map.has_key(point_b):
                distance_map.insert_val(point_b, HashMap(num_locations))
                
            distance_map.get_val(point_b).insert_val(point_a, distance)
    
    return distance_map
            
def create_package_hashmap(package_data):
    package_map = HashMap(len(package_data))
    
    for values in package_data:
        key = int(values[0])
        new_package = Package(key, values[1], values[2], values[3], values[4], values[5], values[6])
        package_map.insert_val(key, new_package)
        
    return package_map
    
def greedy_algorithm(package_map, distance_map, package_list):
    path_taken = []
    distances = []
    
    while len(path_taken) != len(package_list):
        closest_point = None
        closest_distance = 10000
        
        for pkg_id in [x for x in package_list if x not in path_taken]:
            # Get the distance from the current point to this package
            if path_taken:
                distance = get_package_distance(package_map, distance_map, path_taken[-1], pkg_id)
            else:
                distance = get_distance_from_hub(package_map, distance_map, pkg_id)
            
            # If the distance between the current point and this package are 0,
            # that means we can deliver it immediately with no issues
            if distance == 0:
                closest_distance = distance
                closest_point = pkg_id
                break
            
            # This is a list of packages that need to be delivered
            # by a specific deadline. They are prioritized over other packages            
            delivered_by_900 = [15]
            delivered_by_1030 = [1, 6, 13, 14, 16, 20, 25, 29, 30, 31, 34, 37, 40]
            
            # If the closest found package has a deadline, and this package 
            # doesn't, then we ignore it even if it's closer
            if closest_point in delivered_by_900 and pkg_id not in delivered_by_900:
                continue
                
            if closest_point in delivered_by_1030 and pkg_id not in (delivered_by_1030 + delivered_by_900):
                continue
            
            # If the closest found package doesn't have a deadline, and this one
            # does, then we give this package priority even if it's further away
            if pkg_id in delivered_by_900 and closest_point not in delivered_by_900:
                closest_distance = distance
                closest_point = pkg_id
                continue
                
            if pkg_id in delivered_by_1030 and closest_point not in (delivered_by_1030 + delivered_by_900):
                closest_distance = distance
                closest_point = pkg_id
                continue
            
            # If both packages have a deadline, or neither of them do, then we
            # choose the one that's closest
            if distance < closest_distance:                    
                closest_distance = distance
                closest_point = pkg_id
                
        path_taken.append(closest_point)
        distances.append(closest_distance)
    
    # Add the distance needed to travel from the final point back to the hub
    distances.append(get_distance_from_hub(package_map, distance_map, path_taken[-1]))
    
    return DeliveryRoute(path_taken, distances)
    
def get_address_distance(distance_map, point_a, point_b):
    val = distance_map.get_val(point_a)
    return val.get_val(point_b)
    
def get_package_distance(package_map, distance_map, pkg_1, pkg_2):
    address_1 = package_map.get_val(pkg_1).address
    address_2 = package_map.get_val(pkg_2).address
    return get_address_distance(distance_map, address_1, address_2)

def get_distance_from_hub(package_map, distance_map, pkg):
    address = package_map.get_val(pkg).address
    return get_address_distance(distance_map, "HUB", address)
    
def simulate_deliveries(package_map, distance_map, hours_passed):
    packages_a = [1, 8, 12, 13, 14, 15, 16, 19, 20, 21, 29, 30, 31, 34, 40]
    packages_b = [3, 4, 6, 11, 17, 18, 22, 23, 24, 25, 26, 32, 36, 37, 38]
    packages_c = [2, 5, 7, 9, 10, 19, 27, 28, 33, 39]
    
    truck_a = Truck("Truck A", greedy_algorithm(package_map, distance_map, packages_a))
    truck_b = Truck("Truck B", greedy_algorithm(package_map, distance_map, packages_b))
    truck_c = Truck("Truck C", greedy_algorithm(package_map, distance_map, packages_c))
    
    # Truck A leaves immediately, so its distance traveled is simply
    # the speed of the truck times how much time has passed
    truck_a.departure_time = 0
    truck_a.calculate_distance_traveled(hours_passed)
    truck_a.calculate_time_finished()
    
    # Truck B waits until 9:05am to leave so it can pick up the delayed 
    # packages. Its distance traveled is the speed of the truck multiplied by
    # time passed, minus how time spent waiting at the hub before leaving
    truck_b.departure_time = 1 + 5/60
    truck_b.calculate_distance_traveled(hours_passed)
    truck_b.calculate_time_finished()
        
    # Truck C doesn't leave until either Truck A or Truck B have returned, as
    # we only have two drivers. So Truck C isn't really a different truck,
    # it's simply the third batch of packages that will be picked up by either
    # truck A or truck B. This is also helpful because one of the packages on
    # truck C doesn't arrive until 10:20am, so it would need delayed anyway
    if truck_a.is_route_finished() and truck_b.is_route_finished():
        if truck_a.time_finished < truck_b.time_finished: 
            truck_c.departure_time = truck_a.time_finished
        else:
            truck_c.departure_time = truck_b.time_finished
    
    elif truck_a.is_route_finished():
        truck_c.departure_time = truck_a.time_finished
        
    elif truck_b.is_route_finished():
        truck_c.departure_time = truck_b.time_finished 
        
    truck_c.calculate_distance_traveled(hours_passed)
    truck_c.calculate_time_finished()
    
    truck_a.calculate_package_statuses(package_map)
    truck_b.calculate_package_statuses(package_map)
    truck_c.calculate_package_statuses(package_map)
    
    total_delivered = 0
    for truck in [truck_a, truck_b, truck_c]:
        truck.print_status(package_map)
        total_delivered += truck.get_total_delivered(package_map)
        
    total_packages = len(packages_a) + len(packages_b) + len(packages_c)
    total_traveled = truck_a.distance_traveled + truck_b.distance_traveled + truck_c.distance_traveled
    total_necessary = sum(truck_a.route.distance_list) + sum(truck_b.route.distance_list) + sum(truck_c.route.distance_list)
    total_time = max(truck_a.time_finished, truck_b.time_finished, truck_c.time_finished)
    
    print(f"{total_time} hours spent, {total_delivered} out of {total_packages} delivered, {total_traveled} out of {total_necessary} traveled")
    
def get_simulation_time():
    while True:
        print("The day starts at 8:00 AM")
        
        while True:
            chosen_time = input("Enter a time to calculate: ").lower().strip()
            
            try:
                chosen_time = datetime.datetime.strptime(chosen_time, "%I:%M %p")
                
            except ValueError:
                print("Please ensure your time is in the format 'hh:mm AM/PM'")
                continue
                
            hours_passed = chosen_time.hour + (chosen_time.minute/60) - 8
            
            return max(0, hours_passed)

def main():
    distance_data = load_distance_data()
    distance_map = create_distance_hashmap(distance_data)
    
    package_data = load_package_data()
    package_map = create_package_hashmap(package_data)
    
    while True:
        hours_passed = get_simulation_time()
        simulate_deliveries(package_map, distance_map, hours_passed)
    
main()