/* eslint-disable @typescript-eslint/ban-ts-comment */

import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
// @ts-ignore
import { Search } from './search2.view';

export function simple() {
    return execView(Search, {}, mockReq({}, {
        JSON: {
            searchParams: {},
            search: {
                url: 'https://yandex.ru/search/'
            }
        },
        MordaZone: 'ru',
        ClckBaseShort: 'yandex.ru/clck'
    }));
}
