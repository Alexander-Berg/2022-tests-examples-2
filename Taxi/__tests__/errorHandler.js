/* eslint-disable indent */
import request from 'supertest';
import express from 'express';

import errorHandler from '_common/server/middleware/errorHandler';
import {RedirectError, RenderError, HttpError} from '_common/server/errors';

const fallbackErrorText = 'ERROR';
const renderFn = jest.fn();
const i18nPrint = jest.fn();

jest.mock('_common/server/utils/logger', () => ({
    info: () => {},
    warn: () => {},
    fatal: () => {}
}));

const errorImpl = () => {
    throw new Error('oops');
};

function createApp() {
    const app = express();

    app.use((req, res, next) => {
        req.bunker = {
            tanker: {
                keysets: {
                    frontend: {
                        keys: {}
                    }
                }
            }
        };
        res.render500 = async () => {
            renderFn();
            res.status(500).send('render five hundred');
        };
        req.i18n = {
            print: i18nPrint
        };
        next();
    });

    app.get('/', (req, res) => {
        res.status(200).send('ok');
    });

    app.get('/error', (req, res) => {
        throw new Error('oops');
    });

    app.get('/render-error', (req, res) => {
        const cause = new Error('oops');
        throw new RenderError('app/index', cause);
    });

    app.get('/redirect-error', (req, res) => {
        throw new RedirectError('/', 302);
    });

    app.get('/401-error', (req, res) => {
        throw new HttpError(401, 'auth error');
    });

    app.get('/500-error', (req, res) => {
        throw new HttpError(500, 'backend timeout');
    });

    app.use(errorHandler({i18nKey: 'i18n', fallbackErrorText}));

    return app;
}

describe('errorHandler', () => {
    let app;
    beforeEach(() => {
        app = createApp();
    });

    afterEach(() => {
        jest.resetAllMocks();
    });

    it.each`
        path               | label
        ${'/error'}        | ${'something error'}
        ${'/render-error'} | ${'render error'}
        ${'/500-error'}    | ${'http error with status 500'}
    `('Should be render five hundredth page on $label', async ({path}) => {
        const response = await request(app).get(path);
        expect(response.statusCode).toBe(500);
        expect(renderFn).toHaveBeenCalledTimes(1);
    });

    it.each`
        path               | label
        ${'/error'}        | ${'something error'}
        ${'/render-error'} | ${'render error'}
        ${'/500-error'}    | ${'http error with status 500'}
    `('Should be print localized text on $label, if failed to render five hundredth page', async ({path}) => {
        // failed render to five hundred page
        renderFn.mockImplementation(errorImpl);
        await request(app).get(path);
        expect(i18nPrint).toHaveBeenCalledTimes(1);
    });

    it.each`
        path               | label
        ${'/error'}        | ${'something error'}
        ${'/render-error'} | ${'render error'}
        ${'/500-error'}    | ${'http error with status 500'}
    `(
        'Should be print fallback text on $label, if failed to render five hundredth page and print localized text',
        async ({path}) => {
            // failed render to five hundred page
            renderFn.mockImplementation(errorImpl);
            i18nPrint.mockImplementation(errorImpl);
            const response = await request(app).get(path);
            expect(response.text).toEqual(fallbackErrorText);
        }
    );

    it('Should be redirect on RedirectError', async () => {
        const response = await request(app).get('/redirect-error');
        expect(response.statusCode).toEqual(302);
    });

    it('Should be return status and message on HttpError with 4xx status', async () => {
        const response = await request(app).get('/401-error');
        expect(response.statusCode).toEqual(401);
        expect(response.body.error).toBe('auth error');
    });
});
