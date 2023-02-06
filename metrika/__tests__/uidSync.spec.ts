/* eslint-env mocha */
import * as sinon from 'sinon';
import * as deviceSyncUtils from '@private/src/providers/deviceSync/utils';
import * as settings from '@src/utils/counterSettings';
import { CounterOptions } from '@src/utils/counterOptions';
import { UID_SYNC_TIME_NAME } from '@private/src/providers/deviceSync/const';
import { useUidSyncProvider } from '../uidSync';
import { MOBILE_UID_SYNC_PROVIDER } from '../const';

describe('uidSyncUtils', () => {
    const sandbox = sinon.createSandbox();

    let counterSettingsStorageGetStub: sinon.SinonStub;
    let syncStub: sinon.SinonStub;

    const win = {} as Window;
    const counterId = '123';
    const counterOptions = {
        id: counterId,
    } as any as CounterOptions;

    beforeEach(() => {
        counterSettingsStorageGetStub = sandbox.stub(
            settings,
            'getCounterSettings',
        );

        syncStub = sandbox.stub(deviceSyncUtils, 'sync');
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('empty settings', () => {
        counterSettingsStorageGetStub.callsFake((_, _1, fn) => {
            return Promise.resolve(fn({ settings: {} }));
        });

        return useUidSyncProvider(win, counterOptions).then(() => {
            sinon.assert.notCalled(syncStub);
        });
    });

    it('sync with settings', () => {
        const testSbp = {
            a: 1,
            b: 2,
        };

        const counterSettings = {
            settings: {
                sbp: testSbp,
            },
        };

        counterSettingsStorageGetStub.callsFake((_, _1, fn) => {
            return Promise.resolve(fn(counterSettings));
        });

        return useUidSyncProvider(win, counterOptions).then(() => {
            sinon.assert.calledWith(syncStub, win, counterSettings, {
                counterOptions,
                provider: MOBILE_UID_SYNC_PROVIDER,
                data: Object.assign({}, testSbp, { c: counterId }),
                lastTimeKey: UID_SYNC_TIME_NAME,
            });
        });
    });
});
