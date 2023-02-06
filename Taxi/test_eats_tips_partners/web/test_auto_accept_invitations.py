import pytest

from eats_tips_partners.common import invitations as invitations_lib


@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
@pytest.mark.mysql('chaevieprosto', files=['chaevie.sql'])
async def test_auto_accept_invitations(
        taxi_eats_tips_partners_web, web_context, pgsql,
):
    result_alias_info, result_no_card = (
        await invitations_lib.auto_accept_invitations(
            web_context,
            admin_ids=['700', '00000000-0000-0000-0000-000000000102'],
        )
    )
    assert (
        sorted(result_alias_info, key=lambda elem: elem.get('place_number'))
        == sorted(
            [
                {
                    'linked_personal_code': '3000000',
                    'person_fullname': 'Пупкин Георгий Витальевич',
                    'person_name': 'Гоша',
                    'place_address': None,
                    'place_number': '0001090',
                    'place_title': None,
                },
                {
                    'linked_personal_code': '0000140',
                    'person_fullname': 'Чаевых Потап Вилларибо',
                    'person_name': 'Потап',
                    'place_address': '',
                    'place_number': '0001000',
                    'place_title': 'Деревня Вилларибо',
                },
                {
                    'linked_personal_code': '0000280',
                    'person_fullname': 'Пупкин Инокентий Витальевич',
                    'person_name': 'Кеша',
                    'place_address': None,
                    'place_number': '0001080',
                    'place_title': None,
                },
            ],
            key=lambda elem: elem.get('place_number'),
        )
    )
    assert result_no_card == [
        {
            'person_fullname': 'Новый админ',
            'person_name': '',
            'place_address': '',
            'place_number': '0001020',
            'place_title': 'Сам себе ресторан',
        },
    ]
