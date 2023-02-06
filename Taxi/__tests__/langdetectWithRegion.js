const request = require('supertest');
const cookieParser = require('cookie-parser');
const tld = require('@yandex-int/express-tld');
const express = require('express');

const langdetectWithRegion = require('../langdetectWithRegions');

const mockFullData = require('./langdetectWithRegion_allData.mock.json');
const mockWithoutCountriesByDomainData = require('./langdetectWithRegion_withoutCountiesByDomain.mock.json');
const mockWithoutDefaultLangData = require('./langdetectWithRegion_withoutDefaultLang.mock.json');

describe('langdetectWithRegion middleware', () => {
    it('langdetectWithRegion должен получить информацию о регионе из бункера', () => {
        const app = createApp(mockFullData);

        return request(app)
            .get('/')
            .set('Host', 'taxi.yandex.ru')
            .expect(200, {
                fi: {
                    isLinkToMain: true,
                    isDefaultForDomain: true,
                    defaultLang: 'en',
                    host: '//taxi.yandex.fin',
                    languages: ['fr', 'fi', 'en', 'he']
                },
                ci: {
                    isLinkToMain: true,
                    isDefaultForDomain: true,
                    defaultLang: 'en',
                    host: '//taxi.yandex.cin',
                    languages: ['fr', 'fi', 'en', 'he']
                },
                co: {
                    isLinkToMain: true,
                    isDefaultForDomain: true,
                    defaultLang: 'es',
                    host: '//taxi.yandex.con',
                    languages: ['es', 'en']
                },
                int: {
                    isLinkToMain: true,
                    isDefaultForDomain: true,
                    defaultLang: 'en',
                    host: '//taxi.yandex.int',
                    languages: ['fr', 'fi', 'en', 'he']
                }
            });
    });

    it('langdetectWithRegion должен работать без информации о странах по доменам', () => {
        const app = createApp(mockWithoutCountriesByDomainData);

        return request(app)
            .get('/')
            .expect(200, {
                fi: {
                    isLinkToMain: true,
                    isDefaultForDomain: false,
                    defaultLang: 'en',
                    languages: ['fr', 'fi', 'en', 'he']
                },
                ci: {
                    isLinkToMain: true,
                    isDefaultForDomain: false,
                    defaultLang: 'en',
                    languages: ['fr', 'fi', 'en', 'he']
                },
                co: {
                    isLinkToMain: true,
                    isDefaultForDomain: false,
                    defaultLang: 'es',
                    languages: ['es', 'en']
                },
                int: {
                    isLinkToMain: true,
                    isDefaultForDomain: false,
                    defaultLang: 'en',
                    languages: ['fr', 'fi', 'en', 'he']
                }
            });
    });

    it('langdetectWithRegion должен работать без информации о языке по умолчанию', () => {
        const app = createApp(mockWithoutDefaultLangData);

        return request(app)
            .get('/')
            .expect(200, {
                fi: {
                    isDefaultForDomain: false,
                    isLinkToMain: true,
                    languages: ['fr', 'fi', 'en', 'he']
                },
                ci: {
                    isDefaultForDomain: false,
                    isLinkToMain: true,
                    languages: ['fr', 'fi', 'en', 'he']
                },
                co: {
                    isDefaultForDomain: false,
                    isLinkToMain: true,
                    languages: ['es', 'en']
                },
                int: {
                    isDefaultForDomain: false,
                    isLinkToMain: true,
                    languages: ['fr', 'fi', 'en', 'he']
                }
            });
    });

    function createApp(prepareData = {}) {
        const app = express();

        app.get(
            ['/:region([a-z]{2}_[a-z]{2,3})/:page?', '/:page?'],
            [
                tld(),
                cookieParser(),
                (req, res, next) => {
                    Object.assign(req, prepareData);
                    next();
                },
                langdetectWithRegion('countries')
            ],
            (req, res) => {
                res.status(200).json(req.langdetect.regions);
            }
        );

        // eslint-disable-next-line handle-callback-err
        app.use((err, req, res, next) => {
            res.status(500).json({message: err.message});
        });

        return app;
    }
});
