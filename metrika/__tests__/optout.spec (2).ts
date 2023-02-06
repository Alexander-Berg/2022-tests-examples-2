import * as chai from 'chai';
import * as sinon from 'sinon';
import * as storage from '@src/storage/global';
import * as metrikaPlayer from '@src/utils/metrikaPlayer';
import { isOptoutEnabled, OPTOUT_KEY } from '@src/providers/optout';

describe('providers / OptOut', () => {
    const ctx = {} as any as Window;

    let getValSpy: any;
    let storageStub: any;
    let optoutValue: any;
    let isMetrikaPlayer: any;

    beforeEach(() => {
        getValSpy = sinon.spy(() => optoutValue);
        storageStub = sinon.stub(storage, 'getGlobalStorage').returns({
            getVal: getValSpy,
        } as any);
        isMetrikaPlayer = sinon
            .stub(metrikaPlayer, 'isMetrikaPlayer')
            .returns(false);
    });

    afterEach(() => {
        storageStub.restore();
        getValSpy.resetHistory();
        isMetrikaPlayer.restore();
    });

    it('disabled optout returns false', () => {
        optoutValue = undefined;

        const result = isOptoutEnabled(ctx);
        chai.expect(getValSpy.calledWith(OPTOUT_KEY)).to.be.ok;
        chai.expect(result).to.be.false;
    });

    it('enabled optout return true', () => {
        optoutValue = true;

        const result = isOptoutEnabled(ctx);
        chai.expect(getValSpy.calledWith(OPTOUT_KEY)).to.be.ok;
        chai.expect(result).to.be.true;
    });

    it('should switch optout on inside metrika player', () => {
        optoutValue = false;
        isMetrikaPlayer.returns(true);

        const result = isOptoutEnabled(ctx);
        chai.expect(getValSpy.calledWith(OPTOUT_KEY)).to.be.ok;
        chai.expect(result).to.be.true;
    });
});
