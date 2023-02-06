import typing

import asyncpg
import pytest

from taxi_exp.util import pg_helpers
from test_taxi_exp.helpers import db


def get_args(typename: typing.Any) -> str:
    return ','.join(typename.__annotations__.keys())


class DeleteCase(typing.NamedTuple):
    comment: str
    exception_text: typing.Optional[str]  # noqa
    mds_id: str
    last_version: int


class AddCase(typing.NamedTuple):
    comment: str
    exception_text: typing.Optional[str]  # noqa
    name: str


class UpdateCase(typing.NamedTuple):
    comment: str
    parent_name: str
    exception_text: typing.Optional[str]  # noqa


class TypedFileCase(typing.NamedTuple):
    file_type: typing.Optional[str]  # noqa
    expected_file_type: str
    is_raise: bool


@pytest.mark.parametrize(
    get_args(DeleteCase),
    [
        DeleteCase(
            comment='dont_remove_child',
            exception_text=(
                'conflict: this operation allows to parent file only'
            ),
            mds_id='2cccccc',
            last_version=3,
        ),
        DeleteCase(
            comment='dont_remove_if_file_used_in_experiment',
            exception_text='conflict: file 4eeeeee are used in 1 experiments',
            mds_id='4eeeeee',
            last_version=1,
        ),
        DeleteCase(
            comment='success_remove_file_with_history',
            exception_text=None,
            mds_id='74807b81b2a9474a931b8eb968e0f838',
            last_version=3,
        ),
        DeleteCase(
            comment='success_remove_file_without_history',
            exception_text=None,
            mds_id='5ffffff',
            last_version=1,
        ),
        DeleteCase(
            comment='dont_remove_if_child_used_in_experiment',
            exception_text=(
                'conflict: file 231b3a60e38b47d0ab1e4fb42e4a4de1 '
                'or it`s versions are used in 1 experiments'
            ),
            mds_id='231b3a60e38b47d0ab1e4fb42e4a4de1',
            last_version=3,
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('files.sql',))
async def test_remove_file(
        comment, exception_text, mds_id, last_version, taxi_exp_client,
):
    taxi_exp_app = taxi_exp_client.app
    try:
        await db.delete_file(taxi_exp_app, mds_id, last_version)
    except pg_helpers.DatabaseError as exc:
        assert str(exc) == exception_text


@pytest.mark.parametrize(
    get_args(AddCase),
    [
        AddCase(
            comment='fail_if_name_is_non_unique',
            exception_text=(
                'duplicate key value violates unique constraint '
                '"file_name_constraint"\nDETAIL:  '
                'Key (name)=(existing_name) already exists.'
            ),
            name='existing_name',
        ),
        AddCase(
            comment='success', exception_text=None, name='non_existing_name',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('files.sql',))
async def test_adding_new_file(comment, exception_text, name, taxi_exp_client):
    taxi_exp_app = taxi_exp_client.app
    try:
        await db.add_or_update_file(taxi_exp_app, name)
    except pg_helpers.DatabaseError as exc:
        assert str(exc) == exception_text


@pytest.mark.parametrize(
    get_args(UpdateCase),
    [UpdateCase(comment='success', parent_name='f11', exception_text=None)],
)
@pytest.mark.pgsql('taxi_exp', files=('files.sql',))
async def test_update_file(
        comment, parent_name, exception_text, taxi_exp_client,
):
    taxi_exp_app = taxi_exp_client.app
    try:
        await db.add_or_update_file(taxi_exp_app, parent_name)
    except pg_helpers.DatabaseError as exc:
        assert str(exc) == exception_text


@pytest.mark.parametrize(
    get_args(TypedFileCase),
    [
        TypedFileCase(
            file_type='string', expected_file_type='string', is_raise=False,
        ),
        TypedFileCase(
            file_type=None, expected_file_type='string', is_raise=True,
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('files.sql',))
async def test_types(file_type, expected_file_type, is_raise, taxi_exp_client):
    taxi_exp_app = taxi_exp_client.app
    if is_raise:
        with pytest.raises(asyncpg.exceptions.NotNullViolationError):
            await db.add_or_update_file(
                taxi_exp_app, 'file_123', file_type=file_type,
            )
    else:
        file_id = await db.add_or_update_file(
            taxi_exp_app, 'file_123', file_type=file_type,
        )

        file = await db.get_file(taxi_exp_app, file_id)

        assert file['file_type'] == expected_file_type
