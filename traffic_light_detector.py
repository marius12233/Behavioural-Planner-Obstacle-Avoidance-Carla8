import traffic_light_detection_module 
from traffic_light_detection_module.predict import *
import cv2
import numpy as np

def load_model():
    config = get_config(os.path.join("traffic_light_detection_module", "config.json"))
    model = get_model(config)
    return model

class TrafficLightDetector:


    def __init__(self, model):
        self.__model = model
        self.__bbox=None
        self.__class = None
        self.__img = None
        self.box = None
        #self._min_frames_ok = 3 #minimum number of frames 
        self._max_frame_ok = 2 #number of consecutive frames to detect traffic light 
        self._counter_consecutive_detection = 0
    
    def find_traffic_light(self, img):
        if img is None:
            return None
        boxes = self.__model.predict(img)
        self.__img = img
        if len(boxes)==0:
            self.__bbox=None
            return None #There is any traffic ligth
        
        box=boxes[0] #the most important
        self.box = box
        score = box.get_score()
        if score<0.2:
            self.__bbox=None
            return None
        #print("Score: ", score)
        w,h,_ = img.shape
        self.__class = box.get_label()
        self.__bbox = (int(box.xmin*w), int(box.ymin*h), int(box.xmax*w), int(box.ymax*h))
        self._counter_consecutive_detection+=1
        if self._counter_consecutive_detection < self._max_frame_ok:
            return None
        else:
            self._counter_consecutive_detection=0

        return self.__bbox

    def get_bbox(self):
        return self.__bbox
    
    def get_enlarged_bbox(self):
        bbox = self.get_bbox()
        if bbox is None:
            return None
        xmin, ymin, xmax, ymax = bbox
        xmin-=20
        #ymin-=50
        xmax+=20
        #ymax+=50
        return (xmin, ymin, xmax, ymax)
        

    def is_red(self):
        return self.__class
    

    def draw_boxes_on_image(self, img):
        if self.__bbox is None or self.__img is None:
            return img
        label = self.is_red()
        c = (0,255,0) if label == 0 else (0,0,255)
        #img = np.copy(img)
        bbox = self.get_bbox()
        cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), c)
        return img 

    def draw_enlarged_boxes_on_image(self, img):
        if self.__bbox is None or self.__img is None:
            return img
        label = self.is_red()
        c = (0,255,0) if label == 0 else (0,0,255)
        #img = np.copy(img)
        bbox = self.get_enlarged_bbox()
        x_c = bbox[0] + (bbox[2] - bbox[0])//2 #take the center point
        y_c = bbox[1] + (bbox[3] - bbox[1])//2
        cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), c)
        cv2.circle(img, (int(x_c),int(y_c)), 1, (0,0,255), thickness=-1)
        return img        
    

    def show_traffic_light(self):
        if self.__img is None:
            return None
        img = self.draw_boxes_on_image()
        if img is None:
            return 
        cv2.imshow("img traffic light", img)
        cv2.waitKey(0)


if __name__=="__main__":
    detector = TrafficLightDetector()
    img = cv2.imread(os.path.join("traffic_light_detection_module", "test_images","test (8).png"))
    detector.find_traffic_light(img)
    detector.show_traffic_light()

