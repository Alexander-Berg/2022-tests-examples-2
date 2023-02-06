/* eslint-env mocha */
import * as chai from 'chai';
import * as sinon from 'sinon';
import * as sender from '@src/sender';
import * as location from '@src/utils/location';
import * as browserUtils from '@src/utils/browser';
import * as globalUtils from '@src/storage/global';
import * as time from '@src/utils/time';
import { CounterOptions } from '@src/utils/counterOptions';
import { getUserDataStorage } from '@private/src/providers/deviceSync/userDataStorage';
import * as userDataStorageUtils from '@private/src/providers/deviceSync/userDataStorage';
import { CounterSettings } from '@src/utils/counterSettings';
import { SenderInfo } from '@src/sender/SenderInfo';
import { TransportOptions } from '@src/transport/types';
import { SyncOptions } from '../utils';
import {
    COUNTER_TO_SAVE,
    dataToSendToDevice,
    DEVICESYNC_PROVIDER,
    FULL_PORTS,
    HTTPS_ONLY_PORTS,
} from '../const';
import * as deviceSyncUtils from '../utils';

describe('deviceSyncUtils', () => {
    let getSenderStub: sinon.SinonStub<any, any>;
    const sandbox = sinon.createSandbox();
    let isAndroidStub: sinon.SinonStub;
    let getPlatformStub: sinon.SinonStub;
    let getGlobalStorageStub: sinon.SinonStub;
    let timer: sinon.SinonStub;

    const userStorage = {
        getVal: () => 0,
        setVal: () => {},
    } as any as ReturnType<typeof getUserDataStorage>;

    const win = {} as Window;
    const counterOptions = {
        counterType: '0',
    } as CounterOptions;
    const counterSettings = {} as CounterSettings;

    beforeEach(() => {
        getSenderStub = sandbox.stub(sender, 'getSender');
        sandbox.stub(location, 'getLocation').returns({
            href: 'http://testlocation',
        } as any);

        isAndroidStub = sandbox.stub(browserUtils, 'isAndroid');
        getPlatformStub = sandbox.stub(browserUtils, 'getPlatform');

        timer = sandbox.stub();
        sandbox.stub(time, 'TimeOne').returns(timer);
        sandbox
            .stub(userDataStorageUtils, 'getUserDataStorage')
            .returns(userStorage);
    });

    afterEach(() => {
        sandbox.restore();
    });
    it('checks csp', () => {
        const ctx = {} as Window;
        const counterOpts = {} as any;
        const senderSpy = sinon.spy();
        getSenderStub.callsFake(() => {
            return senderSpy;
        });
        deviceSyncUtils.checkCSP(ctx, counterOpts);
        sinon.assert.calledWith(
            getSenderStub,
            ctx,
            DEVICESYNC_PROVIDER,
            counterOpts,
        );
        sinon.assert.calledWith(senderSpy, {}, [deviceSyncUtils.CSP_DOMAIN]);
    });

    // getHosts
    it('getHosts / android', () => {
        isAndroidStub.returns(true);

        chai.expect(deviceSyncUtils.getHosts(win)).to.eq(FULL_PORTS);
    });

    it('getHosts / ios', () => {
        getPlatformStub.returns('iPhone');

        chai.expect(deviceSyncUtils.getHosts(win)).to.eq(HTTPS_ONLY_PORTS);
    });

    it('getHosts / empty hosts', () => {
        chai.expect(deviceSyncUtils.getHosts(win)).to.deep.eq([]);
    });

    // isEnabled
    it('isEnabled / break timeout', (done) => {
        const syncOptions = {} as SyncOptions;
        getGlobalStorageStub = sandbox.stub(globalUtils, 'getGlobalStorage');
        getGlobalStorageStub.returns({ getVal: () => false });
        timer.returns(0);

        deviceSyncUtils
            .isEnabled(win, timer, userStorage, counterSettings, syncOptions)
            .catch(() => {
                done();
            });
    });

    it('isEnabled / invalid counter type', (done) => {
        const syncOptions = {
            counterOptions: { counterType: '1' } as CounterOptions,
        } as SyncOptions;
        getGlobalStorageStub = sandbox.stub(globalUtils, 'getGlobalStorage');
        getGlobalStorageStub.returns({ getVal: () => false });
        timer.returns(100);

        deviceSyncUtils
            .isEnabled(win, timer, userStorage, counterSettings, syncOptions)
            .catch(() => {
                done();
            });
    });

    it('isEnabled / check csp', () => {
        const syncOptions = {
            counterOptions,
        } as SyncOptions;
        const checkCSPStub = sandbox.stub(deviceSyncUtils, 'checkCSP');

        getGlobalStorageStub = sandbox.stub(globalUtils, 'getGlobalStorage');
        getGlobalStorageStub.returns({ getVal: () => false });
        timer.returns(100);

        return deviceSyncUtils
            .isEnabled(win, timer, userStorage, counterSettings, syncOptions)
            .then(() => {
                sinon.assert.called(checkCSPStub);
            });
    });

    // requestLocalHosts
    it('requestLocalHosts should pass right parameters to sender test', () => {
        const host = "'(-$&$&$'";
        const port = 11;
        const syncOptions = {
            provider: DEVICESYNC_PROVIDER,
            counterOptions: COUNTER_TO_SAVE,
        } as SyncOptions;

        const isHttps = 0 as const;
        getSenderStub.callsFake(
            () =>
                (
                    senderInfo: SenderInfo,
                    urls: string[],
                    _opt?: TransportOptions,
                ): Promise<any> => {
                    if (senderInfo) {
                        chai.expect(senderInfo).to.be.deep.eq(
                            dataToSendToDevice,
                        );
                    }
                    const url = `http://127.0.0.1:${port}/p`;
                    chai.expect(urls).to.include(url);
                    chai.expect(_opt && _opt.withCreds === false).to.be.true;
                    chai.expect(_opt && _opt.returnRawResponse).to.be.true;
                    return Promise.resolve({});
                },
        );
        return deviceSyncUtils.requestLocalHosts(
            window,
            [[[host, port, isHttps]]],
            syncOptions,
        );
    });

    it('save / should pass right parameters to sender', () => {
        const dataString = 'some string';
        const dataPort = 123;
        const testTime = 100;
        getSenderStub.callsFake(
            () =>
                (
                    senderInfo: SenderInfo,
                    counterOpts: CounterOptions,
                ): Promise<any> => {
                    chai.expect(counterOpts).to.be.deep.eq(COUNTER_TO_SAVE);
                    chai.expect(
                        !!senderInfo &&
                            !!senderInfo.brInfo &&
                            !!senderInfo.urlParams,
                    ).to.be.true;
                    if (
                        !!senderInfo &&
                        !!senderInfo.brInfo &&
                        !!senderInfo.urlParams
                    ) {
                        chai.expect(senderInfo.brInfo.getVal('di')).to.be.equal(
                            dataString,
                        );
                        chai.expect(
                            senderInfo.brInfo.getVal('dit'),
                        ).to.be.equal(testTime);
                        chai.expect(
                            senderInfo.brInfo.getVal('dip'),
                        ).to.be.equal(dataPort);
                        chai.expect(
                            senderInfo.urlParams['page-url'],
                        ).to.be.equal('http://testlocation');
                    }
                    return Promise.resolve();
                },
        );
        return deviceSyncUtils.save(window, dataString, dataPort, testTime);
    });

    // sync
    it('sync / should not call requestLocalHosts if empty hosts', () => {
        sandbox.stub(deviceSyncUtils, 'getHosts').returns([]);
        const isEnabledStub = sandbox.stub(deviceSyncUtils, 'isEnabled');
        const requestLocalHostsStub = sandbox.stub(
            deviceSyncUtils,
            'requestLocalHosts',
        );

        return deviceSyncUtils
            .sync(win, counterSettings, { counterOptions } as SyncOptions)
            .then(() => {
                sinon.assert.notCalled(isEnabledStub);
                sinon.assert.notCalled(requestLocalHostsStub);
            })
            .catch(chai.assert.fail);
    });

    it('sync / should not call requestLocalHosts if not enabled', () => {
        sandbox.stub(deviceSyncUtils, 'getHosts').returns(FULL_PORTS);
        const isEnabledStub = sandbox.stub(deviceSyncUtils, 'isEnabled');
        const requestLocalHostsStub = sandbox.stub(
            deviceSyncUtils,
            'requestLocalHosts',
        );

        isEnabledStub.rejects();

        return deviceSyncUtils
            .sync(win, counterSettings, { counterOptions } as SyncOptions)
            .then(() => {
                sinon.assert.called(isEnabledStub);
                sinon.assert.notCalled(requestLocalHostsStub);
            })
            .catch(chai.assert.fail);
    });

    it('sync / should call requestLocalHosts', () => {
        const isEnabledStub = sandbox.stub(deviceSyncUtils, 'isEnabled');
        const hosts = FULL_PORTS;
        const syncOptions = { counterOptions } as SyncOptions;
        const makeRequestStub = sandbox.stub(deviceSyncUtils, 'makeRequest');

        isEnabledStub.resolves();
        sandbox.stub(deviceSyncUtils, 'getHosts').returns(hosts);

        return deviceSyncUtils
            .sync(win, counterSettings, syncOptions)
            .then(() => {
                sinon.assert.called(isEnabledStub);
                chai.expect(makeRequestStub.getCall(0).args[0]).to.eq(win);
                chai.expect(makeRequestStub.getCall(0).args[1]).to.eq(hosts);
                chai.expect(makeRequestStub.getCall(0).args[4]).to.eq(
                    syncOptions,
                );
            })
            .catch(chai.assert.fail);
    });
});
