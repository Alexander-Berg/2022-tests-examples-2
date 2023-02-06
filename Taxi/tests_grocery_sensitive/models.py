import dataclasses
from typing import Optional
import uuid


@dataclasses.dataclass
class SensitiveData:
    entity_type: str
    entity_id: str
    request_id: str = dataclasses.field(
        default_factory=lambda: str(uuid.uuid4()),
    )
    yandex_uid: Optional[str] = None
    personal_phone_id: Optional[str] = None
    user_data: Optional[dict] = None
    extra_data: Optional[dict] = None

    def format(self):
        result = dict()
        if self.yandex_uid is not None:
            result['yandex_uid'] = self.yandex_uid
        if self.personal_phone_id is not None:
            result['personal_phone_id'] = self.personal_phone_id
        if self.extra_data is not None:
            result['extra_data'] = self.extra_data
        if self.user_data is not None:
            result.update(self.user_data)

        return result
