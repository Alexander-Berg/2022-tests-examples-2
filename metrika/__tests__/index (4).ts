import { Request, Response } from 'express';
import { noop } from 'lodash';

import { secretkeyV1 } from '..';

const getReq = () =>
    (({
        blackbox: {
            uid: 12345,
            status: 'VALID',
        },
        cookies: {
            yandexuid: '67890',
        },
    } as unknown) as Request);

describe('secret-key', () => {
    const res = ({} as unknown) as Response;

    it('fills secretkeyV1 field', () => {
        const req = getReq();
        secretkeyV1(req, res, noop);

        expect(req.secretkeyV1).toBeTruthy();
    });

    it(`doesn't overwrite req.secretkey if it exists`, () => {
        const req = getReq();
        req.secretkey = 'predefinedValue';
        secretkeyV1(req, res, noop);

        expect(req.secretkey).toBe('predefinedValue');
    });

    it(`doesn't set req.secretkey if it doesn't exists`, () => {
        const req = getReq();
        secretkeyV1(req, res, noop);

        expect(req.secretkey).toBeUndefined();
    });

    it('calls next', () => {
        const req = getReq();
        const next = jest.fn();
        secretkeyV1(req, res, next);

        expect(next).toHaveBeenCalledTimes(1);
    });
});
