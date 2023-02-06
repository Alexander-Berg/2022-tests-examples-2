import inspect
import os

import bson.json_util

import patterns


async def fill_db(object_type, create_json, mongo):
    get_json = await mongo.patterns.find(
        {'_id': bson.ObjectId(create_json['id'])},
    ).to_list(None)
    f_out_paths = [
        os.path.join(
            os.path.dirname(os.path.dirname(inspect.getfile(patterns))),
            'test_patterns',
            'web',
            'static',
            f'test_get_{object_type}',
            'db_patterns.json',
        ),
        os.path.join(
            os.path.dirname(os.path.dirname(inspect.getfile(patterns))),
            'test_patterns',
            'web',
            'static',
            f'test_edit_{object_type}',
            'db_patterns.json',
        ),
        os.path.join(
            os.path.dirname(os.path.dirname(inspect.getfile(patterns))),
            'test_patterns',
            'web',
            'static',
            f'test_validate_{object_type}',
            'db_patterns.json',
        ),
    ]
    for f_out_path in f_out_paths:
        if os.path.exists(f_out_path):
            continue
        with open(f_out_path, 'w') as f_out:
            f_out.write(bson.json_util.dumps(get_json, indent=4))
