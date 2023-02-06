import json

from supportai_tasks import models as db_models


def get_percent(numerator: int, denominator: int):
    return (100 * numerator) // denominator if denominator else 0


def prepare_topic_details(topic_details):
    topic_details_dict = json.loads(topic_details)
    new_topic_details = {
        key: {
            'v1': value.get('v1', 0),
            'v2': value.get('v2', 0),
            'IOU': get_percent(
                value['int_count'],
                value['v1'] + value['v2'] - value['int_count'],
            ),
        }
        for key, value in topic_details_dict.items()
    }
    return json.dumps(new_topic_details)


class Aggregation:
    def __init__(self, context, log_extra, task_id):
        self.context = context
        self.log_extra = log_extra
        self.task_id = task_id
        self.aggregation = None

    async def init_from_db(self):
        async with self.context.pg.master_pool.acquire(
                log_extra=self.log_extra,
        ) as conn:
            db_model = db_models.TestingAggregation
            aggregation = await db_model.select_by_task_id(
                context=self.context, db_conn=conn, task_id=self.task_id,
            )

            if aggregation is not None:
                self.aggregation = aggregation
            else:
                self.aggregation = await db_model.insert(
                    context=self.context, db_conn=conn, task_id=self.task_id,
                )

    async def save_testing_aggregation(self):
        async with self.context.pg.master_pool.acquire(
                log_extra=self.log_extra,
        ) as conn:
            db_model = db_models.TestingAggregation
            await db_model.update(
                context=self.context,
                db_conn=conn,
                aggregation=self.aggregation,
            )

    def _set_topic_details(self, sure, v1_add, v2_add, int_add):
        topic_details = json.loads(self.aggregation.topic_details)
        topic_dict = topic_details.get(sure, {})
        new_dict = {
            'v1': topic_dict.get('v1', 0) + v1_add,
            'v2': topic_dict.get('v2', 0) + v2_add,
            'int_count': topic_dict.get('int_count', 0) + int_add,
        }
        topic_details[sure] = new_dict
        self.aggregation.topic_details = json.dumps(topic_details)

    def add_aggregation(
            self,
            response_v1,
            response_v2,
            response_history,
            chat_mark,
            is_equal,
    ):
        sure_v1 = (
            response_v1.features.sure_topic if response_v1.features else None
        )
        sure_v2 = (
            response_v2.features.sure_topic if response_v2.features else None
        )
        sure_history = (
            response_history.features.sure_topic
            if response_history.features
            else None
        )

        if chat_mark == 'ok':
            if sure_v1 == sure_history:
                self.aggregation.topic_ok_count_v1 += 1
            if sure_v1 == sure_history:
                self.aggregation.topic_ok_count_v2 += 1
            self.aggregation.ok_chat_count += 1

        self.aggregation.chat_count += 1
        self.aggregation.equal_count += int(is_equal)

        if response_v1.reply:
            self.aggregation.reply_count_v1 += 1
        if response_v2.reply:
            self.aggregation.reply_count_v2 += 1

        if response_v1.close:
            self.aggregation.close_count_v1 += 1
        if response_v2.close:
            self.aggregation.close_count_v2 += 1

        if response_v1.reply or response_v1.close:
            self.aggregation.reply_or_close_count_v1 += 1
        if response_v1.reply or response_v1.close:
            self.aggregation.reply_or_close_count_v2 += 1

        if sure_v1 is not None and sure_v1 == sure_v2:
            self._set_topic_details(
                sure=sure_v1, v1_add=1, v2_add=1, int_add=1,
            )
        else:
            if sure_v1 is not None:
                self._set_topic_details(
                    sure=sure_v1, v1_add=1, v2_add=0, int_add=0,
                )
            if sure_v2 is not None:
                self._set_topic_details(
                    sure=sure_v2, v1_add=0, v2_add=1, int_add=0,
                )
