import cityflow

def shift_points(int_types, intersection, laneLink):
    for point in laneLink["points"]:
        point["x"] += int_types[intersection]["x"]
        point["y"] += int_types[intersection]["y"]
        
        
def mix_points(points_x, points_y):
    new_points = []
    
    for point_x, point_y in zip(points_x, points_y):
        x_coordinate = point_x["x"]
        y_coordinate = point_y["y"]
        
        new_points.append({"x": x_coordinate, "y": y_coordinate})
    
    return new_points
    
        
def find_intersection_index(roadnet_data, intersection_id):
    for index, intersection in enumerate(roadnet_data["intersections"]):
        if intersection["id"] == intersection_id:
            return index
    
    raise ValueError(f"Index for Intersection {intersection_id} not found")
    
    
def find_roadLink_index(roadnet_data, intersection_index_roadnet, startRoad, endRoad):
    for new_index, new_roadLink in enumerate(roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"]):
        if new_roadLink["startRoad"] == startRoad and new_roadLink["endRoad"] == endRoad:
            return new_index
    
    raise ValueError(f'For {roadnet_data["intersections"][intersection_index_roadnet]["id"]}: Index for roadLink {startRoad} <--> {endRoad} not found')
        
        
def test(path, new_roadnet_file):
    
    engine = cityflow.Engine(path + "config.json", 1)
    engine.reset()
    
    for i in range(300):
        engine.next_step()