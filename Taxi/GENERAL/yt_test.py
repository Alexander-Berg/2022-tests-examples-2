import yt
import yt.yson
import json
import io
from PIL import Image
import io
import sys
import base64
import imp

'''
with open('test.json', 'rb') as file:
    for i, line in enumerate(file):
        test = json.loads(line)

        #Image.open(base64.decodestring(test['Image']))
        with io.open(str(i) + '.jpg', 'wb') as wf:
            wf.write(base64.decode(test['Image']))
'''

with open('test.yson', 'r') as file:
    test = yt.yson.load(file, yson_type="list_fragment")
    for i, line in enumerate(test):
        print((line['Labels']))
        with open(str(i) + '.jpg', 'wb') as wf:
            wf.write(line['Image'])
