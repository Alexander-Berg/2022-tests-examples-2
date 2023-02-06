from typing import Dict
from typing import Optional

import pytest

from form_builder.components.async_validators import _base
from form_builder.components.async_validators import model
from form_builder.models import fields
from form_builder.utils import field_types as ftps


class _TestImpl(_base.BaseAsyncValidator):
    name = 'test-impl'
    required_pd_type = 'phones'

    async def send_data(
            self,
            form_code: str,
            form_values: Dict[str, ftps.Value],
            main_field: fields.Field,
            state: model.ValidatorState,
            x_remote_ip: Optional[str] = None,
    ):
        pass

    async def verify_data(
            self,
            form_code: str,
            form_values: Dict[str, ftps.Value],
            main_field: fields.Field,
            value: ftps.Value,
            state: model.ValidatorState,
            x_remote_ip: Optional[str] = None,
    ) -> model.ValidateResult:
        return model.ValidateResult(True)


@pytest.fixture(name='test_instance')
def _test_instance(web_context):
    return _TestImpl(web_context)


@pytest.fixture(name='get_state')
def _get_state(web_context):
    async def _wrapper(form_code, field_code, submit_id):
        return await model.fetch(
            form_code=form_code,
            field_code=field_code,
            submit_id=submit_id,
            context=web_context,
            conn=web_context.pg.primary,
        )

    return _wrapper
