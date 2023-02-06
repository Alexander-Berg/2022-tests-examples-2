from stall.model.bug_ticket import BugTicket


async def test_get_ticket_data(dataset, tap, cfg):
    with tap.plan(9, 'Никаких данных в продукте и складе'):
        product = await dataset.product()
        tap.ok(product, 'Продукт создан')
        store = await dataset.store()
        tap.ok(store, 'Склад создан')
        bug_ticket = await BugTicket(
         {
             'bug_type': 'other_product',
             'product_id': product.product_id,
             'status': 'creation',
             'vars': {
                 'store_id': store.store_id,
                 'comment': '',
                 'images': []
             }
         }
        ).save()
        tap.ok(bug_ticket, 'bug_ticket создан')
        cfg.set('bug_ticket.photo_size', '666')
        cfg.set('bug_ticket.wms_link.local', 'https://lavka/')
        cfg.set('bug_ticket.wms_link.testing', 'https://lavka/')
        cfg.set('bug_ticket.wms_link.production', 'https://lavka/')
        image = ', '.join(product.images).format(h=666, w=666)
        wms_link_product = 'https://lavka/' + \
                           product.product_id
        images_from_store = ', '.join(bug_ticket.vars['images'])

        description = f'Заявка со склада: {store.address}\n ' \
                      'Проблема: Сканируется_другой_товар\n ' \
                      f'Товар: {product.external_id}\n ' \
                      f'Описание товара: {product.description}\n ' \
                      'Фото товара из аватарницы: \n' \
                      f'{image} \n' \
                      'Срок годности товара (кол-во дней): ' \
                      f'{product.valid} \n' \
                      f'Баркоды: {product.barcode}\n' \
                      f'Ссылка на товар в wms: (({wms_link_product} ' \
                      'product_card)) \n' \
                      f'{images_from_store} \n' \
                      f'{bug_ticket.vars["comment"]}'

        cfg.set('bug_ticket.queue', 'TESTQUEUE')
        cfg.set('bug_ticket.priority', 'norm')

        ticket_data = await bug_ticket.get_ticket_data()

        tap.ok(ticket_data, 'возвращает информацию о тикете')
        tap.eq_ok(ticket_data['queue'], 'TESTQUEUE', 'очередь проставилась')
        tap.eq_ok(ticket_data['priority'], 'norm', 'приоритет проставился')

        tap.eq_ok(ticket_data['summary'],
                  f'{bug_ticket.bug_type}: product: {product.external_id}',
                  'summary')

        tap.eq_ok(ticket_data['tags'], ['Сканируется_другой_товар'], 'tags')
        tap.eq_ok(ticket_data['description'], description, 'description')


async def test_get_ticket_data_full(dataset, tap, cfg):
    with tap.plan(9, 'Заполены данные о продукте и складе'):
        product = await dataset.product(
            images=['https://xxx.com/bad.png', 'https://extra.com/wow.png'],
            description='описание продукта',
            valid=9999,
        )
        tap.ok(product, 'Продукт создан')
        store = await dataset.store(
            address='address'
        )
        tap.ok(store, 'Склад создан')
        bug_ticket = await BugTicket(
         {
             'bug_type': 'other_product',
             'product_id': product.product_id,
             'status': 'creation',
             'vars': {
                 'store_id': store.store_id,
                 'comment': 'какой-то комментарий',
                 'images': ['https://xxx.com/bad.png',
                            'https://extra.com/wow.png']
             }
         }
        ).save()
        tap.ok(bug_ticket, 'bug_ticket создан')
        image = ', '.join(product.images)
        cfg.set('bug_ticket.wms_link.local', 'https://lavka/')
        cfg.set('bug_ticket.wms_link.testing', 'https://lavka/')
        cfg.set('bug_ticket.wms_link.production', 'https://lavka/')

        wms_link_product = 'https://lavka/' + \
                           product.product_id
        images_from_store = ', '.join(bug_ticket.vars['images'])

        description = f'Заявка со склада: {store.address}\n ' \
                      'Проблема: Сканируется_другой_товар\n ' \
                      f'Товар: {product.external_id}\n ' \
                      f'Описание товара: {product.description}\n ' \
                      'Фото товара из аватарницы: \n' \
                      f'{image} \n' \
                      'Срок годности товара (кол-во дней): ' \
                      f'{product.valid} \n' \
                      f'Баркоды: {product.barcode}\n' \
                      f'Ссылка на товар в wms: (({wms_link_product} ' \
                      'product_card)) \n' \
                      f'{images_from_store} \n' \
                      f'{bug_ticket.vars["comment"]}'

        cfg.set('bug_ticket.queue', 'TESTQUEUE')
        cfg.set('bug_ticket.priority', 'norm')

        ticket_data = await bug_ticket.get_ticket_data()

        tap.ok(ticket_data, 'возвращает информацию о тикете')
        tap.eq_ok(ticket_data['queue'], 'TESTQUEUE', 'очередь проставилась')
        tap.eq_ok(ticket_data['priority'], 'norm', 'приоритет проставился')
        tap.eq_ok(ticket_data['summary'],
                  f'{bug_ticket.bug_type}: product: {product.external_id}',
                  'summary')
        tap.eq_ok(ticket_data['tags'], ['Сканируется_другой_товар'], 'tags')
        tap.eq_ok(ticket_data['description'], description, 'description')
