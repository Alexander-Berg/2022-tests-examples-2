import os
from pathlib import Path

from stall.template import Template
from libstall.util import time2time


async def test_empty_eac(tap, now, dataset):
    with tap.plan(3, 'Тест на пустой eac'):
        tmp = os.path.abspath(os.getcwd())
        template_dir = Path(tmp).joinpath('template')
        tmpl = Template(template_dir=template_dir)

        store = await dataset.store(
            lang='ru_RU',
            print_setup={'kitchen_sticker': 'sticker'})
        created = time2time(now(), tz=store.tz) \
            .strftime("%d.%m.%Y, %H:%M")

        kw = {
            'valid': 24,
            'ingredients': 'питьевая вода,'
                           ' кофейные зёрна Арабика 100%,'
                           ' молоко питьевое ультрапастеризованное.',
            'calorie': "49.3",
            'fat': "2.7",
            'carbohydrate': "3.9",
            'protein': "2.4",
            'amount_unit': 'г',
            'amount': int(275.000),
            'manufacturer': "ООО \"Партия Еды\"",
            'storage_low_temp': 2,
            'storage_high_temp': 4,
            'country': "Россия"
        }

        pdf = tmpl.render(
            f'kitchen_sticker/{store.print_setup.sticker_size}',
            locale=store.lang,
            eac=store.print_setup.eac,
            logo=store.print_setup.logo,
            long_title='КАРТОФЕЛЬ ФРИ С РЫБНЫМИ ПАЛОЧКАМИ И СОУСОМ ТАРТАР',
            created=created,
            doc_number='123456-12345',
            barcode='2090006004414',
            **kw
        )

        tap.ok(pdf, 'PDF получен')
        tap.isa_ok(pdf, bytes, 'В бинарном формате')
        tap.eq(pdf[:4].decode(), '%PDF', 'Документ PDF')


async def test_render_html(tap, now, dataset):
    with tap.plan(12, 'Рендер HTML шаблона'):
        tmp = os.path.abspath(os.getcwd())
        template_dir = Path(tmp).joinpath('template')
        tmpl = Template(template_dir=template_dir)

        store_ru = await dataset.store(
            lang='ru_RU',
            print_setup={'kitchen_sticker': 'sticker',
                         'sticker_size': '50x150',
                         'eac': True,
                         'logo': 'lavka'})
        created = time2time(now(), tz=store_ru.tz) \
            .strftime("%d.%m.%Y, %H:%M")
        store_en = await dataset.store(
            lang='en_US',
            print_setup={'kitchen_sticker': 'sticker',
                         'sticker_size': '50x150',
                         'eac': True,
                         'logo': 'deli'})
        store_fr = await dataset.store(
            lang='fr_FR',
            print_setup={'kitchen_sticker': 'sticker',
                         'sticker_size': '50x150',
                         'eac': False,
                         'logo': 'deli'})
        store_old = await dataset.store(
            lang='ru_RU',
            print_setup={'kitchen_sticker': 'sticker',
                         'sticker_size': '50x150',
                         'eac': True,
                         'logo': 'lavka'})

        kw = {
            'valid': 24,
            'ingredients': 'питьевая вода,'
                           ' кофейные зёрна Арабика 100%,'
                           ' молоко питьевое ультрапастеризованное.',
            'calorie': "49.3",
            'fat': "2.7",
            'carbohydrate': "3.9",
            'protein': "2.4",
            'amount_unit': 'г',
            'amount': int(275.000),
            'manufacturer': "ООО \"Партия Еды\"",
            'storage_low_temp': 2,
            'storage_high_temp': 4,
            'country': "Россия"
        }
        store = store_ru

        pdf = tmpl.render(
            f'kitchen_sticker/{store.print_setup.sticker_size}',
            locale=store.lang,
            eac=store.print_setup.eac,
            logo=store.print_setup.logo,
            long_title='КАРТОФЕЛЬ ФРИ С РЫБНЫМИ ПАЛОЧКАМИ И СОУСОМ ТАРТАР',
            created=created,
            doc_number='123456-12345',
            barcode='2090006004414',
            **kw
        )

        tap.ok(pdf, 'PDF получен')
        tap.isa_ok(pdf, bytes, 'В бинарном формате')
        tap.eq(pdf[:4].decode(), '%PDF', 'Документ PDF')

        store = store_old

        pdf = tmpl.render(
            f'kitchen_sticker/{store.print_setup.sticker_size}',
            locale=store.lang,
            eac=store.print_setup.eac,
            logo=store.print_setup.logo,
            long_title=' КАРТОФЕЛЬ ФРИ С РЫБНЫМИ ПАЛОЧКАМИ И СОУСОМ ТАРТАР',
            created=created,
            doc_number='123456-12345',
            barcode='2090006004414',
            **kw
        )

        tap.ok(pdf, 'PDF получен')
        tap.isa_ok(pdf, bytes, 'В бинарном формате')
        tap.eq(pdf[:4].decode(), '%PDF', 'Документ PDF')

        kw = {
            'valid': 24,
            'ingredients': 'water,'
                           ' 100% Arabica coffee beans,'
                           ' ultra-pasteurized drinking milk.',
            'calorie': "49.3",
            'fat': "2.7",
            'carbohydrate': "3.9",
            'protein': "2.4",
            'amount_unit': 'g',
            'amount': int(300.000),
            'manufacturer': "ООО \"Yandex.Lavka\"",
            'storage_low_temp': 0,
            'storage_high_temp': 25,
            'country': "UK"
        }

        store = store_en

        pdf = tmpl.render(
            f'kitchen_sticker/{store.print_setup.sticker_size}',
            locale=store.lang,
            eac=store.print_setup.eac,
            logo=store.print_setup.logo,
            long_title='This is the best latte you\'ve ever taste',
            created=created,
            doc_number='123456-12345',
            barcode='2090006004414',
            **kw
        )
        tap.ok(pdf, 'PDF получен')
        tap.isa_ok(pdf, bytes, 'В бинарном формате')
        tap.eq(pdf[:4].decode(), '%PDF', 'Документ PDF')

        kw = {
            'valid': 24,
            'ingredients': 'eau,'
                           ' grains de café 100% Arabica,'
                           ' lait à boire ultra-pasteurisé',
            'calorie': "49.3",
            'fat': "2.7",
            'carbohydrate': "3.9",
            'protein': "2.4",
            'amount_unit': 'g',
            'amount': int(300.000),
            'manufacturer': "ООО \"Yandex.Lavka\"",
            'storage_low_temp': 0,
            'storage_high_temp': 25,
            'country': "UK"
        }

        store = store_fr

        pdf = tmpl.render(
            f'kitchen_sticker/{store.print_setup.sticker_size}',
            locale=store.lang,
            eac=store.print_setup.eac,
            logo=store.print_setup.logo,
            long_title='C\'est le meilleur latte que vous ayez jamais goûté',
            created=created,
            doc_number='123456-12345',
            barcode='2090006004414',
            **kw
        )
        tap.ok(pdf, 'PDF получен')
        tap.isa_ok(pdf, bytes, 'В бинарном формате')
        tap.eq(pdf[:4].decode(), '%PDF', 'Документ PDF')
