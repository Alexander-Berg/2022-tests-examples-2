import uuid

from aiohttp import web
from motor import motor_asyncio

ROUTES = web.RouteTableDef()


@ROUTES.post('/mongo/create')
async def post(request):
    doc = await request.json()
    if '_id' in doc:
        doc_id = doc['_id']
    else:
        doc_id = uuid.uuid4().hex
        doc['_id'] = doc_id
    collection = _mongo_collection(request)
    await collection.insert_one(doc)
    return web.json_response({'_id': doc_id})


@ROUTES.get('/mongo/{id}')
async def get(request):
    doc_id = request.match_info['id']
    collection = _mongo_collection(request)
    doc = await collection.find_one({'_id': doc_id})
    if doc is None:
        return web.Response(status=404, reason='Foo not found')
    return web.json_response(doc)


def _mongo_collection(request) -> motor_asyncio.AsyncIOMotorCollection:
    return request.app['mongo_collection']
