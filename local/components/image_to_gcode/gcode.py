import os
import numpy as np
import cv2


class MyImageProcessing:
    def __init__(self) -> None:
        # self.monitor_width = None
        # self.monitor_height = None
        # self.frame_add_width_default = 30
        # self.frame_add_heigth_default = 100
        # self.frame_add_posX_default = 0
        # self.frame_add_posY_default = 0
        # self.frame_add_width = None
        # self.frame_add_heigth = None
        # self.frame_add_posX = None
        # self.frame_add_posY = None
        self.resize_scale_default = 100
        self.resize_scale = self.resize_scale_default
        self.image = None
        self.image_width = None
        self.image_heigth = None
        # self.image_remove = None
        self.image_resize = None
        # self.image_resize_org = None
        # self.image_resize_remove = None
        # self.image_resize_width = None
        # self.image_resize_heigth = None
        self.threshold_maxValue_default = 255
        self.threshold_blockSize_default = 17
        self.threshold_constant_default = 10
        self.threshold_maxValue = self.threshold_maxValue_default
        self.threshold_blockSize = self.threshold_blockSize_default
        self.threshold_constant = self.threshold_constant_default
        self.threshold_binary = None #cv2.THRESH_BINARY_INV cv2.THRESH_BINARY
        self.image_threshold = None
        # self.image_active_org = None 
        # self.image_acitve_remove = None
        self.image_white_contour = None
        self.contour_minArcLength_default = 0
        self.contour_minArcLength = self.contour_minArcLength_default
        self.app_save_dir = "App_save_data"
        # self.face_detect = False
        self.final_contours = None
        # self.final_contours_resize = None

        
    def resize_image(self, image):
        self.image_heigth, self.image_width, _ = np.shape(image)
        newWidth = int(self.image_width * self.resize_scale / 100)
        newHeight = int(self.image_heigth * self.resize_scale / 100)
        newDimension = (newWidth, newHeight)
        # resize image
        self.image_resize = cv2.resize(image, newDimension, interpolation = cv2.INTER_AREA)
        self.image_resize_heigth, self.image_resize_width, _ = np.shape(self.image_resize)
        # self.image_blank = np.ones((self.image_resize_heigth,self.image_resize_width, 3), np.uint8)*255
        return self.image_resize
    
    # def __create_default_frame_size(self, width, height):
    #     self.frame_default_w = width//3
    #     self.frame_default_h = height//3
    #     self.frame_default_x = width//2 - self.frame_default_w//2
    #     self.frame_default_y = height//2 - self.frame_default_h//2
        
    # def face_detection(self, image):
    #     tmp_height, tmp_width, _ = np.shape(image)
    #     self.__create_default_frame_size(tmp_width, tmp_height)
    #     # Load the cascade
    #     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    #     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #     self.faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    #     if len(self.faces) >= 1:
    #         self.face_detect = True
    #     else:
    #         self.face_detect = False
        
    # def draw_rectangle(self, image):
    #     # Draw rectangle around the faces
    #     image_frame = np.copy(image)
    #     add_w = self.frame_add_width
    #     add_h = self.frame_add_heigth
    #     add_posX = self.frame_add_posX
    #     add_posY = self.frame_add_posY
    #     if self.face_detect:
    #         for (x, y, w, h) in self.faces:
    #             cv2.rectangle(image_frame, (x-add_posX-add_w, y-add_posY-add_h), (x-add_posX+w+add_w, y-add_posY+h+add_h), (255, 10, 255), 2)
    #             image_cut = image[y-add_posY-add_h:y-add_posY+h+add_h, x-add_posX-add_w:x-add_posX+w+add_w]
    #             break
    #     else:
    #         x = self.frame_default_x
    #         y = self.frame_default_y
    #         w = self.frame_default_w
    #         h = self.frame_default_h
    #         cv2.rectangle(image_frame, (x-add_posX-add_w, y-add_posY-add_h), (x-add_posX+w+add_w, y-add_posY+h+add_h), (255, 0, 0), 2)
    #         image_cut = image[y-add_posY-add_h:y-add_posY+h+add_h, x-add_posX-add_w:x-add_posX+w+add_w]
            
    #     # return image_frame, image_cut
    #     self.image_cut = image_cut
    #     self.image_frame = image_frame
    #     self.image_cut_heigth, self.image_cut_width, _ = np.shape(image_cut)
    #     self.image_blank = np.ones((self.image_cut_heigth,self.image_cut_width, 3), np.uint8)*255
        
    # def removebg(self, image):
    #     image_remove = remove(image)
    #     self.image_remove = cv2.cvtColor(image_remove, cv2.COLOR_RGBA2RGB)
        
    def adaptive_threshold(self, image):
        self.image_gray=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.image_threshold = cv2.adaptiveThreshold(self.image_gray, self.threshold_maxValue, 
                                                     cv2.ADAPTIVE_THRESH_GAUSSIAN_C, self.threshold_binary, #_INV
                                                     self.threshold_blockSize, self.threshold_constant)
    
    def contour_proportion(self):
        minX, maxX, minY, maxY = self.contours_minX_maxX_minY_maxY(self.final_contours)
        self.final_contour_proportion = maxX/maxY
          
    def contour(self):
        self.image_white_contour = np.ones((self.image_resize_heigth,self.image_resize_width, 3), np.uint8)*255
        contours, hierarchy = cv2.findContours(self.image_threshold,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
        self.final_contours = []
        for i, c in enumerate(contours):
            areaContour=cv2.arcLength(c,True)
            area_min =self.contour_minArcLength
            area_max = 1000000000
            if areaContour<area_min or area_max<areaContour:
                continue
            else:
                self.final_contours.append(c)
            cv2.drawContours(self.image_white_contour, contours, i, (0,0,0), 2)

    def contours_minX_maxX_minY_maxY(self, contours):
        minX = 100000
        maxX = 0
        minY = 100000
        maxY = 0

        for count, c in enumerate(contours):
            tmp_minX = np.min(c[:,:,0])
            tmp_minY = np.min(c[:,:,1])
            tmp_maxX = np.max(c[:,:,0])
            tmp_maxY = np.max(c[:,:,1])
            if tmp_minX < minX:
                minX = tmp_minX
            if tmp_minY < minY:
                minY = tmp_minY
            if tmp_maxX > maxX:
                maxX = tmp_maxX
            if tmp_maxY > maxY:
                maxY = tmp_maxY

        return minX, maxX, minY, maxY
    
    def contours_shift(self, contours):
        #set contour to (0,0)
        minX, maxX, minY, maxY = self.contours_minX_maxX_minY_maxY(contours)
        contours_array = []
        for count, contour in enumerate(contours):
            contour_list = []
            for points in contour:
                contour_list.append([[points[0][0] - minX, points[0][1] - minY]])
            contours_array.append(np.array(contour_list))
        
        self.final_contours = contours_array


    def contours_scale(self, contours, x_scale, y_scale):
        contours_array = []
        for count, contour in enumerate(contours):
            contour_list = []
            for points in contour:
                contour_list.append([[points[0][0]*x_scale, points[0][1]*y_scale]])
            contours_array.append(np.array(contour_list))
            
        self.final_contours = contours_array

    def contours_round(self, contours, digits):
        contours_array = []
        for count, contour in enumerate(contours):
            contour_list = []
            for points in contour:
                contour_list.append([[round(points[0][0], digits), round(points[0][1], digits)]])
            contours_array.append(np.array(contour_list))
            
        self.final_contours = contours_array

    def contours_flip_X(self, contours):
        minX, maxX, minY, maxY = self.contours_minX_maxX_minY_maxY(contours)
        contours_array = []
        for count, contour in enumerate(contours):
            contour_list = []
            for points in contour:
                tmp_x = points[0][0]
                tmp_x = tmp_x + abs(tmp_x-maxX)*2 - maxX
                contour_list.append([[tmp_x, points[0][1]]])
            contours_array.append(np.array(contour_list))
            
        self.final_contours = contours_array

    def contours_flip_Y(self, contours):
        minX, maxX, minY, maxY = self.contours_minX_maxX_minY_maxY(contours)
        contours_array = []
        for count, contour in enumerate(contours):
            contour_list = []
            for points in contour:
                tmp_y = points[0][1]
                tmp_y = tmp_y + abs(tmp_y-maxY)*2 - maxY
                contour_list.append([[points[0][0], tmp_y]])
            contours_array.append(np.array(contour_list))
            
        self.final_contours = contours_array

    def contours_approx(self, contours, fac, minArcLength=0, maxArcLength=1000000000):
        contour_approx = []
        for contour in contours:
            tmp_arcLen = cv2.arcLength(contour, True)
            if  tmp_arcLen >= minArcLength and tmp_arcLen < maxArcLength:
                epsilon = fac*cv2.arcLength(contour, True)
                contour_approx.append(cv2.approxPolyDP(contour, epsilon, True))
        # return contour_approx
        self.final_contours = contour_approx

    def contours_hull(self, contours, minArcLength=0, maxArcLength=1000000000):
        contour_hull = []
        for contour in contours:
            tmp_arcLen = cv2.arcLength(contour, True)
            if  tmp_arcLen >= minArcLength and tmp_arcLen < maxArcLength:
                contour_hull.append(cv2.convexHull(contour))
        return contour_hull

    def contours_select(self, contours, minArcLength=0, maxArcLength=1000000000):
        contour_select = []
        for contour in contours:
            tmp_arcLen = cv2.arcLength(contour, True)
            if  tmp_arcLen >= minArcLength and tmp_arcLen < maxArcLength:
                contour_select.append(contour)
        return contour_select

    def contours_minArcLength_maxArcLencth(self, contours):
        minArcLen = 100000
        maxArcLen = 0
        for contour in contours:
            tmp_len = cv2.arcLength(contour, True)
            if tmp_len < minArcLen:
                minArcLen = tmp_len
            if tmp_len > maxArcLen:
                maxArcLen = tmp_len
        return minArcLen, maxArcLen
    
    def draw_final_contours(self):
        self.image_white_contour = np.ones((self.image_resize_heigth,self.image_resize_width, 3), np.uint8)*255
        cv2.drawContours(self.image_white_contour, self.final_contours, -1, (0,0,0), 2)

    def safe_final_contours(self):
        tar_dir = self.app_save_dir
        if not os.path.isdir(tar_dir):
            os.makedirs(tar_dir)
        if self.final_contours is not None:
            np.save(os.path.join(tar_dir, "final_contours.npy"), np.asanyarray(self.final_contours, dtype=object))
            print("Saved successfully!")
        else:
            print("list final_contours not exist")
            
    def load_final_contours(self):
        src_dir = self.app_save_dir
        tempNumpyArray=np.load(os.path.join(src_dir, "final_contours.npy"), allow_pickle=True)
        return tempNumpyArray.tolist()

class MyGcode:
    def __init__(self) -> None:
        self.z_safe_hight_default = 10.0
        self.z_working_hight_default = 0.5
        self.z_depth_default = 1
        self.z_feed_default = 500
        self.xy_feed_default = 1000
        self.spindle_speed_default = 24000
        
        self.z_safe_hight = self.z_safe_hight_default
        self.z_working_hight = self.z_working_hight_default
        self.z_depth = self.z_depth_default
        self.z_feed = self.z_feed_default
        self.xy_feed = self.xy_feed_default = 1000
        self.spindle_speed = self.spindle_speed_default
        self.save_file_str = None
        self.gcode_data = []
        
    def check_save_file_str(self): 
        
        if self.save_file_str is None:
            self.save_file_str = 'gcode.tap'
        else:
            test_save_str = os.path.splitext(self.save_file_str)
            if test_save_str[-1] == "":
                self.save_file_str = self.save_file_str + '.tap'

    
    def generate_gcode(self, contours):
        # set contour to (0|0)
        minX = 1000
        maxX = 0
        minY = 1000
        maxY = 0

        for count, c in enumerate(contours):
            tmp_minX = np.min(c[:,:,0])
            tmp_minY = np.min(c[:,:,1])
            tmp_maxX = np.max(c[:,:,0])
            tmp_maxY = np.max(c[:,:,1])
            if tmp_minX < minX:
                minX = tmp_minX
            if tmp_minY < minY:
                minY = tmp_minY
            if tmp_maxX > maxX:
                maxX = tmp_maxX
            if tmp_maxY > maxY:
                maxY = tmp_maxY
                
        contours_list = []
        contours_array = []
        for count, contour in enumerate(contours):
            contour_list = []
            for points in contour:
                contour_list.append([points[0][0] - minX, points[0][1] - minY])

            contours_list.append(contour_list)
            contours_array.append(np.array(contour_list))
        
        
        # write g-code 
        z_safe_hight = self.z_safe_hight
        z_working_hight = self.z_working_hight
        z_depth = self.z_depth
        z_feed = self.z_feed
        xy_feed = self.xy_feed
        spindle_speed = self.spindle_speed

        gcode_start = [f"M03 S{spindle_speed}", f"G00 Z{z_safe_hight}"]
        gcode_end = [f"G00 Z{z_safe_hight}", "G00 X0 Y0", "M05", "M30"]
        
        self.check_save_file_str()
        
        self.gcode_data = []
        
        with open(self.save_file_str, 'w') as f:
            for count, elem in enumerate(gcode_start):
                f.write(f"{elem}\n")
                self.gcode_data.append(f"{elem}\n")
            for count_contour, contour in enumerate(contours_list):
                tmp_contour_len = len(contour)
                # f.write(f"{tmp_contour_len}#####################################\n")
                if tmp_contour_len == 1:
                    f.write(f"G00 X{contour[0][0]} Y{contour[0][1]}\n")
                    f.write(f"G00 Z0\n")
                    f.write(f"G01 Z-{z_depth} F{z_feed}\n")
                    f.write(f"G00 Z{z_working_hight}\n")
                    self.gcode_data.append(f"G00 X{contour[0][0]} Y{contour[0][1]}\n")
                    self.gcode_data.append(f"G00 Z0\n")
                    self.gcode_data.append(f"G01 Z-{z_depth} F{z_feed}\n")
                    self.gcode_data.append(f"G00 Z{z_working_hight}\n")
                if tmp_contour_len == 2:
                    f.write(f"G00 X{contour[0][0]} Y{contour[0][1]}\n")
                    f.write(f"G00 Z0\n")
                    f.write(f"G01 Z-{z_depth} F{z_feed}\n")
                    f.write(f"G01 X{contour[1][0]} Y{contour[1][1]} F{xy_feed}\n")
                    f.write(f"G00 Z{z_working_hight}\n")
                    self.gcode_data.append(f"G00 X{contour[0][0]} Y{contour[0][1]}\n")
                    self.gcode_data.append(f"G00 Z0\n")
                    self.gcode_data.append(f"G01 Z-{z_depth} F{z_feed}\n")
                    self.gcode_data.append(f"G01 X{contour[1][0]} Y{contour[1][1]} F{xy_feed}\n")
                    self.gcode_data.append(f"G00 Z{z_working_hight}\n")
                if tmp_contour_len > 2:
                    f.write(f"G00 X{contour[0][0]} Y{contour[0][1]}\n")
                    f.write(f"G00 Z0\n")
                    f.write(f"G01 Z-{z_depth} F{z_feed}\n")
                    self.gcode_data.append(f"G00 X{contour[0][0]} Y{contour[0][1]}\n")
                    self.gcode_data.append(f"G00 Z0\n")
                    self.gcode_data.append(f"G01 Z-{z_depth} F{z_feed}\n")
                    for i in range(tmp_contour_len-1):
                        if i == 0:
                            f.write(f"G01 X{contour[i+1][0]} Y{contour[i+1][1]} F{xy_feed}\n")
                            self.gcode_data.append(f"G01 X{contour[i+1][0]} Y{contour[i+1][1]} F{xy_feed}\n")
                        else:
                            f.write(f"G01 X{contour[i+1][0]} Y{contour[i+1][1]}\n")
                            self.gcode_data.append(f"G01 X{contour[i+1][0]} Y{contour[i+1][1]}\n")
                    f.write(f"G00 Z{z_working_hight}\n")
                    self.gcode_data.append(f"G00 Z{z_working_hight}\n")
            for count, elem in enumerate(gcode_end):
                f.write(f"{elem}\n")
                self.gcode_data.append(f"{elem}\n")
                

if __name__ == '__main__':

    img = cv2.imread('gcode_test_img_haus.png')
    # cv2.imshow('1) org img', img)

    
    imgpro = MyImageProcessing()
    imgpro.resize_scale = 200
    img = imgpro.resize_image(img)
    
    # cv2.imshow('2) resize img', img)

    
    imgpro.threshold_blockSize = 21
    imgpro.threshold_constant = 45
    imgpro.threshold_binary = cv2.THRESH_BINARY_INV
    imgpro.adaptive_threshold(img)
    
    # cv2.imshow('3) threshold img', imgpro.image_threshold)
    
    
    imgpro.contour_minArcLength = 0
    imgpro.contour()
    
    cv2.imshow('4) contour img', imgpro.image_white_contour)
    
    
    imgpro.contours_shift(imgpro.final_contours)
    imgpro.draw_final_contours()
    cv2.imshow('5) final contours shift', imgpro.image_white_contour)
    
    
    imgpro.contours_flip_Y(imgpro.final_contours)
    imgpro.draw_final_contours()
    cv2.imshow('6) final contours flip Y', imgpro.image_white_contour)
    
    
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    
    
    gcode = MyGcode()
    gcode.save_file_str = "gcode.tap"
    gcode.generate_gcode(imgpro.final_contours)
    
    
    
    
    