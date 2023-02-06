import argparse

from aiohttp import web

from scripts.cron.update_true_mark_token import main
from stall.client.onec import client as onec_client
from stall.model.stash import Stash


async def test_update_true_mark(tap, cfg, ext_api):
    with tap.plan(3, 'проверяем вытаскивание токена из 1с в стэш'):
        cfg.set('sync.1c.login', 'admin')
        cfg.set('sync.1c.password', 'admin')
        cfg.set('sync.1c.update_true_token_timeout', 0)

        async def handler(req):  # pylint: disable=unused-argument
            return web.json_response(
                status=200,
                data={'token': '123456'},
            )

        async with await ext_api(onec_client, handler):
            args = argparse.Namespace(company_id='zhopka')
            await main(args)

            stash = await Stash.load('true_mark_token_1c_zhopka', by='name')
            tap.eq(stash.value, {'true_mark_token': '123456'}, 'value ok')

            stash.value['true_mark_token'] = '111111'
            await stash.save()
            tap.eq(stash.value, {'true_mark_token': '111111'}, 'value changed')

            await main(args)
            stash = await Stash.load('true_mark_token_1c_zhopka', by='name')
            tap.eq(stash.value, {'true_mark_token': '123456'}, 'value changed')


async def test_update_true_mark_fail(tap, cfg, ext_api):
    with tap.plan(4, 'проверяем кейс с частичными фейлами'):
        cfg.set('sync.1c.login', 'admin')
        cfg.set('sync.1c.password', 'admin')

        async def handler(req):
            cid2res = {
                '111': {
                    'status': 200,
                    'data': {'token': '111'},
                },
                '222': {
                    'status': 401,
                    'data': {'token': '222'},
                },
                '333': {
                    'status': 200,
                    'data': {'foo': 'bar'},
                },
                '444': {
                    'status': 200,
                    'data': {'token': '444'},
                },
            }

            rj = await req.json()
            res = cid2res.get(rj['company_id'], {'status': 400, 'data': {}})

            return web.json_response(
                status=res['status'],
                data=res['data'],
            )

        company_ids = ['111', '222', '333', '444']
        cfg.set(f'sync.1c.companies_true_mark.{cfg("mode")}', company_ids)
        async with await ext_api(onec_client, handler):
            args = argparse.Namespace(company_id=None)
            await main(args)

        stashes = [
            await Stash.load(f'true_mark_token_1c_{cid}', by='name')
            for cid in company_ids
        ]

        tap.eq(stashes[0].value['true_mark_token'], '111', 'есть токен 111')
        tap.ok(not stashes[1], 'нету стэша')
        tap.ok(not stashes[2], 'нету стэша')
        tap.eq(stashes[3].value['true_mark_token'], '444', 'есть токен 444')
