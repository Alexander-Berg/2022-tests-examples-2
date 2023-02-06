/* eslint-disable max-len */
import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';

import { Stocks } from '@block/stocks/stocks.view';
import * as normal from './mocks/normal.json';
import * as many from './mocks/many.json';
const base = {
    blocks_status: {
        enabled_blocks_count: 1
    }
};
const styles = `
    <style>
        .stocks {
            width: 270px;
            padding: 8px 16px;
        }
    </style>
`;

export function stocks_normal() {
    return styles + execView(Stocks, {}, mockReq({}, {
        ...normal as unknown as Partial<Req3Server>,
        ...base as Partial<Req3Server>
    }));
}

export function stocks_many() {
    return styles + execView(Stocks, {}, mockReq({}, {
        ...many as unknown as Partial<Req3Server>,
        ...base as Partial<Req3Server>
    }));
}
export function stocks_normal_night() {
    return {
        html: styles + execView(Stocks, {}, mockReq({}, {
            ...normal as unknown as Partial<Req3Server>,
            ...base as Partial<Req3Server>
        })),
        skin: 'night'
    };
}
export function stocks_many_night() {
    return {
        html: styles + execView(Stocks, {}, mockReq({}, {
            ...many as unknown as Partial<Req3Server>,
            ...base as Partial<Req3Server>
        })),
        skin: 'night'
    };
}
