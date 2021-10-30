import csv

class Package:
    def __init__(self, pkg_id, address, city, state, zipcode, deadline, mass):
        self.package_id = pkg_id
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.deadline = deadline
        self.mass = mass
        self.delivery_status = "at the hub"
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
    
def load_trucks(package_map, distance_map):
    truck_a = [1, 8, 12, 13, 14, 15, 16, 19, 20, 21, 29, 30, 31, 34, 40] # leaves immediately
    truck_b = [3, 4, 5, 6, 11, 17, 18, 22, 23, 24, 25, 26, 32, 36, 37, 38] # delayed to 905
    truck_c = [2, 7, 9, 10, 19, 27, 28, 33, 39] # truck will be taken by whoever returns first
    
    path_a, distances_a = greedy_algorithm(package_map, distance_map, truck_a)
    path_b, distances_b = greedy_algorithm(package_map, distance_map, truck_b)
    path_c, distances_c = greedy_algorithm(package_map, distance_map, truck_c)
    
def greedy_algorithm(package_map, distance_map, package_list):
    path_taken = []
    distances = []
    
    while len(path_taken) != len(package_list):
        closest_point = None
        closest_distance = 10000
        
        for pkg_id in [x for x in package_list if x not in path_taken]:
            if path_taken:
                val = path_taken[-1]
            else:
                val = "HUB"
            
            address = package_map.get_val(pkg_id).address
            
            if path_taken:
                distance = get_package_distance(package_map, distance_map, path_taken[-1], pkg_id)
            else:
                distance = get_distance_from_hub(package_map, distance_map, pkg_id)
            
            if distance == 0:
                closest_distance = distance
                closest_point = pkg_id
                break
            
            delivered_by_900 = [15]
            delivered_by_1030 = [1, 6, 13, 14, 16, 20, 25, 29, 30, 31, 34, 37, 40]
            
            if closest_point in delivered_by_900 and pkg_id not in delivered_by_900:
                continue
                
            if closest_point in delivered_by_1030 and pkg_id not in (delivered_by_1030 + delivered_by_900):
                continue
            
            if pkg_id in delivered_by_900 and closest_point not in delivered_by_900:
                closest_distance = distance
                closest_point = pkg_id
                
                continue
                
            if pkg_id in delivered_by_1030 and closest_point not in (delivered_by_1030 + delivered_by_900):
                closest_distance = distance
                closest_point = pkg_id
                
                continue
            
            if distance < closest_distance:                    
                closest_distance = distance
                closest_point = pkg_id
                
        path_taken.append(closest_point)
        distances.append(closest_distance)
    
    distances.append(get_distance_from_hub(package_map, distance_map, path_taken[-1]))
    
    return path_taken, distances
    
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
    
def main():
    distance_data = load_distance_data()
    distance_map = create_distance_hashmap(distance_data)
    
    package_data = load_package_data()
    package_map = create_package_hashmap(package_data)
    
    load_trucks(package_map, distance_map)
    
main()