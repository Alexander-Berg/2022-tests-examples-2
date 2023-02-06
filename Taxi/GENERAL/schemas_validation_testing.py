import logging

from replication import settings
from replication.foundation.sources import schemas as sources_schemas
from replication.generated.service.swagger import requests
from replication.generated.service.swagger import responses
from replication.generated.service.swagger.models import api as api_models
from replication.generated.web import web_context


logger = logging.getLogger(__name__)


async def handle(
        request: requests.SchemasValidationTesting,
        context: web_context.Context,
) -> responses.SCHEMAS_VALIDATION_TESTING_RESPONSES:
    _check_on_testing_environment()

    secret_id = _make_secret_id(request)
    source_schemas_keeper = context.replication_core.source_schemas_keeper

    connections_state = await source_schemas_keeper.get_connections_state_info(
        secret_id=secret_id, source_type=request.body.source_type,
    )

    return responses.SchemasValidationTesting200(
        api_models.SchemasValidation200(
            created_connections=_prepare_created_connections(
                connection_state=connections_state,
            ),
        ),
    )


def _prepare_created_connections(connection_state: list) -> list:
    res_connection_state = []
    for state in connection_state:
        res_connection_state.append(
            api_models.SchemasValidation200.CreatedConnectionsItem(**state),
        )
    return res_connection_state


def _make_secret_id(
        request: requests.SchemasValidationTesting,
) -> sources_schemas.DatabaseSecretId:
    return sources_schemas.DatabaseSecretId(
        secret_type=request.body.secret_type, secret_id=request.body.secret_id,
    )


def _check_on_testing_environment():
    if settings.ENVIRONMENT == settings.PRODUCTION_ENVIRONMENT:
        raise responses.SchemasValidationTesting403(
            api_models.SchemasValidation403(
                code='reject-on-stable-env',
                message='This endpoint cannot be used in a stable environment',
            ),
        )
