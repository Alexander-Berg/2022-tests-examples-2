import asyncio
import logging
import typing

import hiring_forms_lib.components
from hiring_forms_lib.generated import models
from taxi.logs import auto_log_extra
from taxi.logs import types as log_types

from ...service.config import plugin as config_plugin

logger = logging.getLogger(__name__)


class Cache:
    _config: config_plugin.Config
    _forms_storage: hiring_forms_lib.components.FormsStorage
    _num_load_retries: int
    _pause_before_load_retries_ms: int

    def __init__(
            self,
            context: typing.Any,
            settings: dict,
            activations_parameters: list,
    ):
        self._config = context.config
        self._forms_storage = context.hiring_forms_storage
        self._form_name = settings['form_name']
        self._num_load_retries = settings['num_load_retries']
        self._pause_before_load_retries_ms = settings[
            'pause_before_load_retries_ms'
        ]
        self._ready = False

    @property
    def ready(self) -> bool:
        return self._ready

    async def on_startup(self):
        for attempt_num in range(1, self._num_load_retries + 1):
            try:
                await self._forms_storage.load_form(self._form_name)
            except hiring_forms_lib.exceptions.FormLoadError as exc:
                logger.error(
                    'unable to load form, cannot start',
                    extra=auto_log_extra.to_log_extra(
                        error=str(exc),
                        form_name=self._form_name,
                        attempt=attempt_num,
                    ),
                )
                await asyncio.sleep(
                    self._pause_before_load_retries_ms / 1000.0,
                )
            else:
                self._ready = True
                break
        if not self._ready:
            raise RuntimeError('stop trying to start forms_cache_on_start')

    def get_form(
            self, log_extra: log_types.OPTIONAL_LOG_EXTRA = None,
    ) -> hiring_forms_lib.Form:
        self._check_ready(log_extra)
        return self._forms_storage[self._form_name]

    def from_request(
            self,
            fields: typing.List[models.HiringFormsFieldObject],
            log_extra: log_types.OPTIONAL_LOG_EXTRA = None,
    ) -> typing.List[hiring_forms_lib.Field]:
        self._check_ready(log_extra)
        return self._forms_storage.from_request(
            self._form_name, fields, log_extra=log_extra,
        )

    def _check_ready(self, log_extra: log_types.OPTIONAL_LOG_EXTRA = None):
        if not self._ready:
            logger.error(
                'unable use cache that not ready',
                extra=auto_log_extra.to_log_extra(form_name=self._form_name),
            )
            raise RuntimeError('unable to use cache, it\'s not ready')
