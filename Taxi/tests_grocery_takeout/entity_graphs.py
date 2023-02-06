from . import models

DEFAULT = models.EntityGraph(
    models.EntityNode(
        entity_type='yandex_uid',
        id_name='yandex_uid',
        relation=models.EntityRelation.direct,
        children=[
            models.EntityNode(
                entity_type='orders',
                relation=models.EntityRelation.indirect,
                id_name='order_id',
            ),
        ],
    ),
)
