from datetime import datetime
import uuid

from mouse import Has

from libstall.model import coerces
from libstall.model.storable import Table  # pylint: disable=unused-import
from libstall.model.storable.pg import Pg
from libstall.model.storable.sharded import ShardedPg
from libstall.model.vars import Vars

from . import shard_schema


class PgRecord(Pg, table=Table('tests', pkey='test_id')):
    database = 'tlibstall'

    test_id      = Has(
        types=str,
        required=True,
        default=lambda: uuid.uuid4().hex,
    )
    value        = Has(types=str, required=False, default='hello')
    group        = Has(types=str, required=False)
    lsn          = Has(types=int, required=False, tags='db_default')
    serial       = Has(types=int, required=False, tags='db_default')
    created      = Has(
        types=datetime,
        required=False,
        coerce=coerces.date_time,
        tags='db_default'
    )


class ShardedRecord(ShardedPg, table=Table('tests', pkey='test_id')):
    database = 'tlibstall'
    test_id      = Has(types=str, required=False)
    value        = Has(types=str, required=False, default='hello')
    second_value = Has(types=str, required=False)
    group        = Has(types=str, required=False)
    lsn          = Has(types=int, required=False, tags='db_default')
    serial       = Has(types=int, required=False, tags='db_default')
    created      = Has(
        types=datetime,
        required=False,
        coerce=coerces.date_time,
        tags='db_default'
    )

    shard_module = shard_schema


class VarsRecord(ShardedPg, table=Table('tstvars', pkey='id')):
    database = 'tlibstall'

    id          = Has(types=str, required=False)
    vars        = Has(types=Vars,
                      coerce=Vars.coerce,
                      required=True,
                      tags='db_vars',
                      always_coerce=True,
                      default=lambda: {})

    shard_module = shard_schema


class ShardedRecordSerial(ShardedPg, table=Table('tests', pkey='serial')):
    database = 'tlibstall'
    test_id      = Has(types=str, required=False)
    value        = Has(types=str, required=False, default='hello')
    lsn          = Has(types=int, required=False, tags='db_default')
    serial       = Has(types=int, required=False, tags='db_default')
    created      = Has(
        types=datetime,
        required=False,
        coerce=coerces.date_time,
        tags='db_default'
    )

    shard_module = shard_schema
