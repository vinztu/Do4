import copy
from helper import *

def next_to_left_function(roadnet_data, int_types, left_IN_lane, right_IN_lane, bottom_IN_lane, top_IN_lane, intersection_index_roadnet, intersection_id, intersection):
    
    # Add another lane
    for roadLink_index, roadLink in enumerate(intersection["roadLinks"]):

        # add another lane starting from left or right
        if roadLink["startRoad"] in [left_IN_lane, right_IN_lane]:
            for laneLink_index, laneLink in enumerate(roadLink["laneLinks"]):

                # add the Connection from the old straight lane to the new lane on the other side (avenue -> avenue)
                if roadLink["startRoad"] != left_IN_lane and laneLink["startLaneIndex"] == 1 and laneLink["endLaneIndex"] == 3:
                    copy_laneLink = copy.deepcopy(laneLink)
                    shift_points(int_types, intersection_id, copy_laneLink)
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)

                # add all Connections from the new lane (avenue -> avenue)
                if laneLink["startLaneIndex"] == 2:
                    if roadLink["startRoad"] == left_IN_lane and laneLink["endLaneIndex"] > 1:
                        continue
                          
                    copy_laneLink = copy.deepcopy(laneLink)
                    shift_points(int_types, intersection_id, copy_laneLink)
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)

                    
                # change the right turn (index and points) of the original file (avenue -> street)
                if laneLink["startLaneIndex"] == 3 and laneLink["endLaneIndex"] <= 2:

                    copy_laneLink = copy.deepcopy(laneLink)
                    shift_points(int_types, intersection_id, copy_laneLink)
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][roadLink_index]["laneLinks"].pop(laneLink_index)
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)


        # add another lane starting from bottom or top
        if roadLink["startRoad"] in [bottom_IN_lane, top_IN_lane]:
            for laneLink_index, laneLink in enumerate(roadLink["laneLinks"]):
                # = 3 --> right turn (street -> avenue)
                if laneLink["startLaneIndex"] == 3 and laneLink["endLaneIndex"] == 3 and roadLink["startRoad"] == top_IN_lane:
                    copy_laneLink = copy.deepcopy(laneLink)
                    shift_points(int_types, intersection_id, copy_laneLink)
                    # change the startLaneIndex
                    copy_laneLink["startLaneIndex"] = 2

                    # change the points
                    points_x = roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][roadLink_index]["laneLinks"][0]["points"]
                    points_y = copy_laneLink["points"]

                    copy_laneLink["points"] = mix_points(points_x, points_y)
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)

                # = 0 --> left turn (street -> avenue)
                if laneLink["startLaneIndex"] == 0 and laneLink["endLaneIndex"] == 3 and roadLink["startRoad"] == bottom_IN_lane:
                    copy_laneLink = copy.deepcopy(laneLink)
                    shift_points(int_types, intersection_id, copy_laneLink)
                    roadnet_data["intersections"][intersection_index_roadnet]["roadLinks"][roadLink_index]["laneLinks"].insert(laneLink_index, copy_laneLink)