# pylint: disable=unused-variable,unused-argument

from stall.client.robot_sdc import RobotSDCClient


async def test_open_hatch(tap, dataset, now, uuid, wait_order_status, job):
    with tap.plan(10, 'Открытие крышки ровера'):

        product = await dataset.product()
        store = await dataset.store()
        user = await dataset.user(store=store)
        stock = await dataset.stock(store=store, product=product, count=10)
        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            approved=now(),
            type='order',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 10,
                }
            ],
            vars = {'editable': True},
            courier=dataset.OrderCourier({
                'external_id': uuid(),
                'type': 'rover',
                'vin': uuid(),
                'taxi_driver_uuid': uuid(),
            }),
        )

        await wait_order_status(order, ('processing', 'waiting'))

        with await order.signal({'type': 'open_hatch'}) as s:
            tap.ok(s, 'сигнал отправлен')
            await wait_order_status(order, ('processing', 'waiting'))

            task = await job.take()
            tap.ok(task, 'задача поставлена')
            tap.ok(task.data['order_id'], order.order_id, 'order_id')

            # UGLY: мокаем функцию отправки запроса
            async def _open_hatch(
                    self,
                    vin: str = None,
                    taxi_driver_uuid: str = None,
                    doc_number: str = None
            ):
                tap.ok(vin, order.courier.vin, 'vin')
                tap.ok(
                    taxi_driver_uuid,
                    order.courier.taxi_driver_uuid,
                    'taxi_driver_uuid'
                )
                tap.ok(doc_number, order.attr('doc_number'), 'doc_number')
                return True
            RobotSDCClient.open_hatch = _open_hatch

            tap.ok(await job.call(task), 'Запрос отправлен')

        await wait_order_status(order, ('complete', 'begin'), user_done=user)
