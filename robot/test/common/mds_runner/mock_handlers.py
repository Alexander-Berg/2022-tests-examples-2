from BaseHTTPServer import BaseHTTPRequestHandler


class MdsImagesMainMockHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.protocol_version = 'HTTP/1.1'
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write("""
        {
            "group-id": 3964,
            "imagename": "2a00000170ea620c4108627cea4652c84a93",
            "meta": {
                "crc64": "9F4419C007084F11",
                "md5": "317ca97f12a7d7f8c1d4371c8ce29cb9",
                "modification-time": 1584480259,
                "orig-animated": false,
                "orig-format": "WEBP",
                "orig-orientation": "0",
                "orig-size": {
                    "x": 1680,
                    "y": 1050
                },
                "orig-size-bytes": 243508,
                "processed_by_computer_vision": false,
                "processed_by_computer_vision_description": "computer vision is disabled",
                "processing": "finished"
            },
            "sizes": {
                "orig": {
                    "height": 1050,
                    "path": "/get-images-thumbs/3964/2a00000170ea620c4108627cea4652c84a93/orig",
                    "width": 1680
                }
            }
        }""")


class MdsImagesFreshMockHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.protocol_version = 'HTTP/1.1'
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write("""
        {
            "group-id": 3964,
            "imagename": "2a00000170ea620c4108627cea4652c84a93",
            "meta": {
                "crc64": "9F4419C007084F11",
                "expires-at": "Thu, 19 Mar 2020 21:24:19 GMT",
                "md5": "317ca97f12a7d7f8c1d4371c8ce29cb9",
                "modification-time": 1584480259,
                "orig-animated": false,
                "orig-format": "JPEG",
                "orig-orientation": "0",
                "orig-size": {
                    "x": 1680,
                    "y": 1050
                },
                "orig-size-bytes": 243508,
                "processed_by_computer_vision": false,
                "processed_by_computer_vision_description": "computer vision is disabled",
                "processing": "finished"
            },
            "sizes": {
                "n_13": {
                    "height": 1050,
                    "path": "/get-fast-images/3964/2a00000170ea620c4108627cea4652c84a93/n_13",
                    "width": 1680
                },
                "orig": {
                    "height": 1050,
                    "path": "/get-fast-images/3964/2a00000170ea620c4108627cea4652c84a93/orig",
                    "width": 1680
                }
            }
        }""")
