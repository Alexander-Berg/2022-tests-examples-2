import copy
import dataclasses
import datetime
import json
from typing import Dict
from typing import List
from typing import Optional

from tests_grocery_goals import common

SELECT_GOAL_BY_ID_SQL = """
    SELECT goal_id, name,
        title,
        icon_link,
        goal_page_icon_link,
        legal_text,
        progress_bar_color,
        catalog_text,
        group_text,
        catalog_link,
        catalog_picture_link,
        created,
        updated,
        starts,
        expires,
        goal_type,
        goal_args,
        goal_reward,
        goal_alt_reward,
        status,
        marketing_tags,
        finish_push_title,
        finish_push_message
    FROM grocery_goals.goals WHERE goal_id=%s
"""

INSERT_GOAL = """
    INSERT INTO grocery_goals.goals (
        goal_id,
        name,
        title,
        icon_link,
        goal_page_icon_link,
        legal_text,
        progress_bar_color,
        catalog_text,
        group_text,
        catalog_link,
        catalog_picture_link,
        display_info,
        created,
        updated,
        starts,
        expires,
        goal_type,
        goal_args,
        goal_reward,
        goal_alt_reward,
        status,
        marketing_tags,
        finish_push_title,
        finish_push_message
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
     %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb[], %s, %s, %s, %s)
"""

SELECT_GOAL_PROGRESS = """
    SELECT
        goal_progress_id,
        yandex_uid,
        goal_id,
        progress,
        progress_status,
        new_seen,
        completed_seen,
        reward,
        completed_push_time,
        complete_at,
        reward_used_at,
        reward_swap_at,
        reward_reserved_by
    FROM grocery_goals.goal_progress WHERE yandex_uid=%s AND goal_id=%s
"""

INSERT_GOAL_PROGRESS = """
    INSERT INTO grocery_goals.goal_progress
    (yandex_uid, goal_id, progress, progress_status, new_seen, completed_seen,
     reward, complete_at, reward_used_at, reward_swap_at, reward_reserved_by)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


class GoalRewardPromocode:
    def __init__(self):
        self.promocode_series = common.GOAL_REWARD_PROMOCODE['extra'][
            'promocode_series'
        ]
        self.promocode = None
        self.promocode_value = 500
        self.promocode_type = 'fixed'
        self.currency_sign = '₽'
        self.orders_count = 2

    def get_reward_info(self):
        promocode_field = (
            {} if self.promocode is None else {'promocode': self.promocode}
        )

        return {
            'type': common.GOAL_REWARD_PROMOCODE_TYPE,
            'extra': {
                'value_text': (
                    '-$SIGN$' + str(self.promocode_value) + '$CURRENCY$'
                ),
                'promocode_type': self.promocode_type,
                'currency_sign': self.currency_sign,
                'orders_count_text': str(self.orders_count),
                'orders_count': self.orders_count,
                **promocode_field,
            },
        }

    def get_reward_db_info(self):
        return {
            'type': common.GOAL_REWARD_PROMOCODE_TYPE,
            'extra': {'promocode_series': self.promocode_series},
        }


class GoalRewardSku:
    def __init__(self):
        self.skus = common.DEFAULT_SKUS
        self.sku_image_url_template = 'some_url'

    def get_reward_info(self):
        skus = list(
            map(
                lambda x: {
                    'id': x,
                    'picture_link': self.sku_image_url_template,
                },
                self.skus,
            ),
        )
        return {'type': common.GOAL_REWARD_SKU_TYPE, 'extra': {'skus': skus}}

    def get_user_reward_db_info(self):
        return {'sku': self.skus[0]}

    def get_reward_db_info(self):
        return {
            'type': common.GOAL_REWARD_SKU_TYPE,
            'extra': {'skus': self.skus},
        }


class GoalRewardExternalVendor:
    def __init__(self):
        self.text = common.EXTERNAL_VENDOR_TEXT
        self.picture_link = common.EXTERNAL_VENDOR_PICTURE_LINK
        self.completed_text = common.EXTERNAL_VENDOR_COMPLETED_TEXT
        self.more_info = common.EXTERNAL_VENDOR_MORE_INFO

    def get_reward_info(self):
        return {
            'type': common.GOAL_REWARD_EXTERNAL_VENDOR_TYPE,
            'extra': {
                'text': self.text,
                'picture_link': self.picture_link,
                'completed_text': self.completed_text,
                'more_info': self.more_info,
            },
        }

    def get_reward_db_info(self):
        return {
            'type': common.GOAL_REWARD_EXTERNAL_VENDOR_TYPE,
            'extra': {
                'text': self.text,
                'picture_link': self.picture_link,
                'completed_text': self.completed_text,
                'more_info': self.more_info,
            },
        }


@dataclasses.dataclass
class Goal:
    goal_id: int
    name: str
    title: str
    icon_link: str
    goal_page_icon_link: Optional[str]
    legal_text: str
    progress_bar_color: Optional[str]
    catalog_text: Optional[str]
    group_text: Optional[str]
    catalog_link: Optional[str]
    catalog_picture_link: Optional[str]
    created: datetime.datetime
    updated: datetime.datetime
    starts: datetime.datetime
    expires: datetime.datetime
    goal_type: str
    goal_args: Dict
    goal_reward: Dict
    goal_alt_reward: List[Dict]
    status: str
    marketing_tags: List[str]
    finish_push_title: str
    finish_push_message: str


@dataclasses.dataclass
class GoalProgress:
    goal_progress_id: int
    yandex_uid: str
    goal_id: int
    progress: Dict
    progress_status: str
    new_seen: bool
    completed_seen: bool
    reward: Dict
    completed_push_time: datetime.datetime
    complete_at: datetime.datetime
    reward_used_at: datetime.datetime
    reward_swap_at: datetime.datetime
    reward_reserved_by: Optional[str]


def get_goal_by_id(pgsql, goal_id):
    cursor = pgsql['grocery_goals'].cursor()
    cursor.execute(SELECT_GOAL_BY_ID_SQL, [goal_id])
    result_goals = cursor.fetchone()
    return Goal(
        result_goals[0],
        result_goals[1],
        result_goals[2],
        result_goals[3],
        result_goals[4],
        result_goals[5],
        result_goals[6],
        result_goals[7],
        result_goals[8],
        result_goals[9],
        result_goals[10],
        result_goals[11],
        result_goals[12],
        result_goals[13],
        result_goals[14],
        result_goals[15],
        result_goals[16],
        result_goals[17],
        result_goals[18],
        result_goals[19],
        result_goals[20],
        result_goals[21],
        result_goals[22],
    )


def insert_goal(
        pgsql,
        goal_id=common.GOAL_ID,
        name=common.GOAL_NAME,
        display_info=copy.deepcopy(common.GOAL_DISPLAY_INFO),
        title=common.GOAL_TITLE,
        icon_link=common.GOAL_ICON_LINK,
        goal_page_icon_link=common.GOAL_PAGE_ICON_LINK,
        legal_text=common.GOAL_LEGAL_TEXT,
        progress_bar_color=common.PROGRESS_BAR_COLOR,
        catalog_text=common.CATALOG_TEXT,
        group_text=common.GROUP_TEXT,
        catalog_link=common.CATALOG_LINK,
        catalog_picture_link=common.CATALOG_PICTURE_LINK,
        created=common.GOAL_CREATED,
        updated=common.GOAL_UPDATED,
        starts=common.GOAL_STARTS,
        expires=common.GOAL_EXPIRES,
        goal_type=common.ORDERS_COUNT_GOAL_TYPE,
        goal_args=copy.deepcopy(common.GOAL_ORDER_COUNT_ARGS),
        goal_reward=copy.deepcopy(common.GOAL_REWARD_PROMOCODE),
        goal_alt_reward=None,
        status=common.GOAL_STATUS,
        marketing_tags=copy.deepcopy(common.GOAL_MARKETING_TAGS),
        finish_push_title=copy.deepcopy(
            common.GOAL_PUSH_INFO['finish_title_tanker_key'],
        ),
        finish_push_message=copy.deepcopy(
            common.GOAL_PUSH_INFO['finish_message_tanker_key'],
        ),
):
    cursor = pgsql['grocery_goals'].cursor()
    cursor.execute(
        INSERT_GOAL,
        [
            goal_id,
            name,
            title,
            icon_link,
            goal_page_icon_link,
            legal_text,
            progress_bar_color,
            catalog_text,
            group_text,
            catalog_link,
            catalog_picture_link,
            json.dumps(display_info),
            created,
            updated,
            starts,
            expires,
            goal_type,
            json.dumps(goal_args),
            json.dumps(goal_reward),
            [] if goal_alt_reward is None else [json.dumps(goal_alt_reward)],
            status,
            marketing_tags,
            finish_push_title,
            finish_push_message,
        ],
    )


def get_goal_progress(pgsql, yandex_uid, goal_id):
    cursor = pgsql['grocery_goals'].cursor()
    cursor.execute(SELECT_GOAL_PROGRESS, [yandex_uid, goal_id])
    result_goals = cursor.fetchone()
    if not result_goals:
        return None
    return GoalProgress(
        result_goals[0],
        result_goals[1],
        result_goals[2],
        result_goals[3],
        result_goals[4],
        result_goals[5],
        result_goals[6],
        result_goals[7],
        result_goals[8],
        result_goals[9],
        result_goals[10],
        result_goals[11],
        result_goals[12],
    )


def insert_goal_progress(
        pgsql,
        yandex_uid=common.YANDEX_UID,
        goal_id=common.GOAL_ID,
        progress=copy.deepcopy(common.GOAL_PROGRESS_PROGRESS),
        progress_status=common.GOAL_PROGRESS_STATUS,
        new_seen=False,
        completed_seen=False,
        reward=None,
        complete_at=None,
        reward_used_at=None,
        reward_swap_at=None,
        reward_reserved_by=None,
):
    cursor = pgsql['grocery_goals'].cursor()
    cursor.execute(
        INSERT_GOAL_PROGRESS,
        [
            yandex_uid,
            goal_id,
            json.dumps(progress),
            progress_status,
            new_seen,
            completed_seen,
            json.dumps(reward) if reward else None,
            complete_at,
            reward_used_at,
            reward_swap_at,
            reward_reserved_by,
        ],
    )
