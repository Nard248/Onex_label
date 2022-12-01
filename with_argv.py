import os
import cv2
from google.cloud import vision
import io
from pyzbar.pyzbar import decode

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'token.json'


def resize_image(path):
    image = cv2.imread(path)
    height = image.shape[0]
    width = image.shape[1]
    size = (1500, int((1500 / width) * height))
    image_resized = cv2.resize(image, dsize=size)
    return image_resized


def detect_text(path):
    from google.cloud import vision
    import io
    address_ok = False
    user_code_ok = False
    track_ok = False

    address_variants = ['Ayre', 'Ayrie', 'Aire']
    client = vision.ImageAnnotatorClient()
    with io.open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    response_json = {}
    for text in texts:
        # print(text.description)
        # print('next')
        text_ = text.description
        for address in address_variants:
            if address.upper() in text_.upper() and not address_ok:
                response_json['address'] = 'Ok'
                address_ok = True
                break
        if 'RU' in text_ and len(text_) == 8:
            response_json['User_code'] = text_
            response_json['Country'] = 'RU'
            user_code_ok = True
        elif 'ARM' in text_ and len(text_) == 9:
            response_json['User_code'] = text_
            response_json['Country'] = 'ARM'
            user_code_ok = True
        elif 'GE' in text_ and len(text_) == 7:
            response_json['User_code'] = text_
            response_json['Country'] = 'GE'
            user_code_ok = True
        elif 'TBS' in text_:
            if '_' in text_ and len(text_) == 11:
                response_json['User_code'] = text_.replace('-', '')
                response_json['Country'] = 'GE'
                user_code_ok = True
            elif len(text_) == 10:
                response_json['User_code'] = text_
                response_json['Country'] = 'GE'
                user_code_ok = True

        # vertices = (['({},{})'.format(vertex.x, vertex.y)
        #              for vertex in text.bounding_poly.vertices])

        # print('bounds: {}'.format(','.join(vertices)))
    image_ = cv2.imread(path)
    decoded = decode(image_)
    tracks = []
    for i in range(len(decoded)):
        tracks.append(str(decoded[i].data.decode('utf-8')))
    if tracks[0]: track_ok = True

    for i in decoded:
        print(i.data.decode('utf-8'))
    if track_ok and user_code_ok and address_ok:
        response_json['status'] = 'Ok'
        response_json['tracking'] = tracks

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    return response_json


if __name__ == '__main__':
    import json, sys

    request = json.load(sys.stdin)
    print(request['Path'])
    path = str(request['Path'])

    print(detect_text(path))
