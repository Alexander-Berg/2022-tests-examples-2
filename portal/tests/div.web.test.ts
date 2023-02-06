/* eslint-env node, mocha */
import {expect, use} from 'chai';
import * as chaiJestSnapshot from 'chai-jest-snapshot';
import * as path from 'path';
import * as nock from 'nock';
import {getLogger} from 'portal-node-logger';
import Handlers from '../blocks/index';
import * as mocks from './mocks.web/index';
import {performance} from 'perf_hooks';

import DivHandler, {IRequest} from '../blocks/handler';
const baseReporter = require('mocha/lib/reporters/base');

use(chaiJestSnapshot);
const logger = getLogger({write_to_console: true}, 'tests');
const timeLimit = 2;
const now = Date.now;
const random = Math.random;

function makeReq(id: string) {
    return {
        query: {
            id,
            lat: '55.73562240600586',
            lon: '37.6424446105957'
        },
        cookies: {},
        experiments: new Set(),
        flags: new Set(),
        headers: {['user-agent']: 'got'},
        logger,
        tvm: {
            travel: {ticket: '911'}
        }
    };
}


const tests: {
    [key: string]: {
        handler: {new(req: IRequest, params?: object): DivHandler},
        api?: {
            host: string,
            path: string
        },
        apiResponse?: any
    }
} = {
    sport: {
        handler: Handlers.sport,
        api: {
            host: 'http://data.news.yandex.ru',
            path: '/sport/api/v1/personal_feed?flags=yxnews_enable_personal_feed_api%3D1&picture_sizes=563.304.1&count=20&drop_sensitive=1&is_touch=1&need_pictures=1'
        },
        apiResponse: mocks.sportResponse
    },
    sport_desktop: {
        handler: Handlers.sport_desktop,
        api: {
            host: 'http://data.news.yandex.ru',
            path: '/sport/api/v1/personal_feed?need_pictures=1&is_touch=1&count=20&drop_sensitive=1&picture_sizes=188.204.1'
        },
        apiResponse: mocks.sportDesktopResponse
    },
    news: {
        handler: Handlers.news,
        api: {
            host: 'http://data.news.yandex.ru',
            path: '/api/v2/rubric?preset=morda_div_cards_news_touch'
        },
        apiResponse: mocks.newsResponse
    },
    news_touch_d2: {
        handler: Handlers.news_touch_d2,
        api: {
            host: 'http://data.news.yandex.ru',
            path: '/api/v2/rubric?need_pictures=1&picture_sizes=244.122.1.avatars&video_sizes=244.122.1.avatars' +
                '&preset=morda_div_cards_news_touch&count=10&rubric=personal_feed&personalize=personal_feed'
        },
        apiResponse: mocks.newsD2TouchResponse
    },
    news_desktop_d2: {
        handler: Handlers.news_desktop_d2,
        api: {
            host: 'http://data.news.yandex.ru',
            path: '/api/v2/rubric?need_pictures=1&picture_sizes=256.128.1.avatars&video_sizes=256.128.1.avatars' +
                '&preset=morda_div_cards_news_desktop&count=15&rubric=personal_feed&personalize=personal_feed'
        },
        apiResponse: mocks.newsD2DesktopResponse
    },
    market_desktop: {
        handler: Handlers.market_desktop,
        api: {
            host: 'http://touch-omm.preport.vs.market.yandex.net:17051',
            path: '/yandsearch?reqid=&pof=908&bsformat=2&numdoc=15&pp=110&subreqid=1&client=morda-geohelper' +
                '&place=omm_parallel&rgb=blue&omm_place=marketblock_web&show-urls=encrypted&enable-reasons-to-buy=1' +
                '&rearr-factors=omm_parallel_offerid=1;omm_parallel_promos=1;' +
                'omm_parallel_discount=1;omm_parallel_blue_models_factor=2;' +
                'omm_parallel_promo_codes=1;' +
                'market_dj_exp_for_omm_parallel=blue_attractive_models_omm_parallel_low_shuffle'
        },
        apiResponse: mocks.marketDesktopResponse
    },
    market_touch: {
        handler: Handlers.market_touch,
        api: {
            host: 'http://touch-omm.preport.vs.market.yandex.net:17051',
            path: '/yandsearch?reqid=&pof=903&bsformat=2&numdoc=15&pp=110&subreqid=1&client=morda-geohelper' +
                '&place=omm_parallel&rgb=blue&omm_place=marketblock_touch&show-urls=encrypted&enable-reasons-to-buy=1' +
                '&rearr-factors=omm_parallel_offerid=1;omm_parallel_promos=1;' +
                'omm_parallel_discount=1;omm_parallel_blue_models_factor=2;' +
                'omm_parallel_promo_codes=1;' +
                'market_dj_exp_for_omm_parallel=blue_attractive_models_omm_parallel_low_shuffle'
        },
        apiResponse: mocks.marketTouchResponse
    },

    games_touch: {
        handler: Handlers.games,
        api: {
            host: 'https://api.games.yandex.ru',
            path: '/api/light/v2/touch?with_gif=1&domain=ru&lang=ru&reqid=&puid=&yandexuid=&icookie='
        },
        apiResponse: mocks.gamesTouchResponse
    },
    games_desktop: {
        handler: Handlers.games_desktop,
        api: {
            host: 'https://api.games.yandex.ru',
            path: '/api/light/v2/desktop?with_gif=1&domain=ru&lang=ru&reqid=&puid=&yandexuid=&icookie='
        },
        apiResponse: mocks.gamesDesktopResponse
    },
    games_desktop_redesign: {
        handler: Handlers.games_desktop_v2,
        api: {
            host: 'https://api.games.yandex.ru',
            path: '/api/light/v2/desktop?domain=ru&icookie=&lang=ru&puid=&reqid=&yandexuid='
        },
        apiResponse: mocks.gamesDesktopRedesignResponse
    },
    autoru_desktop: {
        handler: Handlers.autoru_desktop,
        api: {
            host: 'https://search-app.auto.ru',
            path: '/api/1.0/inserts/morda/?platform=desktop'
        },
        apiResponse: mocks.autoruDesktopResponse
    },
    lavka_desktop: {
        handler: Handlers.lavka_desktop
    },
    realty_desktop: {
        handler: Handlers.realty_desktop,
        api: {
            host: 'https://search-app.realty.yandex.ru',
            path: '/api/3/div/data/?geo_id=&platform='
        },
        apiResponse: mocks.realtyDesktopResponse
    },
    realty_touch: {
        handler: Handlers.realty_touch,
        api: {
            host: 'https://search-app.realty.yandex.ru',
            path: '/api/3/div/data/?geo_id=&platform='
        },
        apiResponse: mocks.realtyTouchResponse
    },
    travel_touch: {
        handler: Handlers.travel_touch,
        api: {
            host: 'http://api.travel-balancer-test.yandex.net',
            path: '/api/serp/v1/get_popular_destinations?geo_id=213'
        },
        apiResponse: mocks.travelResponse
    },
    travel_desktop: {
        handler: Handlers.travel_desktop,
        api: {
            host: 'http://api.travel-balancer-test.yandex.net',
            path: '/api/serp/v1/get_popular_destinations?geo_id=213'
        },
        apiResponse: mocks.travelResponse
    },
    general_desktop: {
        handler: Handlers.general_desktop,
        api: {
            host: 'https://search-app.o.yandex.ru',
            path: '/api/div/data/?geo_id=&platform='
        },
        apiResponse: mocks.generalDesktopResponse
    },
    general_touch: {
        handler: Handlers.general_touch,
        api: {
            host: 'https://search-app.o.yandex.ru',
            path: '/api/div/data/?geo_id=&platform='
        },
        apiResponse: mocks.generalTouchResponse
    }
};

describe('Div1/2 Desktop/Touch card tests', () => {
    beforeEach(() => {
        Date.now = () => 1000;
        Math.random = () => 0;
    });

    afterEach(() => {
        nock.cleanAll();
        Date.now = now;
        Math.random = random;
    });

    for (const cardId of Object.keys(tests)) {
        it(`should generate ${cardId} card`, async function () {
            this.slow(100000);
            const test = tests[cardId];

            if (test.api) {
                nock(test.api.host)
                    .get(test.api.path)
                    .reply(200, test.apiResponse)
                    .persist();
            }

            nock(/.*/).get(/.?/)
                .reply(404, function(uri) {
                    // eslint-disable-next-line no-console
                    console.error(`Request for ${cardId} not matched`,
                        `\nExpected ${test.api?.host}${test.api?.path}\n`,
                        `\nActual   ${this.req.getHeader('host')}${uri}`);
                    return 'Not matched';
                })
                .persist();

            const req = makeReq(cardId);

            const block = new (tests[cardId].handler)(req as any, {});
            const result = await block.createBlock();

            expect(JSON.parse(JSON.stringify(result))).to.matchSnapshot(path.join(__dirname, 'mocks.web/div', `${cardId}.card.snap`), 'card');

            const data = tests[cardId].apiResponse;

            const runsCount = 100;
            const renderTimeMedian = Array
                .from({length: runsCount}, () => {
                    const start = performance.now();
                    block.renderData(data);
                    return performance.now() - start;
                })
                .sort((a, b) => a - b)[Math.floor(runsCount / 2)];

            if (this.test) {
                this.test.title += baseReporter
                    .color(renderTimeMedian < timeLimit ? 'checkmark' : 'fail', ` ${renderTimeMedian.toFixed(2)}ms`);
            }
        });
    }
});
