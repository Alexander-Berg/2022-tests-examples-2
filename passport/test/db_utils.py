# -*- coding: utf-8 -*-
from passport.backend.oauth.core.db.eav.attributes import (
    serialize_attribute,
    VIRTUAL_ATTR_ENTITY_ID,
)
from passport.backend.oauth.core.db.schemas import TOKEN_VIRTUAL_ATTR_IS_STATELESS
from passport.backend.oauth.core.db.token import StatelessToken


def model_to_bb_response(eav_model):
    """По инстансу модели формирует список атрибутов, который отдал бы ЧЯ"""
    entity = eav_model.entity_name
    result = {}
    for attr_name, attr_value in eav_model._attributes.items():
        attr_id, serialized_value = serialize_attribute(
            entity=entity,
            entity_id=eav_model.id,
            attr_name=attr_name,
            value=attr_value,
        )
        if isinstance(serialized_value, bytes):
            serialized_value = serialized_value.decode()
        result[str(attr_id)] = serialized_value
    result[str(VIRTUAL_ATTR_ENTITY_ID)] = str(eav_model.id)
    if isinstance(eav_model, StatelessToken):
        result[str(TOKEN_VIRTUAL_ATTR_IS_STATELESS)] = '1'
    return result
