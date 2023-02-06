import dataclasses
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple


def make_geography_insert_query(
        work_mode: str, geo_nodes: List[Tuple[str, bool]],
):
    select_mode_query = (
        f'(SELECT id FROM config.modes WHERE name = \'{work_mode}\')'
    )
    values = [
        f'(\'{node[0]}\', {select_mode_query}, {str(node[1]).lower()})'
        for node in geo_nodes
    ]
    return f"""
    INSERT INTO config.mode_geography (geo_node, mode_id, is_enabled)
     VALUES {','.join(values)}
    """


@dataclasses.dataclass
class ModeGeographyExperiment:
    name: str
    is_enabled: bool


def make_experiments_insert_query(
        work_mode: str,
        geo_node: str,
        experiments: List[ModeGeographyExperiment],
):
    select_mode_query = (
        f'(SELECT id FROM config.modes WHERE name = \'{work_mode}\')'
    )
    select_geography_rule_query = f"""(SELECT id FROM config.mode_geography
        WHERE mode_id = {select_mode_query}
        AND geo_node = \'{geo_node}\')
        """
    values = [
        f"""({select_geography_rule_query}, \'{experiment.name}\',
         {experiment.is_enabled})"""
        for experiment in experiments
    ]
    return f"""
    INSERT INTO config.mode_geography_experiments
     (mode_geography_id, name, is_enabled)
     VALUES {','.join(values)}
    """


@dataclasses.dataclass
class ModeGeographyConfiguration:
    work_mode: str
    geo_node: str
    is_enabled: bool
    experiments: Optional[List[ModeGeographyExperiment]] = None


def insert_mode_geography(rules: List[ModeGeographyConfiguration], pgsql):
    cursor = pgsql['driver_mode_subscription'].cursor()
    for rule in rules:
        cursor.execute(
            make_geography_insert_query(
                rule.work_mode, [(rule.geo_node, rule.is_enabled)],
            ),
        )
        if rule.experiments:
            cursor.execute(
                make_experiments_insert_query(
                    rule.work_mode, rule.geo_node, rule.experiments,
                ),
            )


def fetch_geography_rules(pgsql):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        """
        SELECT mode_geography.id,
               modes.name,
               mode_geography.geo_node,
               mode_geography.is_enabled,
               mode_geography_experiments.name,
               mode_geography_experiments.is_enabled
        FROM config.mode_geography
                INNER JOIN config.modes
                           ON config.modes.id =
                              config.mode_geography.mode_id
                LEFT JOIN config.mode_geography_experiments
                          ON mode_geography_experiments.mode_geography_id =
                             mode_geography.id

        """,
    )
    configurations: Dict[int, ModeGeographyConfiguration] = {}
    for row in cursor:
        config = configurations.setdefault(
            row[0], ModeGeographyConfiguration(row[1], row[2], row[3]),
        )
        if row[4] is not None and row[5] is not None:
            if not config.experiments:
                config.experiments = []
            config.experiments.append(ModeGeographyExperiment(row[4], row[5]))

    res = sorted(
        configurations.values(),
        key=lambda item: (item.work_mode, item.geo_node),
    )
    for item in res:
        if item.experiments:
            item.experiments.sort(key=lambda exp: exp.name)
    return res
