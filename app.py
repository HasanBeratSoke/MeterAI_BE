import io
import os
from PIL import Image as pl
import json
from flask import Flask, request, jsonify, render_template, send_from_directory 
import base64
from ultralytics import YOLO
from PIL import Image
import cv2 as cv
import requests


app = Flask(__name__)
  
global model
model = YOLO("detectModel.pt")
model.to("cpu")

@app.route('/')
def index():
    return '<h1>MeterAI API Python Backend</h1>'


@app.route('/base', methods=['POST'])
def base():
    
    data = request.get_json()
    print(data['base64'])

    # its come base64 raw code from (MUHAMMED)
    rawdata = data['base64']
    encoded_data = str.encode(rawdata)
    

    b = base64.b64decode(encoded_data+ b'=' * (-len(rawdata) % 4) )
    val = io.BytesIO(b)
    img = pl.open(fp=val, mode='r') 
    img.save("test.jpeg") # converted and saved base64 to image
    print("Image saved")

    img_path  = "test.jpeg"
    img = cv.imread(img_path)

    #yolov8 model
    results = model.predict(img)
    result = results[0]
    numberList = []

    for box in result.boxes:
      class_id = result.names[box.cls[0].item()]
      if (class_id != "meter"):
        cords = box.xyxy[0].tolist()
        cords = [round(x) for x in cords]
        conf = round(box.conf[0].item(), 2)
        numberList.append((cords, class_id, conf))


    numberList.sort(key=lambda tup: tup[0][0])
    sorted_class_ids = [class_id for _, class_id, _ in numberList]

    sorted_class_ids_string = ''.join(sorted_class_ids)
    # send response to server (BILAL)
    raw_data = {
     "meterId": 5,
     "indexValue": sorted_class_ids_string
    }
    print(raw_data)

    
    response = requests.post('http://yildizbilal000-001-site1.ftempurl.com/invoice/add', json=raw_data)
    

    return jsonify(response.text)


if __name__ == "__main__":
  app.run()

