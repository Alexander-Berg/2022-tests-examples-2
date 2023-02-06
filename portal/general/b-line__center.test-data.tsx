/* eslint-disable @typescript-eslint/ban-ts-comment */

import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';

// @ts-ignore
import { Tabs__resources } from '@block/tabs/tabs.view';
import { BLine } from '@block/b-line/b-line.view';
import { BLine__center } from '@block/b-line/__center/b-line__center.view';

import mock from './mocks/index';

export function simple() {
    let req = mockReq({}, mock);
    const resources = new home.Resources('index', req, execView);
    req.resources = resources as typeof req['resources'];

    execView(Tabs__resources, {}, req);

    return {
        // Чтобы не было фейлов запросов от саджеста
        mockJs: 'window.server = sinon.fakeServer.create();' +
            'window.server.respondWith(/suggest-ya/, \'{}\');',
        // todo Убрать костыль с цветом, когда избавимся от link
        html: (
            <>
                {req.resources.getHTML('head')}
                <style>
                    {`.home-link_black_yes, .home-link_black_yes:visited {
                        color: #000 !important;
                    }`}
                </style>
                {execView(BLine, {
                    'b-line__mod': ' b-line__center',
                    'b-line__content': execView(BLine__center, {}, req)
                })}
            </>
        )
    };
}
