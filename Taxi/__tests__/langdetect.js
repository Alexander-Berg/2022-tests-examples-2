/* eslint-disable indent */
import express from 'express';
import cookieParser from 'cookie-parser';
import request from 'supertest';
import {langdetectFactory} from '../langdetect';

function createApp(options) {
    const app = express();

    app.use(cookieParser());
    app.use(langdetectFactory(options));
    app.get('*', (req, res) => {
        res.json(req.langdetect);
    });

    return app;
}

const LANGUAGES = ['en', 'ru', 'he', 'kz'];
const LANGUAGES_FN = () => LANGUAGES;

describe('langdetect', () => {
    it.each`
        defaultLang   | expected
        ${undefined}  | ${'en'}
        ${'ru'}       | ${'ru'}
        ${() => 'ru'} | ${'ru'}
    `(
        'Должен вернуть $expected, при заданном defaultLang=$defaultLang, если не нашел в списке доступных языков',
        ({defaultLang, expected}) => {
            const app = createApp({availableLanguages: [], defaultLang});
            return request(app)
                .get('/')
                .query({lang: 'he'})
                .set('accept-language', 'he')
                .set('Cookie', ['lang=he'])
                .expect(200, {id: expected, defaultLang: expected});
        }
    );

    it.each`
        languages       | query   | cookie  | headers | expected
        ${LANGUAGES}    | ${'he'} | ${'ru'} | ${'kz'} | ${'he'}
        ${LANGUAGES}    | ${''}   | ${'ru'} | ${'kz'} | ${'ru'}
        ${LANGUAGES}    | ${''}   | ${''}   | ${'kz'} | ${'kz'}
        ${LANGUAGES_FN} | ${'he'} | ${'ru'} | ${'kz'} | ${'he'}
        ${LANGUAGES_FN} | ${''}   | ${'ru'} | ${'kz'} | ${'ru'}
        ${LANGUAGES_FN} | ${''}   | ${''}   | ${'kz'} | ${'kz'}
    `(
        'Доллжен вернуть $expected при query=$query, cookie=$cookie, headers=$headers',
        ({languages, query, cookie, headers, expected}) => {
            const app = createApp({availableLanguages: languages});
            return request(app)
                .get('/')
                .query({lang: query})
                .set('accept-language', headers)
                .set('Cookie', [`lang=${cookie}`])
                .expect(200, {id: expected, defaultLang: 'en'});
        }
    );

    it('defaultLang может быть функцией', () => {
        const defaultLang = jest.fn();
        const app = createApp({defaultLang, availableLanguages: []});
        return request(app)
            .get('/')
            .expect(() => {
                if (defaultLang.mock.calls.length !== 1) {
                    throw new Error('defaultLang должна была вызываться');
                }
            });
    });

    it('availableLanguages может быть функцией', () => {
        const availableLanguages = jest.fn().mockReturnValue(LANGUAGES);
        const app = createApp({availableLanguages});
        return request(app)
            .get('/')
            .expect(() => {
                if (availableLanguages.mock.calls.length !== 1) {
                    throw new Error('availableLanguages должна была вызываться');
                }
            });
    });
});
