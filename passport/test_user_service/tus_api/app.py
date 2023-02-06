# -*- coding: utf-8 -*-
import logging
from logging.config import dictConfig

from flask import (
    Blueprint,
    Flask,
)
from passport.backend.core.conf import settings as passport_settings
from passport.backend.qa.test_user_service.tus_api import (
    settings as tus_settings,
    views,
)
from passport.backend.qa.test_user_service.tus_api.utils import (
    error_handler,
    escape_query_characters_middleware,
)


log = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)

    log.info('creating app')

    app.add_url_rule('/ping/',
                     view_func=views.ping, methods=['GET'])

    api_v1 = Blueprint('1', __name__)
    api_v1.add_url_rule('/bind_phone/',
                        view_func=views.BindPhone.as_view(), methods=['POST'])
    api_v1.add_url_rule('/create_account/portal/',
                        view_func=views.CreateAccountPortal.as_view(), methods=['GET', 'POST'])
    api_v1.add_url_rule('/create_tus_consumer/',
                        view_func=views.CreateTusConsumer.as_view(), methods=['GET', 'POST'])
    api_v1.add_url_rule('/get_account/',
                        view_func=views.GetAccount.as_view(), methods=['GET'])
    api_v1.add_url_rule('/list_accounts/',
                        view_func=views.ListAccounts.as_view(), methods=['GET'])
    api_v1.add_url_rule('/remove_account_from_tus/',
                        view_func=views.RemoveAccount.as_view(), methods=['GET'])
    api_v1.add_url_rule('/save_account/',
                        view_func=views.SaveAccount.as_view(), methods=['POST'])
    api_v1.add_url_rule('/unlock_account/',
                        view_func=views.UnlockAccount.as_view(), methods=['GET', 'POST'])
    app.register_blueprint(api_v1, url_prefix='/1')

    api_idm = Blueprint('idm', __name__)
    api_idm.add_url_rule('/add-role/', view_func=views.IdmAddRole.as_view(), methods=['POST'])
    api_idm.add_url_rule('/get-all-roles/', view_func=views.IdmGetAllRoles.as_view(), methods=['GET'])
    api_idm.add_url_rule('/info/', view_func=views.IdmInfo.as_view(), methods=['GET'])
    api_idm.add_url_rule('/remove-role/', view_func=views.IdmRemoveRole.as_view(), methods=['POST'])
    app.register_blueprint(api_idm, url_prefix='/idm')

    app.errorhandler(Exception)(error_handler)

    app.wsgi_app = escape_query_characters_middleware(app.wsgi_app)
    return app


def configure_settings():
    if not passport_settings.configured:
        passport_settings.configure(tus_settings)


def prepare_environment():
    dictConfig(tus_settings.LOGGING)


def execute_app():
    configure_settings()
    prepare_environment()

    application = create_app()

    return application
