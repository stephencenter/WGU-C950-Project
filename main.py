# Stephen Center ID#001168251

import csv
import datetime
import math

# The Package class represents the packages being delivered on the trucks
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
        
    # This method reads the current delivery status ID (0, 1, or 2) and returns
    # a string explaining the status
    # Big O: O(1)
    def get_status(self):
        if self.delivery_status == 0:
            return "At the hub"
        
        if self.delivery_status == 1:
            return "En route"
            
        if self.delivery_status == 2:
            return f"Delivered at {float_time(self.delivery_time)}"
    
# The HashMap class is used to store the package objects, as well as the
# distances between addresses
class HashMap:
    def __init__(self):
        self.size = 1
        self.num_items = 0
        self.bucket_list = [[]]
        
    # This method returns true if it has a value for the provided key, false
    # otherwise
    # Big O: O(1)
    def has_key(self, key):
        hashed_key = hash(key) % self.size
        bucket = self.bucket_list[hashed_key]
        
        for kvp in enumerate(bucket):
            if kvp[0] == key:
                return True
                
        return False
        
    # This method inserts a new key-value pair into the hashtable
    # Big O: O(1), O(n^2) if resizing
    def insert_val(self, key, value):
        hashed_key = hash(key) % self.size
        
        # If the provided key already exists in the hashmap then we'll
        # overwrite its value with the new value
        for index, kvp in enumerate(self.bucket_list[hashed_key]):
            if kvp[0] == key:
                self.bucket_list[hashed_key][index] = (key, value)
                return
            
        self.num_items += 1
        
        if self.num_items > self.size:
            self.resize()
            hashed_key = hash(key) % self.size
        
        self.bucket_list[hashed_key].append((key, value))
        
    # This method returns the value corresponding to the provided key
    # Big O: O(1)
    def get_val(self, key):
        hashed_key = hash(key) % self.size
        bucket = self.bucket_list[hashed_key]
       
        for kvp in bucket:
            if kvp[0] == key:
                return kvp[1];
                
        raise KeyError(f"Key '{key}' not found in HashMap")
        
    # This method deletes the key-value pair with the matching key
    # Big O: O(1), O(n^2) if resizing
    def delete_val(self, key):
        if not self.has_key(key):
            raise KeyError(f"Key '{key}' not found in HashMap")
        
        hashed_key = hash(key) % self.size        
        bucket = self.bucket_list[hashed_key]
        self.bucket_list[hashed_key] = [kvp for kvp in bucket if kvp[0] != key]
            
        self.num_items -= 1
        if self.num_items < self.size/2:
            self.resize()
        
    # This method is called when it's necessary to resize the hash map.
    # It sets the number of buckets equal to the smallest power of 2 larger
    # than the number of items in the table
    # Big O: O(n^2)
    def resize(self):
        # Calculate the smallest power of 2 that is larger than the
        # number of items in hashmap (e.g. 16 for 13 items, 8 for 7 items etc)
        self.size = 2**math.ceil(math.log2(self.num_items))
        
        # Create a new list of buckets
        new_buckets = [[] for _ in range(self.size)]
        
        # Assign new hashes to each of the items in the old bucket list
        for bucket in self.bucket_list:
            for kvp in bucket:
                hashed_key = hash(kvp[0]) % self.size
                new_buckets[hashed_key].append(kvp)
                
        # Replace the old bucket list with the new resized one
        self.bucket_list = new_buckets

class Truck:
    def __init__(self, route, departure_time, num_hours):
        self.route = route
        self.departure_time = departure_time
        self.num_hours = num_hours
        self.speed = 18
        
    def run_simulation(self, package_map):
        route_length = sum(self.route.distance_list)
        
        if self.departure_time is not None:
            distance_traveled = max(0, min(route_length, self.speed*(self.num_hours - self.departure_time)))
            distance_traveled = round(distance_traveled, 1)
            time_ended = min(route_length/self.speed, self.num_hours)
        
        else:
            distance_traveled = 0
            time_ended = 0
        
        miles_necessary = 0
        for index, pkg_id in enumerate(self.route.package_order):
            miles_necessary += self.route.distance_list[index]
            the_package = package_map.get_val(pkg_id)
            
            if distance_traveled == 0:
                the_package.delivery_status = 0
                
            elif distance_traveled < miles_necessary:
                the_package.delivery_status = 1
                
            else:
                the_package.delivery_status = 2
                the_package.delivery_time = miles_necessary/self.speed + self.departure_time                
        
        if distance_traveled < route_length:
            was_route_completed = False
        else:
            was_route_completed = True
        
        total_delivered = 0
        for pkg_id in self.route.package_order:
            the_package = package_map.get_val(pkg_id)
            if the_package.delivery_status == 2:
                total_delivered += 1
        
        return SimulationResult(distance_traveled, time_ended, was_route_completed, total_delivered)
     
class DeliveryRoute:
    def __init__(self, package_order, distance_list):
        self.package_order = package_order
        self.distance_list = distance_list
     
class SimulationResult:
    def __init__(self, distance_traveled, time_ended, was_route_completed, total_delivered):
        self.distance_traveled = distance_traveled
        self.time_ended = time_ended
        self.was_route_completed = was_route_completed
        self.total_delivered = total_delivered
    
def float_time(float_time):
    # This method 
    hours = 8 + math.floor(float_time)
    minutes = int((float_time % 1)*60)
    
    h24_string = datetime.datetime.strptime(f"{hours}:{minutes}", "%H:%M")
    h12_string = h24_string.strftime("%I:%M%p")
    return h12_string
                    
def load_distance_data():
    distances_path = "distances.csv"

    with open(distances_path) as f:
        return [x for x in csv.reader(f)]

def load_package_data():
    packages_path = "packages.csv"

    with open(packages_path) as f:
        return [x for x in csv.reader(f)][1:]
    
def create_distance_hashmap(distance_data):
    distance_map = HashMap()
    
    for address in distance_data[0]:
        if not address:
            continue
        
        distance_map.insert_val(address, HashMap())
    
    for index, point_a in enumerate(distance_data[0]):
        if not point_a:
            continue
            
        for row in distance_data:
            point_b = row[0]
            
            if not point_b or not row[index]:
                continue
                
            distance = float(row[index])
            distance_map.get_val(point_a).insert_val(point_b, distance)                
            distance_map.get_val(point_b).insert_val(point_a, distance)
    
    return distance_map
            
def create_package_hashmap(package_data):
    package_map = HashMap()
    
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
    
def simulate_deliveries(package_map, distance_map, num_hours, chosen_pkg):
    packages_a = [1, 8, 12, 13, 14, 15, 16, 19, 20, 21, 29, 30, 31, 34, 40]
    packages_b = [3, 4, 6, 11, 17, 18, 22, 23, 24, 25, 26, 32, 36, 37, 38]
    packages_c = [2, 5, 7, 9, 10, 27, 28, 33, 35, 39]
    
    all_packages = sorted(packages_a + packages_b + packages_c)
    
    truck_a = Truck(greedy_algorithm(package_map, distance_map, packages_a), 0, num_hours)
    simulation_a = truck_a.run_simulation(package_map)
    
    truck_b = Truck(greedy_algorithm(package_map, distance_map, packages_b), 1 + 5/60, num_hours)
    simulation_b = truck_b.run_simulation(package_map)
    
    truck_c_departure_time = None
    if simulation_a.was_route_completed and simulation_b.was_route_completed:
        if simulation_a.time_ended < simulation_b.time_ended: 
            truck_c_departure_time = simulation_a.time_ended
        else:
            truck_c_departure_time = simulation_b.time_ended
    
    elif simulation_a.was_route_completed:
        truck_c_departure_time = simulation_a.time_ended
        
    elif simulation_b.was_route_completed:
        truck_c_departure_time = simulation_b.time_ended
        
    truck_c = Truck(greedy_algorithm(package_map, distance_map, packages_c), truck_c_departure_time, num_hours)
    simulation_c = truck_c.run_simulation(package_map)
    
    total_delivered = 0
    for truck in [simulation_a, simulation_b, simulation_c]:
        total_delivered += truck.total_delivered
        
    total_traveled = round(simulation_a.distance_traveled + simulation_b.distance_traveled + simulation_c.distance_traveled, 1)
    total_required = round(sum(truck_a.route.distance_list) + sum(truck_b.route.distance_list) + sum(truck_c.route.distance_list), 1)
    total_time = round(max(simulation_a.time_ended, simulation_b.time_ended, simulation_c.time_ended), 2)
    
    if chosen_pkg is not None:
        the_package = package_map.get_val(chosen_pkg)
        print(f"Package #{chosen_pkg}: {the_package.get_status()}")
        
    else:
        for pkg_id in all_packages:
            the_package = package_map.get_val(pkg_id)
            print(f"Package #{pkg_id}: {the_package.get_status()}")
            
    print(f"Overview at {float_time(num_hours)}: {total_delivered} out of {len(all_packages)} packages delivered, {total_traveled} out of {total_required} miles traveled")
    
def get_simulation_input():
    package_list = [x for x in range(1, 41)]
    while True:
        print("The day starts at 8:00AM, there are 40 packages")
        print("Leave package# blank to view all packages")
        
        while True:
            chosen = input("Enter a time and a package# to view information: ").lower().split()
            
            # Parse the chosen time from the inputted string
            try:
                chosen_time = chosen[0]
                
            except IndexError:
                print("Please provide a time to get information at")
                continue
                
            try:
                chosen_time = datetime.datetime.strptime(chosen_time, "%I:%M%p")
                
            except ValueError:
                print("Please ensure your time is in the format 'hh:mmAM' or 'hh:mmPM'")
                continue
            
            # Parse the package id from the inputted string
            try:
                chosen_pkg = chosen[1]
                chosen_pkg = int(chosen_pkg)
                
                if chosen_pkg not in package_list:
                    raise ValueError
                
            except IndexError:
                chosen_pkg = None
                
            except ValueError:
                print("Please ensure package# is a number between 1 and 40")
                continue
                
            hours_passed = chosen_time.hour + (chosen_time.minute/60) - 8
            
            return max(0, hours_passed), chosen_pkg

def main():
    distance_data = load_distance_data()
    distance_map = create_distance_hashmap(distance_data)
    
    package_data = load_package_data()
    package_map = create_package_hashmap(package_data)
    
    while True:
        hours_passed, chosen_pkg = get_simulation_input()
        simulate_deliveries(package_map, distance_map, hours_passed, chosen_pkg)
        print("-"*25)
    
main()