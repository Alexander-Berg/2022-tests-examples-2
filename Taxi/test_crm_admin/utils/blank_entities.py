import datetime

from crm_admin import entity
from crm_admin.generated.service.swagger import models


def get_blank_segment() -> entity.CampaignSegment:
    result = entity.CampaignSegment(
        segment_id=1,
        yql_shared_url='',
        yt_table='',
        extra_columns=[],
        aggregate_info=None,
        control=1.2,
        mode=None,
        created_at=datetime.datetime(2000, 1, 1),
        updated_at=None,
        deleted_at=None,
    )
    return result


def get_blank_group() -> entity.UserGroup:
    result = entity.UserGroup(
        group_id=1,
        segment_id=1,
        yql_shared_url=None,
        params=models.api.ShareGroup(name='name', share=10.1),
        sending_stats=models.api.SendingStats(),
        created_at=datetime.datetime(2000, 1, 1),
    )
    return result
