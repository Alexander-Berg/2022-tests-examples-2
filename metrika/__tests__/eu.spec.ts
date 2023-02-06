import * as chai from 'chai';
import * as sinon from 'sinon';
import * as globalStorage from '@src/storage/global';
import { CounterOptions } from '@src/utils/counterOptions';
import { IS_EU_CONFIG_KEY } from '@src/middleware/counterFirstHit';
import { IS_EU_BR_KEY } from '../keys';
import { BRINFO_FLAG_GETTERS } from '../index';

describe('watchSyncFlags eu', () => {
    const winInfo = {} as any;
    const counterId = '1';
    const counterOpt: CounterOptions = {
        id: parseInt(counterId, 10),
        counterType: '0',
    };
    const senderParams: any = {};
    const sandbox = sinon.createSandbox();
    let globalEu: any;
    let getGlobalValSpy: any;

    beforeEach(() => {
        getGlobalValSpy = sandbox.spy(() => globalEu);
        sandbox.stub(globalStorage, 'getGlobalStorage').returns({
            getVal: getGlobalValSpy,
        } as any);
    });

    afterEach(() => {
        sandbox.resetHistory();
        sandbox.restore();
    });

    const check = (value: number | undefined) => {
        globalEu = value;
        const result = BRINFO_FLAG_GETTERS[IS_EU_BR_KEY](
            winInfo,
            counterOpt,
            senderParams,
        );
        chai.expect(getGlobalValSpy.calledWith(IS_EU_CONFIG_KEY)).to.be.ok;
        chai.expect(result).to.be.equal(globalEu);
    };

    it(`has ${IS_EU_BR_KEY}`, () => {
        check(1);
    });

    it(`has not ${IS_EU_BR_KEY}`, () => {
        check(undefined);
    });
});
