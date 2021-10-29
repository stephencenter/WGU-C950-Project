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
        self.hash_table = [[] for _ in range(size)]
        
    def has_key(self, key):
        hashed_key = hash(key) % self.size
        bucket = self.hash_table[hashed_key]
        
        for kvp in enumerate(bucket):
            if kvp[0] == key:
                return True
                
        return False
        
    def insert_val(self, key, value):
        hashed_key = hash(key) % self.size
        self.hash_table[hashed_key].append((key, value))
        
    def get_val(self, key):
        hashed_key = hash(key) % self.size
        bucket = self.hash_table[hashed_key]
       
        for kvp in bucket:
            if kvp[0] == key:
                return kvp[1];
                
        raise KeyError(f"Key '{key}' not found in HashMap")
    
def get_distance(distance_map, point_a, point_b):
    val = distance_map.get_val(point_a)
    return val.get_val(point_b)
   
def verify_distances(distance_data, distance_map):
    for point_a in distance_data[0]:
        if point_a == '':
            continue
           
        for point_b in distance_data[0]:
            if point_b == '':
                continue
            
            val_1 = get_distance(distance_map, point_a, point_b)
            val_2 = get_distance(distance_map, point_b, point_a)
                
            if val_1 != val_2:
                raise ValueError(point_a, point_b)
    
def load_distance_data():
    distances_path = "distances.csv"

    with open(distances_path) as f:
        return [x for x in csv.reader(f)]

def create_distance_hashmap(distance_data):
    num_locations = len(distance_data[0]) - 1
    distance_map = HashMap(num_locations)
    
    for num, point_a in enumerate(distance_data[0]):
        if point_a == '':
            continue
            
        for row in distance_data:
            point_b = row[0]
            distance = row[num]
            
            if point_b == '' or distance == '':
                continue
            
            if not distance_map.has_key(point_a):
                distance_map.insert_val(point_a, HashMap(num_locations))
                
            
            distance_map.get_val(point_a).insert_val(point_b, distance)
            
            if not distance_map.has_key(point_b):
                distance_map.insert_val(point_b, HashMap(num_locations))
                
            distance_map.get_val(point_b).insert_val(point_a, distance)
    
    return distance_map
            
def main():
    distance_data = load_distance_data()
    distance_map = create_distance_hashmap(distance_data)
    verify_distances(distance_data, distance_map)
    
main()