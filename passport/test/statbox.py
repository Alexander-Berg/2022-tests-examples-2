# -*- coding: utf-8 -*-
from passport.backend.core.logging_utils.faker.fake_tskv_logger import (
    BASE_STATBOX_TEMPLATES,
    TskvLoggerFaker,
)


class AdmStatboxLoggerFaker(TskvLoggerFaker):
    logger_class_module = 'passport.backend.adm_api.common.statbox.AdmStatboxLogger'
    templates = BASE_STATBOX_TEMPLATES
