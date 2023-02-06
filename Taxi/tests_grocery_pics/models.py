import uuid


class Image:
    def __init__(self, *, base64_size_bytes, width=100, height=100):
        self.group_id = 'group_id'
        self.name = str(uuid.uuid4())
        self.base64_size_bytes = base64_size_bytes
        self.width = width
        self.height = height
        base64 = str(uuid.uuid4())
        base64 += 'x' * (base64_size_bytes - len(base64))
        self.raw_base64 = base64
        self.base64 = f'data:image/jpg;base64,{base64}'

    def get_url_template(self, mockserver):
        return mockserver.url(f'/{self.group_id}/{self.name}/{{w}}x{{h}}.jpg')

    def get_url(self, mockserver):
        return mockserver.url(
            f'/{self.group_id}/{self.name}/{self.width}x{self.height}.jpg',
        )
