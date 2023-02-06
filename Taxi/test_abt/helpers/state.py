import datetime
import typing as tp

import asyncpg
import yaml

from test_abt import consts


DTIME = datetime.datetime


class StateHelper:
    def __init__(self, pg_facades, builders):
        self.pg = pg_facades  # pylint: disable=invalid-name
        self.builders = builders

        self.last_added_experiment = None
        self.last_added_revision = None
        self.last_added_revision_group = None
        self.last_added_metrics_group = None
        self.last_added_precomputes_table = None

    async def add_metrics_group(
            self,
            title: str = consts.DEFAULT_METRICS_GROUP_TITLE,
            description: str = consts.DEFAULT_METRICS_GROUP_DESCRIPTION,
            owners: tp.Optional[tp.List[str]] = None,
            scopes: tp.Optional[tp.List[str]] = None,
            is_collapsed: bool = consts.DEFAULT_METRICS_GROUP_IS_COLLAPSED,
            enabled: bool = consts.DEFAULT_METRICS_GROUP_ENABLED,
            config: tp.Optional[dict] = None,
            position: int = consts.DEFAULT_METRICS_GROUP_POSITION,
            updated_at: tp.Optional[datetime.datetime] = None,
            created_at: tp.Optional[datetime.datetime] = None,
    ) -> asyncpg.Record:
        owners = (
            consts.DEFAULT_METRIC_GROUP_OWNERS if owners is None else owners
        )
        scopes = (
            consts.DEFAULT_METRIC_GROUP_SCOPES if scopes is None else scopes
        )
        config = (
            self.builders.get_mg_config_builder()
            .add_value_metric()
            .add_precomputes()
            .build()
            if config is None
            else config
        )

        kwargs = {
            'title': title,
            'description': description,
            'owners': owners,
            'scopes': scopes,
            'is_collapsed': is_collapsed,
            'enabled': enabled,
            'config_source': yaml.dump(config),
            'position': position,
        }

        if updated_at:
            kwargs['updated_at'] = updated_at

        if created_at:
            kwargs['created_at'] = created_at

        self.last_added_metrics_group = await self.pg.metrics_groups.add(
            **kwargs,
        )

        return self.last_added_metrics_group

    async def add_precomputes_table(
            self,
            yt_cluster: str = consts.DEFAULT_YT_CLUSTER,
            yt_path: str = consts.DEFAULT_YT_PATH,
            schema: tp.Optional[dict] = None,
            attributes: tp.Optional[dict] = None,
            facets: tp.Optional[dict] = None,
            updated_at: tp.Optional[datetime.datetime] = None,
            created_at: tp.Optional[datetime.datetime] = None,
            indexed_at: tp.Optional[datetime.datetime] = None,
    ) -> asyncpg.Record:
        schema = (
            self.builders.get_pt_schema_builder().build()
            if schema is None
            else schema
        )
        attributes = (
            self.builders.get_pt_attributes_builder().build()
            if attributes is None
            else attributes
        )
        facets = (
            self.builders.get_facets_builder().build()
            if facets is None
            else facets
        )

        kwargs = {
            'yt_cluster': yt_cluster,
            'yt_path': yt_path,
            'schema': schema,
            'attributes': attributes,
            'facets': facets,
        }

        if updated_at:
            kwargs['updated_at'] = updated_at

        if created_at:
            kwargs['created_at'] = created_at

        if indexed_at:
            kwargs['indexed_at'] = indexed_at

        self.last_added_precomputes_table = (
            await self.pg.precomputes_tables.add(
                json_fields=['schema', 'attributes', 'facets'], **kwargs,
            )
        )

        return self.last_added_precomputes_table

    async def bind_mg_with_pt(
            self, metrics_group_id: int, precomputes_table_id: int,
    ) -> None:
        await self.pg.mg_pt.add(
            metrics_groups_id=metrics_group_id,
            precomputes_tables_id=precomputes_table_id,
        )

    async def add_experiment(
            self,
            name: tp.Optional[str] = None,
            experiment_type: tp.Optional[str] = None,
            description: tp.Optional[str] = None,
    ) -> asyncpg.Record:
        name = consts.DEFAULT_EXPERIMENT_NAME if name is None else name
        experiment_type = (
            consts.DEFAULT_EXPERIMENT_TYPE
            if experiment_type is None
            else experiment_type
        )
        description = (
            consts.DEFAULT_EXPERIMENT_DESCRIPTION
            if description is None
            else description
        )
        self.last_added_experiment = await self.pg.experiments.add(
            name=name, type=experiment_type, description=description,
        )
        return self.last_added_experiment

    async def bind_pt_with_experiment(
            self, precomputes_table_id: int, experiment_id: int,
    ) -> None:
        await self.pg.pt_experiments.add(
            precomputes_table_id=precomputes_table_id,
            experiment_id=experiment_id,
        )

    async def add_revision(
            self,
            revision_id: int = consts.DEFAULT_REVISION_ID,
            experiment_id: tp.Optional[int] = None,
            started_at: DTIME = consts.DEFAULT_REVISION_STARTED_AT,
            ended_at: tp.Optional[DTIME] = consts.DEFAULT_REVISION_ENDED_AT,
            data_available_days: tp.Optional[tp.List[str]] = None,
            business_revision_id: tp.Optional[int] = None,
            business_min_version_id: tp.Optional[int] = None,
            business_max_version_id: tp.Optional[int] = None,
    ) -> asyncpg.Record:
        if experiment_id is None:
            assert (
                self.last_added_experiment is not None
            ), 'Add experiment first or specify experiment_id explicitly'
            experiment_id = self.last_added_experiment['id']
        data_available_days = (
            data_available_days
            if data_available_days is not None
            else consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS
        )
        self.last_added_revision = await self.pg.revisions.add(
            revision_id=revision_id,
            experiment_id=experiment_id,
            started_at=started_at,
            ended_at=ended_at,
            data_available_days=data_available_days,
            business_revision_id=business_revision_id,
            business_min_version_id=business_min_version_id,
            business_max_version_id=business_max_version_id,
        )
        return self.last_added_revision

    async def add_revision_group(
            self,
            revision_id: tp.Optional[int] = None,
            group_id: int = consts.DEFAULT_REVISION_GROUP_ID,
            title: str = consts.DEFAULT_REVISION_GROUP_TITLE,
    ) -> asyncpg.Record:
        if revision_id is None:
            assert (
                self.last_added_revision is not None
            ), 'Add revision first or specify revision_id explicitly'
            revision_id = self.last_added_revision['revision_id']
        self.last_added_revision_group = await self.pg.revisions_groups.add(
            revision_id=revision_id, group_id=group_id, title=title,
        )
        return self.last_added_revision_group

    async def add_facets(
            self,
            facets: tp.Union[tp.List[str], str],
            precomputes_table_id: tp.Optional[int] = None,
            revision_id: tp.Optional[int] = None,
    ) -> None:
        if precomputes_table_id is None:
            assert self.last_added_precomputes_table is not None, (
                'Add precomputes table first or specify precomputes_table_id'
                ' explicitly'
            )
            precomputes_table_id = self.last_added_precomputes_table['id']
        if revision_id is None:
            assert (
                self.last_added_revision is not None
            ), 'Add revision first or specify revision_id explicitly'
            revision_id = self.last_added_revision['revision_id']
        if isinstance(facets, str):
            facets = [facets]

        for facet in facets:
            await self.pg.facets.add(
                precomputes_table_id=precomputes_table_id,
                revision_id=revision_id,
                facet=facet,
            )
