# pylint: disable=invalid-name

import logging

from generated.clients import personal
from generated.models import personal as personal_model


logger = logging.getLogger(__name__)


class PersonalDummy:
    def __init__(self, *args, **kwargs) -> None:
        pass

    async def v1_data_type_bulk_retrieve_post(
            self,
            request: personal_model.PersonalBulkRetrieveRequest,
            data_type: str,
    ):
        ids = map(lambda item: item.id, request.items)
        return personal.V1DataTypeBulkRetrievePost200(
            personal_model.PersonalBulkRetrieveResponse(
                [
                    personal_model.BulkRetrieveResponseItem(id, id[:-3])
                    for id in ids
                ],
            ),
        )

    async def v1_data_type_store_post(
            self, body: personal_model.PersonalStoreRequest, data_type: str,
    ):
        return personal.V1DataTypeStorePost200(
            personal_model.PersonalStoreResponse(
                body.value + '_id', body.value,
            ),
        )
