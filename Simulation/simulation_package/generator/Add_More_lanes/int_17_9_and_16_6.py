import copy
from helper import *

def intersection_17_9_and_16_6_function(roadnet_data, int_types, left_IN_lane, right_IN_lane, bottom_IN_lane, top_IN_lane, intersection_index_roadnet, intersection_id, intersection):
    
    # Add another lane
    for roadLink_index, roadLink in enumerate(intersection["roadLinks"]):
        
        # Update Points
        if intersection_id == "intersection_17_9" and roadLink["startRoad"] == bottom_IN_lane:
            for laneLink_index, laneLink in enumerate(roadLink["laneLinks"]):
                
                if laneLink["startLaneIndex"] in {0, 1, 3} and laneLink["endLaneIndex"] <= 2:
                    
                    if laneLink["startLaneIndex"] == 3 and laneLink["endLaneIndex"] >= 2:
                        continue
                    
                    if laneLink["startLaneIndex"] == 0 and laneLink["endLaneIndex"] >= 3:
                        continue
                        
                    copy_laneLink = copy.deepcopy(laneLink)
                    startRoad = "road_17_6_1"
                            
                    new_roadLink_index = find_roadLink_index(roadnet_data, intersection_index_roadnet, startRoad, roadLink["endRoad"])
                    
                    if laneLink_index < len(roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"]):
                        roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].pop(laneLink_index)
                        
                    if laneLink["startLaneIndex"] == 3:
                        copy_laneLink["startLaneIndex"] = 2
                        
                    shift_points(int_types, intersection_id, copy_laneLink)
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)
           
        # Update Points
        if intersection_id == "intersection_16_6" and roadLink["startRoad"] == top_IN_lane:
            for laneLink_index, laneLink in enumerate(roadLink["laneLinks"]):
                if laneLink["startLaneIndex"] in {0,1,3} and laneLink["endLaneIndex"] <= 2:
                    
                    if laneLink["startLaneIndex"] == 3 and laneLink["endLaneIndex"] >= 2:
                        continue
                    
                    if laneLink["startLaneIndex"] == 0 and laneLink["endLaneIndex"] >= 3:
                        continue
                        
                    copy_laneLink = copy.deepcopy(laneLink)
                    startRoad = "road_16_9_3"

                    new_roadLink_index = find_roadLink_index(roadnet_data, intersection_index_roadnet, startRoad, roadLink["endRoad"])
                    
                    if laneLink_index < len(roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"]):
                        roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].pop(laneLink_index)
                        
                    if laneLink["startLaneIndex"] == 3:
                        copy_laneLink["startLaneIndex"] = 2
                        
                    shift_points(int_types, intersection_id, copy_laneLink)
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)
        

        ###############################
        
        # add another lane starting from left or right
        if roadLink["startRoad"] in [left_IN_lane, right_IN_lane]:
            for laneLink_index, laneLink in enumerate(roadLink["laneLinks"]):

                # add the Connection from the old straight lane to the new lane on the other side (avenue -> avenue)
                if intersection_id == "intersection_17_9" and laneLink["startLaneIndex"] == 1:
                    if (roadLink["startRoad"] == left_IN_lane and laneLink["endLaneIndex"] == 2) or (roadLink["startRoad"] == right_IN_lane and laneLink["endLaneIndex"] == 3):
                        copy_laneLink = copy.deepcopy(laneLink)
                        
                        if roadLink["startRoad"] == right_IN_lane:
                            copy_laneLink["startLaneIndex"] = 0
                        
                        shift_points(int_types, intersection_id, copy_laneLink)
                        new_roadLink_index = find_roadLink_index(roadnet_data, intersection_index_roadnet, roadLink["startRoad"], roadLink["endRoad"])
                        roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)
                        
                if intersection_id == "intersection_16_6" and laneLink["startLaneIndex"] == 1:
                    if (roadLink["startRoad"] == left_IN_lane and laneLink["endLaneIndex"] == 3) or (roadLink["startRoad"] == right_IN_lane and laneLink["endLaneIndex"] == 2):
                        copy_laneLink = copy.deepcopy(laneLink)
                        
                        if roadLink["startRoad"] == left_IN_lane:
                            copy_laneLink["startLaneIndex"] = 0
                        
                        shift_points(int_types, intersection_id, copy_laneLink)
                        new_roadLink_index = find_roadLink_index(roadnet_data, intersection_index_roadnet, roadLink["startRoad"], roadLink["endRoad"])
                        roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)

                        
                #############

                # add all Connections from the new lane (avenue -> avenue)
                if laneLink["startLaneIndex"] == 2 and intersection_id == "intersection_17_9":
                    if (roadLink["startRoad"] == left_IN_lane and laneLink["endLaneIndex"] <= 2) or (roadLink["startRoad"] == right_IN_lane and laneLink["endLaneIndex"] <= 3):
                        copy_laneLink = copy.deepcopy(laneLink)
                        
                        if roadLink["startRoad"] == right_IN_lane:
                            copy_laneLink["startLaneIndex"] = 1
                            
                        shift_points(int_types, intersection_id, copy_laneLink)
                        new_roadLink_index = find_roadLink_index(roadnet_data, intersection_index_roadnet, roadLink["startRoad"], roadLink["endRoad"])
                        roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)
                        
                # add all Connections from the new lane (avenue -> avenue)
                if laneLink["startLaneIndex"] == 2 and intersection_id == "intersection_16_6":
                    if (roadLink["startRoad"] == left_IN_lane and laneLink["endLaneIndex"] <= 3) or (roadLink["startRoad"] == right_IN_lane and laneLink["endLaneIndex"] <= 2):
                        copy_laneLink = copy.deepcopy(laneLink)
                        
                        if roadLink["startRoad"] == left_IN_lane:
                            copy_laneLink["startLaneIndex"] = 1
                            
                        shift_points(int_types, intersection_id, copy_laneLink)
                        new_roadLink_index = find_roadLink_index(roadnet_data, intersection_index_roadnet, roadLink["startRoad"], roadLink["endRoad"])
                        roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)

                #############
                
                # change the right turn (index and points) of the original file (avenue -> street)
                if laneLink["startLaneIndex"] == 3 and laneLink["endLaneIndex"] <= 2:
                    if intersection_id == "intersection_17_9" and roadLink["startRoad"] == left_IN_lane:
                        continue
                    
                    if intersection_id == "intersection_16_6" and roadLink["startRoad"] == right_IN_lane:
                        continue

                    copy_laneLink = copy.deepcopy(laneLink)
                    
                    copy_laneLink["startLaneIndex"] = 2
                    shift_points(int_types, intersection_id, copy_laneLink)
                    
                    new_roadLink_index = find_roadLink_index(roadnet_data, intersection_index_roadnet, roadLink["startRoad"], roadLink["endRoad"])
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].pop(laneLink_index)
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)


        # add another lane starting from bottom or top
        if roadLink["startRoad"] in [bottom_IN_lane, top_IN_lane]:
            for laneLink_index, laneLink in enumerate(roadLink["laneLinks"]):
                # = 3 --> right turn (street -> avenue)
                if laneLink["startLaneIndex"] == 3:
                    if intersection_id == "intersection_17_9":
                        if (roadLink["startRoad"] == bottom_IN_lane and laneLink["endLaneIndex"] == 2) or (roadLink["startRoad"] == top_IN_lane and laneLink["endLaneIndex"] == 3):
                            copy_laneLink = copy.deepcopy(laneLink)
                            shift_points(int_types, intersection_id, copy_laneLink)

                            # change the startLaneIndex
                            if roadLink["startRoad"] == top_IN_lane:
                                copy_laneLink["startLaneIndex"] = 1
                            if roadLink["startRoad"] == bottom_IN_lane:
                                copy_laneLink["startLaneIndex"] = 2

                                    
                            if roadLink["startRoad"] == bottom_IN_lane:
                                startRoad = "road_17_6_1"
                            else:
                                startRoad = roadLink["startRoad"]
                                
                            new_roadLink_index = find_roadLink_index(roadnet_data, intersection_index_roadnet, startRoad, roadLink["endRoad"])

                            # change the points
                            points_x = roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"][0]["points"]
                            points_y = copy_laneLink["points"]

                            copy_laneLink["points"] = mix_points(points_x, points_y)
                            roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)
                            
                    if intersection_id == "intersection_16_6":
                        if (roadLink["startRoad"] == bottom_IN_lane and laneLink["endLaneIndex"] == 3) or (roadLink["startRoad"] == top_IN_lane and laneLink["endLaneIndex"] == 2):
                            copy_laneLink = copy.deepcopy(laneLink)
                            shift_points(int_types, intersection_id, copy_laneLink)

                            # change the startLaneIndex
                            if roadLink["startRoad"] == top_IN_lane:
                                copy_laneLink["startLaneIndex"] = 2
                            if roadLink["startRoad"] == bottom_IN_lane:
                                copy_laneLink["startLaneIndex"] = 1
                                    
                            
                            if roadLink["startRoad"] == top_IN_lane:
                                startRoad = "road_16_9_3"
                            else:
                                startRoad = roadLink["startRoad"]
                                
                            new_roadLink_index = find_roadLink_index(roadnet_data, intersection_index_roadnet, startRoad, roadLink["endRoad"])

                            # change the points
                            points_x = roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"][0]["points"]
                            points_y = copy_laneLink["points"]
                            copy_laneLink["points"] = mix_points(points_x, points_y)

                            roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)

                # = 0 --> left turn (street -> avenue)
                if laneLink["startLaneIndex"] == 0:
                    if intersection_id == "intersection_17_9":
                        if (roadLink["startRoad"] == bottom_IN_lane and laneLink["endLaneIndex"] == 3) or (roadLink["startRoad"] == top_IN_lane and laneLink["endLaneIndex"] == 2):
                            copy_laneLink = copy.deepcopy(laneLink)
                            shift_points(int_types, intersection_id, copy_laneLink)
                            
                            if roadLink["startRoad"] == bottom_IN_lane:
                                startRoad = "road_17_6_1"
                            else:
                                startRoad = roadLink["startRoad"]
                                
                            new_roadLink_index = find_roadLink_index(roadnet_data, intersection_index_roadnet, startRoad, roadLink["endRoad"])
                            roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)
                        
                    if intersection_id == "intersection_16_6":
                        if (roadLink["startRoad"] == bottom_IN_lane and laneLink["endLaneIndex"] == 2) or (roadLink["startRoad"] == top_IN_lane and laneLink["endLaneIndex"] == 3):
                            copy_laneLink = copy.deepcopy(laneLink)
                            shift_points(int_types, intersection_id, copy_laneLink)
                            
                            if roadLink["startRoad"] == top_IN_lane:
                                startRoad = "road_16_9_3"
                            else:
                                startRoad = roadLink["startRoad"]
                                
                            new_roadLink_index = find_roadLink_index(roadnet_data, intersection_index_roadnet, startRoad, roadLink["endRoad"])
                            roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][new_roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)