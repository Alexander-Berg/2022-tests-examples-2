# mypy: ignore-errors
import logging
import typing as t

from eats_testing_simplifier_responser.generated.service.swagger import (  # noqa: IS001
    requests,
    responses,
)
import eats_testing_simplifier_responser.generated.service.swagger.models.api as models  # noqa: E501 line too long
from eats_testing_simplifier_responser.generated.web import web_context
import eats_testing_simplifier_responser.internal.utils as utils

logger = logging.getLogger(__name__)

MODELS = t.Union[
    models.CardPaymentMethod,
    models.PersonalWalletPaymentMethod,
    models.CorpPaymentMethod,
    models.ApplePayPaymentMethod,
    models.GooglePayPaymentMethod,
    models.AddNewCardMethod,
    models.SbpPaymentMethod,
    models.CashPaymentMethod,
    models.CreateYandexBankPaymentMethod,
    models.YandexBankPaymentMethod,
]


def _filter_payment_methods(
        user_payments: models.UserPaymentMethodsAvailability,
        context: web_context.Context,
) -> t.List[t.Dict]:  # уазать какие объекты внутри листа
    payment_methods_from_config: t.List = context.config.EATS_TESTING_SIMPLIFIER_RESPONSER_DEFAULT_PAYMENT_METHODS_NEW[  # noqa: E501 line too long
        'default_payment_methods'
    ]
    serialized_data = user_payments.serialize()
    users_payment_methods = serialized_data['payment_methods']
    response_payment_methods = []
    for element in users_payment_methods:
        for default_payment_method in payment_methods_from_config:
            if default_payment_method['id'] != element['id']:
                continue
            if not element['enable']:
                default_payment_method['availability']['available'] = False
                default_payment_method['availability'][
                    'disabled_reason'
                ] = 'Мок оплат'
            response_payment_methods.append(default_payment_method)
    return response_payment_methods


MAPPING: t.Dict = {
    'card': {
        'class': models.CardPaymentMethod,
        'fields': [
            'type',
            'name',
            'short_title',
            'id',
            'bin',
            'currency',
            'system',
            'number',
            'availability',
            'service_token',
        ],
    },
    'personal_wallet': {
        'class': models.PersonalWalletPaymentMethod,
        'fields': [
            'type',
            'name',
            'availability',
            'id',
            'description',
            'currency_rules',
        ],
    },
    'corp': {
        'class': models.CorpPaymentMethod,
        'fields': [
            'type',
            'name',
            'availability',
            'id',
            'description',
            'currency',
        ],
    },
    'applepay': {
        'class': models.ApplePayPaymentMethod,
        'fields': [
            'type',
            'merchant_id_list',
            'availability',
            'service_token',
            'name',
        ],
    },
    'googlepay': {
        'class': models.GooglePayPaymentMethod,
        'fields': [
            'type',
            'merchant_id',
            'availability',
            'service_token',
            'name',
        ],
    },
    'add_new_card': {
        'class': models.AddNewCardMethod,
        'fields': ['type', 'availability', 'binding_service_token', 'name'],
    },
    'sbp': {
        'class': models.SbpPaymentMethod,
        'fields': ['type', 'availability', 'name'],
    },
    'cash': {
        'class': models.CashPaymentMethod,
        'fields': ['type', 'availability', 'name'],
    },
}


def _transform(response_payment_methods: t.List[dict]) -> t.List[MODELS]:
    result = []
    for payment_method in response_payment_methods:
        payment_method_type = payment_method['type']
        model_class: MODELS = MAPPING[payment_method_type]['class']
        fields: t.List[str] = MAPPING[payment_method_type]['fields']
        method = model_class.deserialize(  # noqa: IS001
            {**{k: payment_method[k] for k in fields}},
        )
        result.append(method)

    return result


async def handle(
        request: requests.PaymentMethodsAvailability,
        context: web_context.Context,
) -> responses.PAYMENT_METHODS_AVAILABILITY_RESPONSES:
    if request.middlewares.api_4_0.auth_ctx:
        passport_uid = request.middlewares.api_4_0.auth_ctx.yandex_uid
    else:
        return responses.PaymentMethodsAvailability400(
            data=models.ErrorResponse(
                code='400', message='No passport_uid in request',
            ),
        )
    user_payments = await utils.user_payment_methods(passport_uid, context)
    logger.info('User payment methods LPM = %s', str(user_payments))
    region_id = request.body.region_id

    filtered_user_payment_methods = _filter_payment_methods(
        user_payments, context,
    )
    logger.info(
        'User filtered_user_payment_methods = %s',
        str(filtered_user_payment_methods),
    )
    payment_methods = _transform(filtered_user_payment_methods)
    logger.info('User payment_methods = %s', str(payment_methods))

    if not payment_methods:
        return responses.PaymentMethodsAvailability200(
            data=models.PaymentMethodsAvailabilityResponse(
                payment_methods=payment_methods,
                last_used_payment_method=None,
                region_id=region_id,
            ),
        )

    last_used_payment_method = payment_methods[0]
    last_used_payment_method_id = getattr(
        last_used_payment_method, 'id', last_used_payment_method.type,
    )
    last_payment_method_response = (
        # pylint: disable=W0212
        models._PaymentMethodsAvailabilityResponseLastUsedPaymentMethod(  # noqa: E501
            type=last_used_payment_method.type, id=last_used_payment_method_id,
        )
    )

    return responses.PaymentMethodsAvailability200(
        data=models.PaymentMethodsAvailabilityResponse(
            payment_methods=payment_methods,
            last_used_payment_method=last_payment_method_response,
            region_id=region_id,
        ),
    )
