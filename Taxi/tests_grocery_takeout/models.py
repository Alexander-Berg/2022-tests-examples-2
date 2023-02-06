import dataclasses
import datetime
from typing import List
from typing import Optional

from . import consts


class EntityRelation:
    direct = 'direct'
    indirect = 'indirect'

    values = (direct, indirect)


class JobType:
    load = 'load'
    delete = 'delete'

    values = (load, delete)


class JobStatus:
    init = 'init'
    done = 'done'

    values = (init, done)


class JobTaskStatus:
    init = 'init'
    done = 'done'

    values = (init, done)


class DeleteStatus:
    init = 'init'
    done = 'done'

    values = (init, done)


class JobMetricStatus:
    requested = 'requested'
    started = 'started'
    done = 'done'


@dataclasses.dataclass
class EntityNode:
    entity_type: str
    id_name: str = consts.ENTITY_ID_NAME
    settings_name: Optional[str] = None
    relation: Optional[str] = None
    children: List['EntityNode'] = dataclasses.field(default_factory=list)
    delete_after: Optional[list] = None

    def serialize(self) -> dict:
        return {
            'entity_type': self.entity_type,
            'id_name': self.id_name,
            'settings_name': self.settings_name,
            'relation': self.relation,
            'children': [
                it.serialize() for it in self.children  # pylint: disable=E1133
            ],
            'delete_after': self.delete_after,
        }

    @staticmethod
    def parse(value: dict):
        return EntityNode(
            entity_type=value['entity_type'],
            id_name=value['id_name'],
            settings_name=value.get('settings_name'),
            relation=value['relation'],
            children=[EntityNode.parse(it) for it in value['children'] or []],
            delete_after=value.get('delete_after'),
        )


class EntityGraph:
    def __init__(self, *nodes: EntityNode):
        self.nodes = nodes

    def __getitem__(self, index) -> EntityNode:
        return self.nodes[index]

    def __eq__(self, other):
        return isinstance(other, EntityGraph) and self.nodes == other.nodes

    def __repr__(self):
        return repr(self.nodes)

    def serialize(self) -> list:
        return [it.serialize() for it in self.nodes]

    @staticmethod
    def parse(value: list):
        return EntityGraph(*map(EntityNode.parse, value))


@dataclasses.dataclass
class Job:
    job_id: str = consts.JOB_ID
    job_type: str = JobType.load
    till_dt: datetime.datetime = consts.NOW_DT
    graph: EntityGraph = dataclasses.field(default_factory=EntityGraph)
    status: str = JobStatus.init
    anonym_id: Optional[str] = consts.ANONYM_ID


@dataclasses.dataclass
class JobEntityTask:
    job_id: str = consts.JOB_ID
    entity_type: str = consts.ENTITY_TYPE
    status: str = JobTaskStatus.init
    entity_ids: List[str] = dataclasses.field(default_factory=list)
    entity_ids_version: int = 0


@dataclasses.dataclass
class JobEntity:
    job_id: str = consts.JOB_ID
    entity_type: str = consts.ENTITY_TYPE
    entity_id: str = 'entity_id'
    entity_data: dict = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class DeleteRequest:
    job_id: str = consts.JOB_ID
    yandex_uids: List[str] = dataclasses.field(
        default_factory=lambda: [consts.YANDEX_UID],
    )
    user_ids: Optional[list] = None
    phone_ids: Optional[list] = None
    personal_phone_ids: Optional[list] = None
    personal_email_ids: Optional[list] = None
    status: str = DeleteStatus.init
    created: datetime.datetime = consts.NOW_DT
