import io
import os
from PIL import Image as pl
import json
from flask import Flask, request, jsonify, render_template, send_from_directory 
import base64
from ultralytics import YOLO
from PIL import Image
import cv2 as cv

app = Flask(__name__)
  
global model
model = YOLO("detectModel.pt")


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
    resultsMeter = model.predict(img)
    result = resultsMeter[0]


    for box in result.boxes:
      class_id = result.names[box.cls[0].item()]
      if (class_id == "meter"):
        cords = box.xyxy[0].tolist()
        cords = [round(x) for x in cords]
        conf = round(box.conf[0].item(), 2)

        # crop meter
        meter_crop = img[cords[1]:cords[3], cords[0]:cords[2]]
        resultsNumber = model.predict(meter_crop)
        result = resultsNumber[0]
        print(result.names)
        numberList = []
        for box in result.boxes:
            class_id = result.names[box.cls[0].item()]
            if (class_id != "meter"):
                cords = box.xyxy[0].tolist()
                cords = [round(x) for x in cords]
                conf = round(box.conf[0].item(), 2)
                print("Object type:", class_id)
                print("Coordinates:", cords)
                print("Probability:", conf)
                print("---")
                numberList.append((cords, class_id, conf))

        numberList.sort(key=lambda tup: tup[0][0])

        sorted_class_ids = [class_id for _, class_id, _ in numberList]
        print(sorted_class_ids)
        sorted_class_ids_string = ''.join(sorted_class_ids)

        # send response to server (BILAL)

        raw_data = {
            'MeterId': 3,
            'IndexValue': sorted_class_ids_string

        }

        json_data = json.dumps(raw_data)


        response = request.post('http://yildizbilal000-001-site1.ftempurl.com/invoice/add', json=json_data)

        
        if response.status_code == 200:
            return 'Veri başariyla gönderildi'
        else:
            return 'Veri gönderimi başarisiz'
        
        break
      
        return jsonify(sorted_class_ids)
    return jsonify("Meter not found")


if __name__ == "__main__":
  app.run()

