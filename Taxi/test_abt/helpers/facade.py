import json

from abt.utils import postgres as pg_utils


class BasePgFacade:
    p_key: str = 'id'
    table_name: str

    def __init__(self, context):
        self.postgres = context.pg

    async def fetch_by_query(self, query, *args):
        records = await pg_utils.fetch(self.postgres.master_pool, query, args)
        return [dict(record) for record in records]

    async def fetchone_by_query(self, query, *args):
        record = await pg_utils.fetchrow(
            self.postgres.master_pool, query, args,
        )
        return dict(record) if record else None

    async def all(self, order_by=None):
        order_by = order_by or self.p_key
        query = f"""
        SELECT * FROM abt.{self.table_name} ORDER BY {order_by}
        """
        return await self.fetch_by_query(query)

    async def by_ids(self, ids):
        query = f"""
        SELECT * FROM abt.{self.table_name}
        WHERE {self.p_key} = ANY($1)
        """
        return await self.fetch_by_query(query, ids)

    async def by_id(
            self, id,
    ):  # pylint: disable=redefined-builtin, invalid-name
        records = await self.by_ids([id])
        return records[0] if records else None

    async def add(self, *_, json_fields=None, **kwargs):
        assert kwargs, 'You can\'t add nothing'
        names, values, placeholders = [], [], []
        json_fields = json_fields or {}
        for i, (name, value) in enumerate(kwargs.items()):
            names.append(name)
            if name in json_fields:
                values.append(json.dumps(value))
                placeholders.append(f'${i + 1}::jsonb')
            else:
                values.append(value)
                placeholders.append(f'${i + 1}')
        query = f"""
        INSERT INTO abt.{self.table_name} (
            {','.join(names)}
        )
        VALUES (
            {','.join(placeholders)}
        )
        RETURNING *
        """
        return await self.fetchone_by_query(query, *values)

    async def count(self) -> int:
        query = f"""
        SELECT COUNT(*) FROM abt.{self.table_name}
        """
        return (await self.fetchone_by_query(query))['count']

    async def first(self, order_by=None):
        order_by = order_by or self.p_key
        query = f"""
        SELECT * FROM abt.{self.table_name} ORDER BY {order_by} LIMIT 1
        """

        record = await self.fetchone_by_query(query)

        assert record is not None, f'No records queried by: {query}'

        return record


class MetricsGroupsFacade(BasePgFacade):
    table_name = 'metrics_groups'


class PrecomputesTablesFacade(BasePgFacade):
    table_name = 'precomputes_tables'

    async def fetchone(
            self, id=None, yt_cluster=None, yt_path=None,
    ):  # pylint: disable=redefined-builtin, invalid-name
        if id is not None:
            where_clause = 'id = $1'
            args = [id]
        elif yt_cluster is not None and yt_path is not None:
            where_clause = 'yt_cluster = $1 AND yt_path = $2'
            args = [yt_cluster, yt_path]
        else:
            raise ValueError('Id or yt_cluster and yt_path required')
        query = f"""
        SELECT *
        FROM abt.{self.table_name}
        WHERE {where_clause}
        """
        return await self.fetchone_by_query(query, *args)

    async def fetchone_by_metrics_group_id(self, metrics_group_id):
        query = f"""
        SELECT pt.*
        FROM abt.{self.table_name} pt
        INNER JOIN abt.metrics_groups_precomputes_tables mgpt
            ON pt.id = mgpt.precomputes_tables_id
        WHERE mgpt.metrics_groups_id = $1
        """
        return await self.fetchone_by_query(query, metrics_group_id)


class ExperimentsFacade(BasePgFacade):
    table_name = 'experiments'

    async def fetchone_by_name(self, name):
        query = f"""
        SELECT * FROM abt.{self.table_name}
        WHERE name = $1
        """
        return await self.fetchone_by_query(query, name)


class RevisionsFacade(BasePgFacade):
    p_key = 'revision_id'
    table_name = 'revisions'


class RevisionsGroupsFacade(BasePgFacade):
    table_name = 'revisions_groups'


class MetricsGroupsPrecomputesTablesFacade(BasePgFacade):
    table_name = 'metrics_groups_precomputes_tables'


class PrecomputesTablesExperimentsFacade(BasePgFacade):
    table_name = 'precomputes_tables_experiments'


class FacetsFacade(BasePgFacade):
    table_name = 'facets'

    async def get_facets_with_revisions(self, precomputes_table_id: int):
        query = f"""
        SELECT * FROM abt.{self.table_name}
        WHERE precomputes_table_id = $1
        ORDER BY (revision_id, facet)
        """
        records = await self.fetch_by_query(query, precomputes_table_id)

        return [
            {'revision_id': record['revision_id'], 'facet': record['facet']}
            for record in records
        ]


class PgFacade:
    def __init__(self, env_context):
        self.metrics_groups = MetricsGroupsFacade(env_context)
        self.precomputes_tables = PrecomputesTablesFacade(env_context)
        self.experiments = ExperimentsFacade(env_context)
        self.revisions = RevisionsFacade(env_context)
        self.revisions_groups = RevisionsGroupsFacade(env_context)
        self.mg_pt = MetricsGroupsPrecomputesTablesFacade(env_context)
        self.pt_experiments = PrecomputesTablesExperimentsFacade(env_context)
        self.facets = FacetsFacade(env_context)
