import datetime
import typing

from feeds_admin import models
from test_feeds_admin import const


GroupType = models.recipients.GroupType


def create_fake_feed(
        target_service: str,
        name: str = 'test',
        payload: typing.Optional[typing.Dict[str, typing.Any]] = None,
        settings: typing.Optional[typing.Dict[str, typing.Any]] = None,
) -> models.feed.Feed:
    return models.feed.Feed(
        feed_id=const.UUID_1,
        target_service=target_service,
        name=name,
        ticket='T-1000',
        status=models.feed.Feed.Status.CREATED,
        payload=payload or {},
        settings=settings or {},
        author='test',
        created=datetime.datetime.now(),
        updated=datetime.datetime.now(),
    )


def create_fake_recipients_group(
        group_type: GroupType = GroupType.CHANNELS,
        group_settings: typing.Optional[typing.Dict[str, typing.Any]] = None,
        recipient_ids: typing.Optional[typing.List[str]] = None,
        yql_link: typing.Optional[str] = None,
) -> models.recipients.RecipientsGroup:
    return models.recipients.RecipientsGroup(
        group_id=None,
        group_type=group_type,
        group_settings=group_settings or {},
        recipient_ids=recipient_ids,
        yql_link=yql_link,
    )


def create_fake_run() -> models.run_history.Run:
    return models.run_history.Run(
        run_id=0,
        feed_id=const.UUID_1,
        recipient_count=None,
        start_at=None,
        planned_start_at=datetime.datetime.now(),
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
        finished_at=None,
        status=models.run_history.Status.PLANNED,
    )


def create_fake_publication(
        target_service: str,
) -> models.publication.Publication:
    return models.publication.Publication(
        feed=create_fake_feed(target_service),
        run=create_fake_run(),
        schedule=models.schedule.Interval(
            start_at=datetime.datetime.now(),
            finish_at=datetime.datetime.now(),
        ),
        recipients_groups=[create_fake_recipients_group()],
    )
