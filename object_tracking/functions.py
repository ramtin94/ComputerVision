class Euclidian_Distance_Tracker():
    def __init__(self, number_of_objects, max_frame_search=5, min_distance_between_2_frames=30):
        self.number_of_objects = number_of_objects 
        self.max_frame_search = max_frame_search
        self.min_distance_between_2_frames = min_distance_between_2_frames
        

        self.objects_array = []

        self.__initialize_object_list()
        

    def __initialize_object_list(self):
        for object_index in range(self.number_of_objects):
            object_dict = dict()
            object_dict["ID"] = object_index
            object_dict["bbs"] = np.array([-1, -1, -1, -1])
            object_dict["missing_frames"] = 0 
            object_dict["observability_status"] = 0
            self.objects_array.append(object_dict)
            


    def __add_object_to_list(self, new_obj_bbs):
        for index in range(self.number_of_objects):
            if self.objects_array[index]["observability_status"] == 0:
                self.objects_array[index]["bbs"] = new_obj_bbs
                self.objects_array[index]["missing_frames"] = 0
                self.objects_array[index]["observability_status"] = 1
                break

    def __calculate_center_of_object(self, object_bb):
        x1, y1, x2, y2 = object_bb
        cx = (x1+x2)/2
        cy = (y1+y2)/2

        return (cx, cy)


    ###############################################

    def get_object_array(self):
        return self.objects_array

    
    def update(self, objects_bbs):
        ######### match the new bbs to previous objects ############
        found_tracklets = list()
        for object_bb in objects_bbs:
            new_object_center = self.__calculate_center_of_object(object_bb)

            object_observed_before = False
            min_distance = np.inf
            min_distance_id = -1
            
            for object_index in range(self.number_of_objects):
                observed_object_center = self.__calculate_center_of_object(self.objects_array[object_index]["bbs"])
                eu_dist = sp.spatial.distance.euclidean(observed_object_center, new_object_center)
                
                if eu_dist<min_distance:
                    min_distance = eu_dist
                    min_distance_id = object_index

            if min_distance < self.min_distance_between_2_frames:
                self.objects_array[min_distance_id]["bbs"] = object_bb
                self.objects_array[min_distance_id]["missing_frames"] = 0
                found_tracklets.append(min_distance_id)
                object_observed_before = True

            if not object_observed_before:
                self.__add_object_to_list(object_bb)

        ################ update missing frames and observabiltiy status #####################
        for index in range(self.number_of_objects):
            if not (index in found_tracklets) and (self.objects_array[index]["observability_status"] == 1) :
                self.objects_array[index]["missing_frames"]+=1
                if self.objects_array[index]["missing_frames"]>self.max_frame_search:
                    self.objects_array[index]["observability_status"] = 0

        return self.objects_array

def get_center_of_bbs(last_frame_centers, bbs):
    curr_frame_centers = 15*np.ones((bbs.shape[0], 3), dtype=np.int32)
    for bb in range(bbs.shape[0]):
        curr_frame_centers[bb][0] = int((bbs[bb][0]+bbs[bb][2])/2)
        curr_frame_centers[bb][1] = int((bbs[bb][1]+bbs[bb][3])/2)
    
    disapeared_circles = list()
    for center_index in range(last_frame_centers.shape[0]):
        last_frame_centers[center_index][2]-=2
        if last_frame_centers[center_index][2] <= 0:
            disapeared_circles.append(center_index)
    
    last_frame_centers = np.delete(last_frame_centers, disapeared_circles, axis=0)
    
    centers = np.append(last_frame_centers, curr_frame_centers, axis=0)
    return centers


