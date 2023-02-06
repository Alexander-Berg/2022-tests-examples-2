# pylint: disable=invalid-name
import dataclasses
import json
import typing as tp

import asyncpg

from supportai_lib import models
from supportai_lib import schemas

from supportai_models.generated.service.swagger import models as api_models
from . import relations

supportai = schemas.Schemas.supportai


@dataclasses.dataclass
@relations.model_model_test_data.register(
    related_field='model_id',
    related_name='model_test_records',
    is_multiple=True,
)
class ModelTestData(models.BaseModel):
    id: int
    model_id: int
    ground_truth_slug: str
    probabilities: tp.List

    db_table = supportai.model_test_data
    api_model = api_models.api.TestDataRecord

    primary_keys = ['id']

    @classmethod
    def from_record(cls, record: asyncpg.Record):
        data = dict(record)
        data['probabilities'] = json.loads(data.pop('probabilities'))
        return cls(**data)

    def to_api(self):
        return self.api_model(
            ground_truth_slug=self.ground_truth_slug,
            probabilities=[
                api_models.api.Probability(
                    slug=probability['slug'],
                    probability=probability['probability'],
                )
                for probability in self.probabilities
            ],
        )
