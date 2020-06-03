
import cv2
import numpy as np

PERSON_CLASS_ID = 0

class Network:
    def __init__(self, weightsPath, configPath, labelsPath, **kwargs):
        self.kwargs = kwargs
        self.net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)

        self.ln = self.net.getLayerNames()
        self.ln = [self.ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

    def make_boxes(self, image):
        (H, W) = image.shape[:2]
        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        layerOutputs = self.net.forward(self.ln)

        boxes = []
        confidences = []
        classIDs = []    
        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]
                if confidence > self.kwargs["confidence"] and classID == PERSON_CLASS_ID:
                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY, width, height) = box.astype("int")
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)
        idxs = np.array(sorted(cv2.dnn.NMSBoxes(boxes, confidences, self.kwargs["confidence"], self.kwargs["threshold"])))
        if len(idxs) > 0:
            boxes = np.array(boxes)[idxs[:,0]]
            # confidences = np.array(confidences)[idxs[:,0]]
            # classIDs = np.array(classIDs)[idxs[:,0]]
        else:
            boxes = np.array([])
            # confidences = np.array([])
            # classIDs = np.array([])
        return boxes
