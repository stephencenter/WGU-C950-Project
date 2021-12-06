# Stephen Center ID#001168251

import csv
import datetime
import math

# The HashMap class is used to store the package objects, as well as the
# distances between addresses
class HashMap:
    def __init__(self, initial_size):
        # An initial size for the HashMap is set so we don't have to
        # continually resize as we initially populate the map
        self.size = 2**math.ceil(math.log2(max(1, initial_size)))
        self.num_items = 0
        self.bucket_list = [[] for _ in range(self.size)]
        
    # This method returns true if it has a value for the provided key, false
    # otherwise
    # Big O: O(1) to O(n)
    def has_key(self, key):
        hashed_key = hash(key) % self.size
        bucket = self.bucket_list[hashed_key]
        
        for kvp in enumerate(bucket):
            if kvp[0] == key:
                return True
                
        return False
        
    # This method inserts a new key-value pair into the hashtable
    # Big O: O(1) to O(n), O(n^2) if resizing
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
    # Big O: O(1) to O(n)
    def get_val(self, key):
        hashed_key = hash(key) % self.size
        bucket = self.bucket_list[hashed_key]
       
        for kvp in bucket:
            if kvp[0] == key:
                return kvp[1];
                
        raise KeyError(f"Key '{key}' not found in HashMap")
        
    # This method deletes the key-value pair with the matching key
    # Big O: O(1) to O(n), O(n^2) if resizing
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
        self.carrier = None
        
    # This method reads the current delivery status ID (0, 1, or 2) and returns
    # a string explaining the status
    # Big O: O(1)
    def get_status(self):
        if self.delivery_status == 0:
            return "At the hub"
        
        if self.delivery_status == 1:
            return f"In transit on {self.carrier}"
            
        if self.delivery_status == 2:
            return f"Delivered at {float_to_time(self.delivery_time, 8)} by {self.carrier}"
            
    # This method converts this package's deadline to a float and returns it
    def get_deadline(self):
        if self.deadline == "EOD":
            return 24
            
        return time_to_float(self.deadline, "%I:%M %p")
   
# The Simulator class is used to simulate our trucks on their deliveries and
# record all the information
class Simulator:
    def __init__(self):
        pass
    
    # This method takes a list of delivery parameters including a list of packages,
    # a number of hours passed, and a departure time, and simulates a delivery
    # with those parameters. It then returns a SimulationResult object that
    # details the outcome of the simulation
    # Big O: O(n^2)
    def simulate_delivery(self, truck_name, package_map, distance_map, package_list, departure_time, hours_passed):
        # First we evaluate an efficient order to deliver the packages in
        pkg_route, distance_list = self.calculate_delivery_route(package_map, distance_map, package_list)
        route_length = sum(distance_list)
        
        # This is the speed of the truck in miles/hour
        speed = 18
        
        # If a departure time was provided, the calculate the distance the truck
        # was able to travel in the amount of time specified, as well as the
        # time their route ended
        if departure_time is not None:
            distance_traveled = max(0, min(route_length, speed*(hours_passed - departure_time)))
            time_ended = distance_traveled/speed + departure_time
            distance_traveled = distance_traveled
        
        # If a departure time was not provided, then the truck will not travel
        # anywhere, and we set its distance to 0
        else:
            distance_traveled = 0
            time_ended = 0
        
        # Evaluate the status of each package given the number of miles traveled
        total_delivered = 0
        for index, pkg_id in enumerate(pkg_route):
            the_package = package_map.get_val(pkg_id)
            
            # Calculate the number of miles necessary to have delivered this
            # package
            miles_necessary = sum(distance_list[:index + 1])
            
            # If distance_traveled == 0, then the package hasn't left the hub
            if distance_traveled == 0:
                the_package.delivery_status = 0
                
            # If distance_travled < miles_necessary, then the package is in 
            # transit
            elif distance_traveled < miles_necessary:
                the_package.delivery_status = 1
                the_package.carrier = truck_name
                
            # Otherwise, the package has been delivered
            else:
                the_package.delivery_status = 2
                the_package.delivery_time = miles_necessary/speed + departure_time 
                the_package.carrier = truck_name    
                total_delivered += 1
        
        # Gather all of the information into a SimulationResult object and 
        # return it
        return SimulationResult(truck_name, departure_time, hours_passed, time_ended, distance_traveled, route_length, len(package_list), total_delivered)
        
    # This method uses a greedy algorithm to determine a good order
    # to deliver a given list of packages in. At every step, it simply
    # choses the closest package to the current address, prioritizing packages
    # that have a delivery deadline
    # Big O: O(n^2)
    def calculate_delivery_route(self, package_map, distance_map, package_list):
        optimal_route = []
        distance_list = []
        
        # Loop until all packages have been placed into the route
        while len(optimal_route) != len(package_list):
            best_package = None
            best_distance = 10000
            best_deadline = 24
            
            for pkg_id in package_list:
                # Skip past packages that are already in the route
                if pkg_id in optimal_route:
                    continue
                    
                # Get the distance from the current point to this package
                if optimal_route:
                    distance = get_package_distance(package_map, distance_map, optimal_route[-1], pkg_id)
                else:
                    distance = get_distance_from_hub(package_map, distance_map, pkg_id)
                    
                # If the distance between the current point and this package are 0,
                # that means we can deliver it immediately with no issues
                if distance == 0:
                    best_package = pkg_id
                    best_distance = distance
                    break
                    
                # Find the current package's deadline
                deadline = package_map.get_val(pkg_id).get_deadline()
                
                # If this package's deadline is later than the current
                # closest_point's deadline, then we skip this package
                if deadline > best_deadline:
                    continue
                    
                # If this package's deadline is earlier than the current
                # closest_point's deadline, then we prioritze this package
                if deadline < best_deadline:
                    best_package = pkg_id
                    best_distance = distance
                    best_deadline = deadline
                    continue
                    
                # Prioritize packages that are closer to the most recent package
                if distance < best_distance:
                    best_package = pkg_id
                    best_distance = distance
                    best_deadline = deadline
                    
            optimal_route.append(best_package)
            distance_list.append(best_distance) 
        
        # Add the distance needed to travel from the final point back to the hub
        distance_list.append(get_distance_from_hub(package_map, distance_map, optimal_route[-1]))
        
        return optimal_route, distance_list
    
# This class represents the result of the Simulator.simulate_delivery() method.
# It details how the delivery went, including time spent, distance traveled, and
# number of packages delivered
class SimulationResult:
    def __init__(self, truck_name, departure_time, hours_passed, time_ended, distance_traveled, route_length, num_packages, total_delivered):
        self.truck_name = truck_name
        self.departure_time = departure_time
        self.hours_passed = hours_passed
        self.time_ended = time_ended
        self.distance_traveled = distance_traveled
        self.route_length = route_length
        self.num_packages = num_packages
        self.total_delivered = total_delivered
        
    # This method returns true if the total distance traveled was enough to 
    # complete the route, false otherwise
    def was_route_completed(self):
        return self.distance_traveled >= self.route_length
        
    # This method returns a string detailing the status of the truck at the
    # time the simulation finished
    def get_truck_status(self):
        if self.departure_time is None:
            return "Waiting for a truck to return"
            
        if self.hours_passed < self.departure_time:
            string_time = float_to_time(self.departure_time, 8)
            return f"Ready for departure at {string_time}"
            
        if self.was_route_completed():
            string_time = float_to_time(self.time_ended, 8)
            return f"Route completed at {string_time}"
            
        return "Route in progress"    
        
# This function takes a float and a number of hours to add on and returns a 
# string formatted in the standard HH:MMam/pm format.
# Example: 8.5, 2 -> 10:30am
# Big O: O(1)
def float_to_time(float_time, add_hours):
    hours = math.floor(float_time)
    minutes = min(math.ceil((float_time - hours)*60), 59)
    
    h24_string = datetime.datetime.strptime(f"{hours + add_hours}:{minutes}", "%H:%M")
    h12_string = h24_string.strftime("%I:%M%p")
    return h12_string
    
# This function takes a time string and a parse format and converts it to a
# float. Example: 10:30am, "%I:%M%p" -> 10.5
# Big O: O(1)
def time_to_float(string_time, parse_format):
    timestamp = datetime.datetime.strptime(string_time, parse_format)
    return timestamp.hour + timestamp.minute/60
    
# This function loads the distances.csv file as a list of lists so it can be
# used to the create the distance map
# Big O: O(n)  
def load_distance_data():
    distances_path = "distances.csv"

    with open(distances_path) as f:
        return [x for x in csv.reader(f)]

# This function loads the packages.csv file as a list of lists so it can be used
# to create the package map
# Big O: O(n)
def load_package_data():
    packages_path = "packages.csv"

    with open(packages_path) as f:
        return [x for x in csv.reader(f)][1:]
    
# This function reads the data pulled from the distances.csv file and uses it to
# create a table that can be used to quickly find the distance between any two addresses
# Big O: O(n^2)
def create_distance_hashmap(distance_data):
    map_size = len(distance_data[0])
    distance_map = HashMap(map_size)
    
    for address in distance_data[0]:
        if not address:
            continue
        
        distance_map.insert_val(address, HashMap(map_size))
    
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
           
# This function reads the data pulled from the packages.csv file and parses it
# into a hashmap of package objects
# Big O: O(n)
def create_package_hashmap(package_data):
    map_size = len(package_data)
    package_map = HashMap(map_size)
    
    for values in package_data:
        key = int(values[0])
        new_package = Package(key, values[1], values[2], values[3], values[4], values[5], values[6])
        package_map.insert_val(key, new_package)
        
    return package_map
    

# This function returns the distance in miles between two addresses
# Big O: O(1) to O(n)
def get_address_distance(distance_map, point_a, point_b):
    val = distance_map.get_val(point_a)
    return val.get_val(point_b)
   
# This function retrieves the destination addresses for two packages and 
# feeds them into get_address_distance() to calculate and return the distance
# between them
# Big O: O(1) to O(n)
def get_package_distance(package_map, distance_map, pkg_1, pkg_2):
    address_1 = package_map.get_val(pkg_1).address
    address_2 = package_map.get_val(pkg_2).address
    return get_address_distance(distance_map, address_1, address_2)

# This function returns the distance that a given package's destination is
# from the hub
# Big O: O(1) to O(n)
def get_distance_from_hub(package_map, distance_map, pkg):
    address = package_map.get_val(pkg).address
    return get_address_distance(distance_map, "HUB", address)
    
# This function runs the delivery simulation for all the trucks and records
# the results in a SimulationResult object, which it then returns
# Big O: O(n^2) 
def run_simulation(package_map, distance_map, hours_passed):
    simulator = Simulator()
    
    # These are our three batches of packages. They have been divided into
    # these three groups to ensure that all packages get delivered in an
    # efficient manner. The order of the packages in these lists does NOT
    # matter - the route taken by the trucks is determined by an algorithm
    # and is independent of the ordering of the list
    packages_a = [1, 8, 12, 13, 14, 15, 16, 19, 20, 21, 29, 30, 31, 34, 40]
    packages_b = [3, 4, 6, 11, 17, 18, 22, 23, 24, 25, 26, 32, 36, 37, 38]
    packages_c = [2, 5, 7, 9, 10, 27, 28, 33, 35, 39]
    
    # Run the simulation for Truck A carrying package list A.
    # None of the packages in group A are delayed, so Truck A will leave
    # immediately
    results_a = simulator.simulate_delivery("Truck A", package_map, distance_map, packages_a, 0, hours_passed)
    
    # Run the simulation for Truck B carrying package list B.
    # Package group B has many packages that are delayed until 9:05am, so we
    # hold Truck B until then so it can carry all its packages
    results_b = simulator.simulate_delivery("Truck B", package_map, distance_map, packages_b, 1 + 5/60, hours_passed)
    
    # We only have two drivers, so package group C will be picked up by the first
    # truck that returns from its deliveries
    c_departure_time = None
    c_truck_name = "No truck"
    
    # One of the packages in group C doesn't arrive until 10:20am, so that is
    # the earliest we can send them off
    c_earliest_time = 2 + 1/3
    
    # Set the departure time equal to the completion time of the first truck
    # to return
    if results_a.was_route_completed() or results_b.was_route_completed():
        c_departure_time = max(c_earliest_time, min(results_a.time_ended, results_b.time_ended))
        if results_a.time_ended < results_b.time_ended:
            c_truck_name = "Truck A-2"
            
        else:
            c_truck_name = "Truck B-2"
        
    # Run the simulation for Truck A or B carrying package list C
    results_c = simulator.simulate_delivery(c_truck_name, package_map, distance_map, packages_c, c_departure_time, hours_passed)
    
    return [results_a, results_b, results_c]
    
# This function asks the user what time they want to run the simulation at
# and what package (if any) they want to see the status of
def get_simulation_input():
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
                
            # Convert the chosen time to a datetime object so we can extract
            # the number of hours and minutes later
            try:
                chosen_time = time_to_float(chosen_time, "%I:%M%p")
                chosen_time = max(chosen_time - 8, 0)
                
            except ValueError:
                print("Please ensure your time is in the format 'hh:mmAM' or 'hh:mmPM'")
                continue
            
            # Parse the package id from the inputted string
            try:
                chosen_pkg = chosen[1]
                chosen_pkg = int(chosen_pkg)
                
                if chosen_pkg not in range(1, 41):
                    raise ValueError
                
            # If the user didn't provide a package id then we will display
            # all of the packages later
            except IndexError:
                chosen_pkg = None
                
            # A value error will be raised if the provided id isn't an integer
            # in the range 1 to 40
            except ValueError:
                print("Please ensure package# is a number between 1 and 40")
                continue
            
            # Return the user input
            return chosen_time, chosen_pkg

# This function displays the results of the simulation to the user
# Big O: O(n)
def print_simulation_results(package_map, hours_passed, chosen_pkg, simulation_list):
    # Get the totals for all the simulation results
    num_pkgs_delivered = sum([result.total_delivered for result in simulation_list])
    num_pkgs_total = sum([result.num_packages for result in simulation_list])
    num_miles_traveled = round(sum([result.distance_traveled for result in simulation_list]), 1)
    num_miles_required = round(sum([result.route_length for result in simulation_list]), 1)
    num_hours_spent = round(max([result.time_ended for result in simulation_list]), 2)
    
    # Print an overview of the simulations
    print(f"Overview at {float_to_time(hours_passed, 8)}: {num_pkgs_delivered} out of {num_pkgs_total} packages delivered, {num_miles_traveled} out of {num_miles_required} miles traveled")
    
    # Print the results for each individual simulation
    for res in simulation_list:
        name = res.truck_name
        traveled = round(res.distance_traveled, 2)
        r_length = round(res.route_length, 2)
        pkg_done = res.total_delivered
        pkg_total = res.num_packages
        status = res.get_truck_status()
        print(f"{name}: {pkg_done} out of {pkg_total} packages, {traveled} out of {r_length} miles, {status}")
        
    # If the user specified a package to view then we only display that package's status
    if chosen_pkg is not None:
        the_package = package_map.get_val(chosen_pkg)
        print(f"Package #{chosen_pkg}: {the_package.get_status()}")
        
    # If the user didn't specify a package, then we print all package statuses
    else:
        for pkg_id in [x for x in range(1, 41)]:
            the_package = package_map.get_val(pkg_id)
            print(f"Package #{pkg_id}: {the_package.get_status()}")
    
# This function is our main function. It creates our distance and package
# maps, and then it runs our main loop
def main():
    distance_data = load_distance_data()
    distance_map = create_distance_hashmap(distance_data)
    
    package_data = load_package_data()
    package_map = create_package_hashmap(package_data)
    
    # This is the main program loop. The program will continually ask the
    # user to enter a time and package id, then it will run a simulation. 
    # Finally, it will print the results of the simulation and restart the loop
    while True:
        hours_passed, chosen_pkg = get_simulation_input()
        print("-"*25)
        results = run_simulation(package_map, distance_map, hours_passed)
        print_simulation_results(package_map, hours_passed, chosen_pkg, results)
        print("-"*25)
        
if __name__ == "__main__":
    main()