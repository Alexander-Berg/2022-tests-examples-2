import scooter_accumulator_bot.clients as clients
from scooter_accumulator_bot.generated.service.swagger.models import (
    api as api_models,
)
from scooter_accumulator_bot.telegram_bot import notification

# Проверяем, что все роли из clients.Role есть в кодогенеренной схеме.
# Зачем: при добавлении новой роли можно забыть прорастить это в ручки.
async def test_ok():
    for user_role_field in clients.Role:
        api_models.BotMessageRequest(
            message='unused_message',
            user_role=user_role_field.value.lower(),
            send_to_all=False,
            format=None,
            notification_type=notification.Type.VALIDATE_ACCUMULATORS_RESPONSE,
        )
