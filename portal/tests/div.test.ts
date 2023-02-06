/* eslint-env node, mocha */
import {expect, use} from 'chai';
import {Response} from 'express';
import * as chaiJestSnapshot from 'chai-jest-snapshot';
import {getLogger} from 'portal-node-logger';
import {experiments, RequestWithExps} from '@server/libs/experiments';
import {cards as div1Cards} from '../blocks/div1/app/index';
import {cards as div2Cards} from '../blocks/div2/app/index';
import * as mocks from './mocks/index';
import {I18n} from '../i18n';
import {getAppDivOpts, AppReq, AppDivOptions} from '../blocks/app-div-options';
import * as path from 'path';
import {performance} from 'perf_hooks';
import {mockResponse} from './mock-response';

const baseReporter = require('mocha/lib/reporters/base');
use(chaiJestSnapshot);
mocks.req.logger = getLogger({write_to_console: true}, 'tests');
experiments.init(mocks.req as unknown as RequestWithExps, null as unknown as Response, () => undefined);

const timeLimit = 2;
const now = Date.now;
const random = Math.random;

describe('Div PP card tests', () => {
    beforeEach(() => {
        Date.now = () => 1000;
        Math.random = () => 0;
    });

    afterEach(() => {
        Date.now = now;
        Math.random = random;
    });

    const i18n = new I18n(mocks.req.query.lang);
    const clean = (obj: unknown)=> {
        if (typeof obj === 'object' && obj && 'templates' in obj) {
            delete (obj as {[k: string]: unknown}).templates;
        }

        return JSON.parse(JSON.stringify(obj));
    };
    const excludedBlocks = ['market_div2'];
    const _div2Cards = div2Cards.filter(card => !excludedBlocks.includes(card.config.id));

    for (const card of [...div1Cards, ..._div2Cards]) {
        const config = card.config;
        const opts = getAppDivOpts(
            mocks.req.post_data[config.id as keyof typeof mocks.req.post_data] as AppDivOptions['params'],
            mocks.req as unknown as AppReq,
            mocks.req.data[config.id as keyof typeof mocks.req.data]
        );

        it(`should generate ${config.id} card`, async function () {
            this.slow(100000);
            const response = mockResponse(config.id, card.fetch.bind(null), opts);
            const data = await response;
            const renderer = card.render.bind(null);
            const result = renderer(i18n, opts, data);

            expect(clean(result)).to.matchSnapshot(path.join(__dirname, 'mocks/div', `${config.id}.card.snap`), 'card');
            if (card.requestParamsBuilder) {
                expect(card.requestParamsBuilder(opts))
                    .to.matchSnapshot(path.join(__dirname, 'mocks/div', `${config.id}.card.snap`), 'req');
            }

            const runsCount = 100;
            const renderTimeMedian = Array
                .from({length: runsCount}, () => {
                    const start = performance.now();
                    renderer(i18n, opts, data);
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
