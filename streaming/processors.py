
import os
import itertools

from django.conf import settings
from scipy.spatial import distance
import numpy as np
import cv2

ORI_X = 0
ORI_Y = 1
WIDTH = 2
HEIGHT = 3

PERSON_CLASS_ID = 0
COLOR_PEOPLE_BOX = (99,  43, 206)
COLOR_FAR_LINE = (102, 220, 225)
COLOR_CLOSE_LINE = (36,60, 255)
LIGHT_COLOR_TEXT = (255,255,255)
DARK_COLOR_TEXT = (0, 0, 0)
THICKNESS_LINE = 2
SECURE_DISTANCE = 2

class CamProcessor:
    def __init__(self):
        self.args = {
            'threshold': settings.MODEL_THRESHOLD,
            'confidence': settings.MODEL_CONFIDENCE,
            'people_height': settings.MODEL_PEOPLE_HEIGHT,
        }

        weightsPath = os.path.join(settings.MODEL_PATH, settings.MODEL_WEIGHTS)
        configPath = os.path.join(settings.MODEL_PATH, settings.MODEL_CONFIG)
        self.net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)

        if settings.MODEL_ENABLE_CUDA:
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

        self.ln = self.net.getLayerNames()
        self.ln = [self.ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

    def make_boxes(self, image):
        (H, W) = image.shape[:2]
        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        net = self.net
        args = self.args
        ln = self.ln
        net.setInput(blob)
        layerOutputs = self.net.forward(self.ln)
        boxes = []
        confidences = []
        classIDs = []    
        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]
                if confidence > args["confidence"] and classID == PERSON_CLASS_ID:
                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY, width, height) = box.astype("int")
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)
        idxs = np.array(sorted(cv2.dnn.NMSBoxes(boxes, confidences, args["confidence"], args["threshold"])))
        if len(idxs) > 0:
            boxes = np.array(boxes)[idxs[:,0]]
            confidences = np.array(confidences)[idxs[:,0]]
            classIDs = np.array(classIDs)[idxs[:,0]]
        else:
            boxes = np.array([])
            confidences = np.array([])
            classIDs = np.array([])
        return boxes

    def mesure_distance(self, boxes):
        get_lower_center = lambda box: (box[ORI_X] + box[WIDTH] // 2, box[ORI_Y] + box[HEIGHT])
        f = lambda x: np.arctan(x) / (np.pi/2)

        results = []
        for (index_a, box_a), (index_b, box_b) in itertools.combinations(enumerate(boxes), 2):
            base_box_a = get_lower_center(box_a)
            base_box_b = get_lower_center(box_b)

            euclidean_distance = distance.euclidean(base_box_a, base_box_b)
            height_box_a = self.args['people_height'] / box_a[HEIGHT]
            height_box_b = self.args['people_height'] / box_b[HEIGHT]

            l1 = f(box_a[HEIGHT] / box_b[HEIGHT])
            l2 = 1 - l1

            D = l1 * height_box_a * euclidean_distance + l2 * height_box_b * euclidean_distance

            a = [index_a, index_b,
                 base_box_a, base_box_b, 
                 round(D, 2)]
            results.append(a)

        return np.array(results)

    def get_min_distances(self, distances):
        min_distances = []
        if len(distances)>0:
            for i in set(distances[:,0]):
                a = distances[distances[:,0] == i][distances[distances[:,0] == i][:,-1].argmin()]
                min_distances.append(a)

        return np.array(min_distances)

    def draw_over_frame(self, image, boxes, distance_lines):
        for box in boxes:
            edge_0 = (box[ORI_X], box[ORI_Y])
            edge_1 = (box[ORI_X] + box[WIDTH], box[ORI_Y] + box[HEIGHT])
            cv2.rectangle(image, edge_0, edge_1, COLOR_PEOPLE_BOX, THICKNESS_LINE)

        for line in distance_lines:
            line_color = COLOR_CLOSE_LINE if line[4] < SECURE_DISTANCE else COLOR_FAR_LINE
            image = cv2.line(image, line[2], line[3], line_color, THICKNESS_LINE)

            e = ((np.array(line[2])+np.array(line[3]))/2).astype(int)
            mesure_text = '{}m'.format(line[4])
            position_text = (e[0], e[1] - 5)
            cv2.putText(image, mesure_text, position_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, DARK_COLOR_TEXT, THICKNESS_LINE)
            cv2.putText(image, mesure_text, position_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, LIGHT_COLOR_TEXT, THICKNESS_LINE - 1)

        return image

    def calculate_statistical_results(self, boxes, distance_lines):
        amount_people = len(boxes)

        if amount_people > 1:
            minimal_distance = min([x[4] for x in distance_lines])
            average_distance = np.mean([x[4] for x in distance_lines])
        else:
            minimal_distance = 0
            average_distance = 0

        return {
            'amount_people': amount_people,
            'minimal_distance': minimal_distance,
            'average_distance': average_distance,
        }

    def inference(self, frame):
        frame = cv2.resize(frame, (640, 360),
            fx=0, fy=0, interpolation=cv2.INTER_LINEAR)

        boxes = self.make_boxes(frame)
        distance_lines = self.mesure_distance(boxes)
        shorter_distance_lines = self.get_min_distances(distance_lines)

        statistical = self.calculate_statistical_results(boxes, shorter_distance_lines)
        if statistical['amount_people'] > 0:
            frame = self.draw_over_frame(frame, boxes, shorter_distance_lines)

        results = {
            'frame': frame,
            'graphical': {
                'boxes': boxes,
                'distance_lines': distance_lines,
            },
            'statistical': statistical
        }

        return results
