import copy
from helper import *

def top_or_bottom_function(roadnet_data, int_types, left_IN_lane, right_IN_lane, top_IN_lane, bottom_IN_lane, top_intersections, intersection_index_roadnet, intersection_id, intersection):
    
    top_or_bottom = "top" if intersection_id in top_intersections else "bottom"
                        
    # Add another lane
    for roadLink_index, roadLink in enumerate(intersection["roadLinks"]):

        # add another lane starting from left or right
        if roadLink["startRoad"] in [left_IN_lane, right_IN_lane]:
            for laneLink_index, laneLink in enumerate(roadLink["laneLinks"]):
                
                # add the Connection from the old straight lane to the new lane on the other side (avenue -> avenue)
                if (intersection_id in {"intersection_11_6", "intersection_11_9", "intersection_18_6"} and roadLink["startRoad"] == right_IN_lane and laneLink["startLaneIndex"] == 1 and laneLink["endLaneIndex"] == 3) \
                    or (intersection_id in {"intersection_29_6", "intersection_29_9", "intersection_15_9"} and roadLink["startRoad"] == left_IN_lane and laneLink["startLaneIndex"] == 1 and laneLink["endLaneIndex"] == 3):
                    copy_laneLink = copy.deepcopy(laneLink)
                    shift_points(int_types, intersection_id, copy_laneLink)
                    
                    if (top_or_bottom == "top" and roadLink["startRoad"] == right_IN_lane) or (top_or_bottom == "bottom" and roadLink["startRoad"] == left_IN_lane):
                        copy_laneLink["startLaneIndex"] = 0
                        
                    new_roadLink_index = find_roadLink_index(roadnet_data, intersection_index_roadnet, roadLink["startRoad"], roadLink["endRoad"])
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)
                    
                # add the Connection from the old straight lane to the new lane on the other side (avenue -> avenue)
                elif laneLink["startLaneIndex"] == 1 and laneLink["endLaneIndex"] == 2:
                    if intersection_id in {"intersection_11_9", "intersection_11_6", "intersection_18_6"} and roadLink["startRoad"] == right_IN_lane:
                        continue
                    
                    if intersection_id in {"intersection_29_6", "intersection_29_9", "intersection_15_9"} and roadLink["startRoad"] == left_IN_lane:
                        continue
                    
                    copy_laneLink = copy.deepcopy(laneLink)
                    
                    if (top_or_bottom == "top" and roadLink["startRoad"] == right_IN_lane) or (top_or_bottom == "bottom" and roadLink["startRoad"] == left_IN_lane):
                        copy_laneLink["startLaneIndex"] = 0
                        
                    shift_points(int_types, intersection_id, copy_laneLink)
                    new_roadLink_index = find_roadLink_index(roadnet_data, intersection_index_roadnet, roadLink["startRoad"], roadLink["endRoad"])
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)

                ################
             
                # add all Connections from the new lane (avenue -> avenue)
                if laneLink["startLaneIndex"] == 2 and laneLink["endLaneIndex"] <= 2:
                    copy_laneLink = copy.deepcopy(laneLink)
                    
                    if (top_or_bottom == "top" and roadLink["startRoad"] == right_IN_lane) or (top_or_bottom == "bottom" and roadLink["startRoad"] == left_IN_lane):
                        copy_laneLink["startLaneIndex"] = 1
                        
                    shift_points(int_types, intersection_id, copy_laneLink)
                    new_roadLink_index = find_roadLink_index(roadnet_data, intersection_index_roadnet, roadLink["startRoad"], roadLink["endRoad"])
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)
                    
                
                if intersection_id in {"intersection_11_6", "intersection_11_9", "intersection_18_6"} and roadLink["startRoad"] == right_IN_lane and laneLink["startLaneIndex"] == 2 and laneLink["endLaneIndex"] == 3:
                    copy_laneLink = copy.deepcopy(laneLink)
                    shift_points(int_types, intersection_id, copy_laneLink)
                    
                    if (top_or_bottom == "top" and roadLink["startRoad"] == right_IN_lane) or (top_or_bottom == "bottom" and roadLink["startRoad"] == left_IN_lane):
                        copy_laneLink["startLaneIndex"] = 1
                        
                    new_roadLink_index = find_roadLink_index(roadnet_data, intersection_index_roadnet, roadLink["startRoad"], roadLink["endRoad"])
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)
                    
                if intersection_id in {"intersection_29_6", "intersection_29_9", "intersection_15_9"} and roadLink["startRoad"] == left_IN_lane and laneLink["startLaneIndex"] == 2 and laneLink["endLaneIndex"] == 3:
                    copy_laneLink = copy.deepcopy(laneLink)
                    shift_points(int_types, intersection_id, copy_laneLink)
                    
                    if (top_or_bottom == "top" and roadLink["startRoad"] == right_IN_lane) or (top_or_bottom == "bottom" and roadLink["startRoad"] == left_IN_lane):
                        copy_laneLink["startLaneIndex"] = 1
                        
                    new_roadLink_index = find_roadLink_index(roadnet_data, intersection_index_roadnet, roadLink["startRoad"], roadLink["endRoad"])
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)
                    
                ################

                # (TOP) change the right turn (index and points) of the original file (avenue -> street)
                if top_or_bottom == "top" and laneLink["startLaneIndex"] == 3 and laneLink["endLaneIndex"] <= 2 and roadLink["startRoad"] == right_IN_lane:
                    copy_laneLink = copy.deepcopy(laneLink)
                    shift_points(int_types, intersection_id, copy_laneLink)
                    copy_laneLink["startLaneIndex"] = 2
                    new_roadLink_index = find_roadLink_index(roadnet_data, intersection_index_roadnet, roadLink["startRoad"], roadLink["endRoad"])
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].pop(laneLink_index)
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)
                
                # (BOTTOM) change the right turn (index and points) of the original file (avenue -> street)
                if top_or_bottom == "bottom" and laneLink["startLaneIndex"] == 3 and laneLink["endLaneIndex"] <= 2 and roadLink["startRoad"] == left_IN_lane:
                    copy_laneLink = copy.deepcopy(laneLink)
                    shift_points(int_types, intersection_id, copy_laneLink)
                    copy_laneLink["startLaneIndex"] = 2
                    new_roadLink_index = find_roadLink_index(roadnet_data, intersection_index_roadnet, roadLink["startRoad"], roadLink["endRoad"])
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].pop(laneLink_index)
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)

        # add another lane starting from bottom or top
        if (roadLink["startRoad"] == top_IN_lane and top_or_bottom == "top") or (roadLink["startRoad"] == bottom_IN_lane and top_or_bottom == "bottom"):
            for laneLink_index, laneLink in enumerate(roadLink["laneLinks"]):
                # = 3 --> right turn (street -> avenue)
                if (laneLink["startLaneIndex"] == 3 and laneLink["endLaneIndex"] == 2 and intersection_id not in {"intersection_11_9", "intersection_29_6"}) \
                    or (intersection_id in {"intersection_11_9", "intersection_29_6"} and laneLink["startLaneIndex"] == 3 and laneLink["endLaneIndex"] == 3):
                    
                    
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
                if (laneLink["startLaneIndex"] == 0 and laneLink["endLaneIndex"] == 2 and intersection_id not in {"intersection_11_6", "intersection_29_9", "intersection_15_9", "intersection_18_6"}) \
                    or (intersection_id in {"intersection_11_6", "intersection_29_9", "intersection_15_9", "intersection_18_6"} and laneLink["startLaneIndex"] == 0 and laneLink["endLaneIndex"] == 3):
                    
                        
                    copy_laneLink = copy.deepcopy(laneLink)
                    shift_points(int_types, intersection_id, copy_laneLink)
                    
                    new_roadLink_index = find_roadLink_index(roadnet_data, intersection_index_roadnet, roadLink["startRoad"], roadLink["endRoad"])
                    
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)