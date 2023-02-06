import io
import os

from PIL import Image


MLAAS_URL = 'http://ml.taxi.dev.yandex.net/models/dkk'
LP_URL = 'http://front.tst.ape.yandex.net/licenseplate-ocr__v012/recognize'
AMMO_TEMPLATE = (
""" 
POST /remote_quality_control HTTP/1.1
Host: pyml.taxi.yandex.net
Accept: */*
User-Agent: Tank
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Length:

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="front"; filename="front.jpg"
Content-Type: image/jpeg

{front}
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="back"; filename="back.jpg"
Content-Type: image/jpeg

{back}
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="left"; filename="left.jpg"
Content-Type: image/jpeg

{left}
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="right"; filename="right.jpg"
Content-Type: image/jpeg

{right}
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="trunk"; filename="trunk.jpg"
Content-Type: image/jpeg

{trunk}
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="blank"; filename="blank.jpg"
Content-Type: image/jpeg

{blank}
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="salon_front"; filename="salon_front.jpg"
Content-Type: image/jpeg

{salon_front}
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="salon_back"; filename="salon_back.jpg"
Content-Type: image/jpeg

{salon_back}
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="exam_info"; filename="exam_info.json"
Content-Type: application/json

{exam_info}
------WebKitFormBoundary7MA4YWxkTrZu0gW--

"""
)

def to_utf(j):
    if isinstance(j, dict):
        for k, v in j.iteritems():
            j[k] = to_utf(j[k])
    elif isinstance(j, list):
        for i in xrange(len(j)):
            j[i] = to_utf(j[i])
    elif isinstance(j, unicode):
        return j.encode('utf-8')
    return j

def make_ammo(folder_images, exam_info_path):
    img_str_dict = {}
    for filename in ['front', 'back', 'left', 'right',
                     'trunk', 'blank', 'salon_front', 'salon_back']:
        with open(os.path.join(folder_images, filename) + '.jpg', 'rb') as f:
            img_str  = f.read()
            img = Image.open(io.BytesIO(img_str))
            img_str_dict[filename] = img_str
    with open(exam_info_path, 'r') as f:
        img_str_dict['exam_info'] = f.read()

    ammo_str = AMMO_TEMPLATE.format(front=img_str_dict['front'],
                                    back=img_str_dict['back'],
                                    left=img_str_dict['left'],
                                    right=img_str_dict['right'], 
                                    trunk=img_str_dict['trunk'],
                                    blank=img_str_dict['blank'],
                                    salon_front=img_str_dict['salon_front'],
                                    salon_back=img_str_dict['salon_back'], 
                                    exam_info=img_str_dict['exam_info'])
    
    
    index = ammo_str.find('Content-Length:') + len('Content-Length:')
    content_length = len(ammo_str[index:]) - 2
    # content_length = 858539
    ammo_str = ammo_str[:index] + b' ' + str(content_length) + ammo_str[index:]
    total_length = len(b'' + ammo_str.lstrip('\n')) - 2
    # total_length = 858725
    ammo_str = b'' + str(total_length) + '' + ammo_str

    return ammo_str

def send_parallel_requests_mlaas(data, session_trash):
    reqs = []
    photos_iterator = PHOTO_TO_NUMBER_MAPPING.iteritems()
    for photo_key, photo_number in photos_iterator:
        req = grequests.request(
            method='post',
            url=MLAAS_URL,
            data=data[photo_key],
            params={'type': photo_number},
            headers={'Content-Type': 'image/png'},
            timeout=(0.05, 0.5),
            session=session_trash
        )
        reqs.append(req)
    resps = grequests.map(reqs)
    return resps

def send_parallel_requests_cv(data, session_lp):
    reqs = []
    for photo_key in ['front', 'back']:
        req = grequests.request(
            method='post',
            url=LP_URL,
            data=data[photo_key],
            headers={'Content-Type': 'image/png'},
            timeout=(0.05, 0.75),
            session=session_lp
        )
        reqs.append(req)
    resps = grequests.map(reqs)
    return resps
