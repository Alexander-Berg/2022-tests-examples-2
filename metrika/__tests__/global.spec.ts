/* eslint-env mocha */
import * as chai from 'chai';
import { globalStorage, GlobalCtx, GlobalStorage } from '..';
import { yandexNamespace, metrikaNamespace } from '../global';

describe('GlobalStorage', () => {
    let storage: GlobalCtx;
    let inStorage: Window;
    let gs: GlobalStorage;

    beforeEach(() => {
        storage = {};
        inStorage = storage as Window;
        gs = globalStorage(inStorage);
    });
    /* eslint-disable  no-underscore-dangle */
    it('should create Ya namespace', () => {
        chai.expect(storage).to.have.property(yandexNamespace);
        chai.expect(storage[yandexNamespace]).to.have.property(
            metrikaNamespace,
        );
    });
    it('should set var to gs', () => {
        gs.setVal('a', 1);
        if (storage.Ya && storage.Ya._metrika) {
            chai.expect(storage.Ya._metrika.a).to.eq(1);
        } else {
            chai.assert.fail();
        }
    });
    it('should setSafe var to gs', () => {
        gs.setSafe('a', 2);
        if (storage.Ya && storage.Ya._metrika) {
            chai.expect(storage.Ya._metrika.a).to.eq(2);
        } else {
            chai.assert.fail();
        }
    });
    it('should setSafe var to gs', () => {
        gs.setVal('a', 1);
        gs.setSafe('a', 2);
        if (storage.Ya && storage.Ya._metrika) {
            chai.expect(storage.Ya._metrika.a).to.eq(1);
        } else {
            chai.assert.fail();
        }
    });
    it('should get var from gs', () => {
        const val = 0;
        gs.setVal('a', val);
        const i = gs.getVal('a');
        chai.expect(i).to.eq(val);
    });
    it('should get undef var from gs', () => {
        const val = 10;
        const i = gs.getVal('a', val);
        chai.expect(i).to.eq(val);
    });
});
