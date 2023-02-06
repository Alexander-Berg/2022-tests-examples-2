import * as chai from 'chai';
import * as sinon from 'sinon';
import { CounterOptions, getCounterKey } from '@src/utils/counterOptions';
import { browserInfo } from '@src/utils/browserInfo';
import { SenderInfo } from '@src/sender/SenderInfo';
import * as storage from '@src/storage/global';
import * as config from '@src/config';
import * as json from '@src/utils/json';
import * as debug from '@src/providers/debugger/dispatchEvent';
import { getRange, cMap } from '@src/utils/array';
import { PAGE_VIEW_BR_KEY } from '@src/providers/hit/const';
import { paramsMiddleware } from '../params';

describe('params middleware', () => {
    const win = () => {
        return {
            JSON,
        } as any as Window;
    };
    const sandbox = sinon.createSandbox();
    const params = { hi: 1 };
    const counterOptions: CounterOptions = {
        id: 332,
        counterType: '0',
    };

    beforeEach(() => {
        sandbox.stub(debug, 'dispatchDebuggerEvent');
    });
    afterEach(() => {
        sandbox.restore();
    });

    it('call callback', () => {
        const winInfo = win();
        const brInfo = browserInfo();
        const senderParams: SenderInfo = {
            brInfo,
            params,
            urlParams: {},
        };
        const middleware = paramsMiddleware(winInfo, 'h', counterOptions);
        if (middleware.beforeRequest) {
            middleware.beforeRequest(senderParams, () => {
                chai.expect(senderParams.rBody).to.be.equal(
                    JSON.stringify(params),
                );
            });
        }
    });
    it('send nothing if stringify broken', (done) => {
        const winInfo = win();
        const brInfo = browserInfo();
        const senderParams: SenderInfo = {
            brInfo,
            params,
        };
        const parseStub = sandbox.stub(json, 'stringify').returns('');
        const middleware = paramsMiddleware(winInfo, 'h', counterOptions);
        if (middleware.beforeRequest) {
            middleware.beforeRequest(senderParams, () => {
                parseStub.restore();
                chai.expect(senderParams.rBody).to.be.not.ok;
                done();
            });
        }
    });
    it('dont call big callback', (done) => {
        const winInfo = win();
        const brInfo = browserInfo();
        brInfo.setVal(PAGE_VIEW_BR_KEY, 1);
        const stubConf = sandbox.stub(config, 'config').value({
            MAX_LEN_SITE_INFO: 1,
        });
        const stubStorage = sandbox.stub(storage, 'getGlobalStorage').returns({
            getVal: () => {
                return {
                    [getCounterKey(counterOptions)]: {
                        params: () => {
                            stubConf.restore();
                            stubStorage.restore();
                            done();
                        },
                    },
                };
            },
        } as any);
        const bigParams = cMap(() => params, getRange(100));
        const senderParams: SenderInfo = {
            brInfo,
            params: bigParams,
            urlParams: {},
        };
        const middleware = paramsMiddleware(winInfo, 'h', counterOptions);
        if (middleware.beforeRequest) {
            middleware.beforeRequest(senderParams, () => {
                chai.expect(senderParams.rBody).to.be.equal(undefined);
            });
        }
        if (middleware.afterRequest) {
            middleware.afterRequest(senderParams, () => {});
        }
    });
});
