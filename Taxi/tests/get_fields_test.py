
from ci_tools import report, get_fields_from_config


@report('ikars', 'get_fields.py', tg_bot=True, tg_login='iiggy')
def main():
    raise AttributeError("Fuck'em all!")


if __name__ == '__main__':
    tg_token, chat_id = get_fields_from_config('bot_config.json',
                                               ['regular_client_tbot_token',
                                                'regular_discounts_chat_id'])
    print(chat_id)
    main()
