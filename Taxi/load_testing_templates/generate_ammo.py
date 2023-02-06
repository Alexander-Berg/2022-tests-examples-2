import json
import uuid

with open('queue.ammo', 'a') as file:
    for i in range(0, 600):
        file.write('231 /queue\r\n')
        json_data = {
            'task_id': uuid.uuid4().hex,
            'queue_name': 'eats_order_integration_send_order',
            'args': [],
            'kwargs': {
                'order_id': 'order_id',
                'idempotency_key': '123456',
                'sync': True,
            },
            'eta': '2021-09-30T09:33:23.886987+0000',
        }
        file.write(json.dumps(json_data))
        file.write('\r\n')
