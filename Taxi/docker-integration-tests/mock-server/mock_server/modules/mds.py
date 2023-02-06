import collections
import logging

from aiohttp import web

logger = logging.getLogger()


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self._storage = collections.defaultdict(dict)

        self.router.add_put('/{bucket_name}/{object_name}', self.upload_data)
        self.router.add_get('/{bucket_name}/{object_name}', self.download_data)
        self.router.add_delete(
            '/{bucket_name}/{object_name}', self.object_delete,
        )

    async def upload_data(self, request):
        bucket_name = request.match_info['bucket_name']
        obj_name = request.match_info['object_name']
        logger.info(
            'put in mds - bucket: %s, object: %s', bucket_name, obj_name,
        )

        body = await request.read()

        self._storage[bucket_name][obj_name] = body

        return web.Response(status=200, headers={'ETag': ''})

    async def download_data(self, request):
        bucket_name = request.match_info['bucket_name']
        obj_name = request.match_info['object_name']
        logger.info(
            'get from mds - bucket: %s, object: %s', bucket_name, obj_name,
        )

        try:
            body = self._storage[bucket_name][obj_name]
        except KeyError:
            return web.Response(text='error', status=404, headers={'ETag': ''})

        response = web.StreamResponse(headers={'ETag': ''})
        response.enable_chunked_encoding()
        response.content_type = 'application/octet-stream'
        await response.prepare(request)
        await response.write(body)
        return response

    async def object_delete(self, request):
        bucket_name = request.match_info['bucket_name']
        obj_name = request.match_info['object_name']
        logger.info(
            'delete from mds - bucket: %s, object: %s', bucket_name, obj_name,
        )

        try:
            del self._storage[bucket_name][obj_name]
        except KeyError:
            return web.Response(
                text='Delete error - object not found', status=404,
            )
        else:
            return web.Response(status=204)
