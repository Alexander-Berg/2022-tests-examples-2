# pylint: disable=too-many-locals
import csv

from aiohttp import web
import bson

from taxi.clients import passport
from taxi.clients import support_chat

from chatterbox.internal import task_source


@passport.auth_required
async def import_chats(request) -> web.Response:
    data = await request.text()
    response_data = []
    lines = data.split('\n')
    csv_reader = csv.reader(lines, delimiter=';')
    for line in csv_reader:
        if len(line) == 9:
            (
                message,
                user_id,
                user_phone_id,
                order_id,
                order_alias_id,
                user_phone,
                driver_id,
                park_db_id,
                tags_string,
            ) = line
            tags = tags_string.split(',')
        elif len(line) == 8:
            (
                message,
                user_id,
                user_phone_id,
                order_id,
                order_alias_id,
                user_phone,
                driver_id,
                park_db_id,
            ) = line
            tags = []
        else:
            continue
        if user_phone_id == 'rand':
            user_phone_id = str(bson.ObjectId())
        source = request.app.task_source_manager.support_chat_source
        chat = await source.support_chat_client.create_chat(
            owner_id=user_phone_id,
            owner_role=support_chat.SENDER_ROLE_CLIENT,
            message_text=message,
            message_sender_id=user_phone_id,
            message_sender_role=support_chat.SENDER_ROLE_CLIENT,
        )
        task = await request.app.tasks_manager.create(
            task_type=task_source.TYPE_CHAT,
            chat_type=task_source.CHAT_TYPE_CLIENT,
            external_id=chat['id'],
        )
        meta_info = {
            'user_id': user_id,
            'order_id': order_id,
            'order_alias_id': order_alias_id,
            'user_phone_id': user_phone_id,
            'user_phone': user_phone,
            'driver_id': driver_id,
            'park_db_id': park_db_id,
        }
        task = await request.app.tasks_manager.update_meta(
            task=task,
            set_meta_fields=meta_info,
            add_tags=tags,
            predispatch=False,
        )
        await request.app.predispatcher.process_task(
            task=task, log_extra=request['log_extra'],
        )
        response_data.append(
            {'id': str(task['_id']), 'external_id': task['external_id']},
        )
    response = web.json_response(data=response_data)
    return response
