import copy
from helper import *

def left_function(roadnet_data, int_types, left_IN_lane, right_IN_lane, top_IN_lane, bottom_IN_lane, intersection_index_roadnet, intersection_id, intersection):
    
    # Add another lane
    for roadLink_index, roadLink in enumerate(intersection["roadLinks"]):

        # add another lane starting from bottom or top
        if roadLink["startRoad"] in [bottom_IN_lane, top_IN_lane]:
            for laneLink_index, laneLink in enumerate(roadLink["laneLinks"]):
                # = 3 --> right turn (street -> avenue)
                if laneLink["startLaneIndex"] == 3 and laneLink["endLaneIndex"] == 3 and roadLink["startRoad"] == top_IN_lane:
                    copy_laneLink = copy.deepcopy(laneLink)
                    shift_points(int_types, intersection_id, copy_laneLink)
                    # change the startLaneIndex
                    copy_laneLink["startLaneIndex"] = 1

                    new_roadLink_index = find_roadLink_index(roadnet_data, intersection_index_roadnet, roadLink["startRoad"], roadLink["endRoad"])
                    
                    # change the points
                    points_x = roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"][0]["points"]
                    points_y = copy_laneLink["points"]

                    copy_laneLink["points"] = mix_points(points_x, points_y)
                    
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)

                # = 0 --> left turn (street -> avenue)
                if laneLink["startLaneIndex"] == 0 and laneLink["endLaneIndex"] == 3 and roadLink["startRoad"] == bottom_IN_lane:
                    copy_laneLink = copy.deepcopy(laneLink)
                    shift_points(int_types, intersection_id, copy_laneLink)
                    new_roadLink_index = find_roadLink_index(roadnet_data, intersection_index_roadnet, roadLink["startRoad"], roadLink["endRoad"])
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)