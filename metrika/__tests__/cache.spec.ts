import * as sinon from 'sinon';
import { initCC } from '../cache';
import { CC_VAR, CC_VAR_DEFAULT } from '../const';

describe('crossdomin cache', () => {
    let ls: {
        getVal: sinon.SinonStub<any, any>;
        setVal: sinon.SinonStub<any, any>;
    };
    let gl: {
        setVal: sinon.SinonStub<any, any>;
    };
    beforeEach(() => {
        ls = {
            getVal: sinon.stub(),
            setVal: sinon.stub(),
        };
        gl = {
            setVal: sinon.stub(),
        };
    });

    it('reads data from ls and set default', () => {
        initCC({} as any, {} as any, gl as any, ls as any);
        sinon.assert.calledWith(ls.setVal, CC_VAR, CC_VAR_DEFAULT);
    });
    it('reads data from ls and set stored', () => {
        const testVal = 'test';
        ls.getVal.withArgs(CC_VAR).returns(testVal);
        initCC({} as any, {} as any, gl as any, ls as any);
        sinon.assert.calledWith(gl.setVal, CC_VAR, testVal);
    });
});
