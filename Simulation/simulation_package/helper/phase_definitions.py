def phase_definitions():
    # Predefined phases
    normal_intersection = {0: [0, 7, 2, 3, 6, 10],
                           1: [1, 8, 2, 3, 6, 10],
                           2: [4, 11, 2, 3, 6, 10],
                           3: [5, 9, 2, 3, 6, 10],
                           4: [0, 1, 2, 3, 6, 10],
                           5: [7, 8, 2, 3, 6, 10],
                           6: [9, 11, 2, 3, 6, 10],
                           7: [4, 5, 2, 3, 6, 10]
                          }


    top_intersection = {0: [0, 3, 2, 5],
                        1: [0, 1, 2, 5],
                        2: [5, 2, 4]
                       }

    bottom_intersection = {0: [0, 4, 1, 2],
                           1: [4, 5, 1, 2],
                           2: [3, 1, 2]
                          }


    left_intersection = {0: [2, 5, 1, 4],
                         1: [2, 3, 1, 4],
                         2: [0, 1, 4]
                        }

    intersection_16_9 = {0: [0, 4, 2, 3, 7], # l - r 
                         1: [1, 5, 2, 3, 7], # l_u, r_d
                         2: [6, 8, 2, 3, 7], # top ->
                         3: [0, 1, 2, 3, 7], # left ->
                         4: [4, 5, 2, 3, 7]  # right ->
                        }

    intersection_17_9 = {0: [0, 6, 2, 5, 8], # l - r
                         1: [4, 7, 2, 5, 8], # t_r, b_l
                         2: [0, 1, 2, 5, 8], # left ->
                         3: [3, 4, 2, 5, 8]  # bottom ->
                        }


    intersection_16_6 = {0: [0, 4, 1, 2, 7], # l - r
                         1: [3, 6, 1, 2, 7], # t_r, b_l
                         2: [4, 5, 1, 2, 7], # right ->
                         3: [6, 8, 1, 2, 7], # top ->
                        }

    intersection_17_6 = {0: [0, 7, 2, 3, 6], # l - r
                         1: [1, 8, 2, 3, 6], # l_u, r_d
                         2: [4, 5, 2, 3, 6], # bottom
                         3: [0, 1, 2, 3, 6], # left
                         4: [7, 8, 2, 3 ,6], # right
                        }


    all_phases = {
        "normal_intersection": normal_intersection,
        "top_intersection": top_intersection,
        "bottom_intersection": bottom_intersection,
        "left_intersection": left_intersection,
        "intersection_16_9": intersection_16_9,
        "intersection_17_9": intersection_17_9,
        "intersection_16_6": intersection_16_6,
        "intersection_17_6": intersection_17_6
    }
    
    return all_phases