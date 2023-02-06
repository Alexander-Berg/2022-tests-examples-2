/* eslint-env mocha */
import * as chai from 'chai';
import * as errorLogger from '@src/utils/errorLogger/handleError';
import * as sinon from 'sinon';
import { CounterOptions } from '@src/utils/counterOptions';
import * as settings from '@src/utils/counterSettings';
import * as time from '@src/utils/time';
import * as globalStorage from '@src/storage/global';
import * as browser from '@src/utils/browser';
import * as location from '@src/utils/location';
import * as userDataStorage from '@private/src/providers/deviceSync/userDataStorage';
import { getTimestamp, getMin } from '@src/utils/time';
import * as debugConsole from '@src/providers/debugConsole';
import { taskOf } from '@src/utils/async';
import { HostInfo, HTTPS_ONLY_PORTS } from '../const';
import * as deviceSyncUtils from '../utils';
import * as deviceSync from '../deviceSync';

describe('useDeviceSyncProvider', () => {
    const fakeWindow = {} as any as Window;
    const sandbox = sinon.createSandbox();
    let counterSettingsStorageGetStub: sinon.SinonStub;
    let TimeStub: any;
    let getPlatformStub: any;
    let isAndroidStub: any;
    let isDeviceSyncDomainStub: any;
    let getUserDataStorageStub: any;
    let requestLocalHostsStub: any;
    let checkCSP: sinon.SinonStub<any, any>;

    let saveStub: any;
    let getGlobalStorageStub: any;

    const deviceHosts = HTTPS_ONLY_PORTS;
    const deviceData = 'device responce';
    const deviceUrlIndex = 1;

    const COUNTER_TYPE_OK = '0';
    const testPort = 123123;

    let isAndroid = false;
    let platform = 'iPhone';
    let isDeviceDomain = false;
    let isInProgress = false;
    let hasCSP = false;
    let reportStub: sinon.SinonStub<any, any>;

    beforeEach(() => {
        isAndroid = false;
        reportStub = sandbox
            .stub(errorLogger, 'reportError')
            .callsFake((a, b, error) => {
                throw error;
            });
        platform = 'iPhone';
        isDeviceDomain = false;
        isInProgress = false;
        TimeStub = sandbox.stub(time, 'TimeOne');
        TimeStub.returns((fn: Function) => {
            if (fn === getTimestamp) {
                return 'timestamp';
            }
            if (fn === getMin) {
                return 100;
            }
            return 0;
        });

        getPlatformStub = sandbox.stub(browser, 'getPlatform');
        getPlatformStub.callsFake(() => platform);

        isAndroidStub = sandbox.stub(browser, 'isAndroidWebView');
        isAndroidStub.callsFake(() => isAndroid);

        isDeviceSyncDomainStub = sandbox.stub(location, 'isDeviceSyncDomain');
        isDeviceSyncDomainStub.callsFake(() => isDeviceDomain);

        counterSettingsStorageGetStub = sandbox.stub(
            settings,
            'getCounterSettings',
        );
        counterSettingsStorageGetStub.callsFake((_, _1, fn) => {
            return Promise.resolve(
                fn({
                    settings: {
                        pcs: '0',
                        eu: true,
                    },
                    userData: {
                        ds: '10',
                    },
                }),
            );
        });

        requestLocalHostsStub = sandbox.stub(
            deviceSyncUtils,
            'requestLocalHosts',
        );
        checkCSP = sandbox.stub(deviceSyncUtils, 'checkCSP');
        checkCSP.callsFake(() => {
            return hasCSP ? Promise.reject() : Promise.resolve();
        });
        requestLocalHostsStub.callsFake((ctx: Window, hosts: HostInfo[][]) => {
            chai.expect(hosts).to.be.equal(deviceHosts);
            return taskOf({
                responseData: deviceData,
                urlIndex: deviceUrlIndex,
                host: ['', testPort, 1] as HostInfo,
            });
        });

        saveStub = sandbox.stub(deviceSyncUtils, 'save');
        saveStub.callsFake((ctx: Window, data: any, port: number) => {
            chai.expect(data).to.be.equal(deviceData);
            chai.expect(port).to.be.equal(testPort);
            return Promise.resolve('done');
        });

        getUserDataStorageStub = sandbox.stub(
            userDataStorage,
            'getUserDataStorage',
        );
        getUserDataStorageStub.returns({
            getVal: sinon.fake.returns('10'),
            setVal: sinon.fake.resolves(''),
        });

        getGlobalStorageStub = sandbox.stub(globalStorage, 'getGlobalStorage');
        getGlobalStorageStub.returns({
            getVal: sinon.stub().callsFake(() => isInProgress),
            setVal: sinon.fake(),
            setSafe: sinon.fake(),
        });

        sandbox.stub(debugConsole, 'consoleLog');
    });

    afterEach(() => {
        sandbox.restore();
    });
    const getCounterId = () => {
        return Math.floor(Math.random() * 100);
    };

    it('should call requestLocalHosts and save in all good environment at yandex domains', () => {
        isDeviceDomain = true;
        return deviceSync
            .useRawDeviceSyncProvider(fakeWindow, {
                counterType: COUNTER_TYPE_OK,
                id: getCounterId(),
            })
            .then(() => {
                sinon.assert.calledOnce(requestLocalHostsStub);
                sinon.assert.calledOnce(saveStub);
            });
    });

    it('should call requestLocalHosts and save in all good environment at non-yandex domains if randomly chosen', () => {
        platform = 'iPad';

        return deviceSync
            .useRawDeviceSyncProvider(fakeWindow, {
                counterType: COUNTER_TYPE_OK,
                id: getCounterId(),
            })
            .then(() => {
                sinon.assert.calledOnce(requestLocalHostsStub);
                sinon.assert.calledOnce(saveStub);
            });
    });

    it('should avoid requestLocalHosts calling if domain has csp', () => {
        hasCSP = true;
        return deviceSync
            .useRawDeviceSyncProvider(fakeWindow, {
                counterType: COUNTER_TYPE_OK,
                id: getCounterId(),
            })
            .then(() => {
                sinon.assert.notCalled(requestLocalHostsStub);
                sinon.assert.notCalled(saveStub);
            });
    });

    it('should avoid requestLocalHosts calling if in progress flag is set', () => {
        isDeviceDomain = true;
        isInProgress = true;
        return deviceSync
            .useRawDeviceSyncProvider(fakeWindow, {
                counterType: COUNTER_TYPE_OK,
                id: getCounterId(),
            })
            .then(() => {
                sinon.assert.notCalled(requestLocalHostsStub);
                sinon.assert.notCalled(saveStub);
            });
    });

    it('should avoid requestLocalHosts calling if not mobile Safari and  not Android', () => {
        isDeviceDomain = true;
        platform = 'random';

        return deviceSync
            .useRawDeviceSyncProvider(fakeWindow, {
                counterType: COUNTER_TYPE_OK,
                id: getCounterId(),
            })
            .then(() => {
                chai.expect(requestLocalHostsStub.calledOnce).to.be.false;
                chai.expect(saveStub.calledOnce).to.be.false;
            });
    });

    it('should avoid requestLocalHosts calling at not Yandex domain and not randomly choosen', () => {
        return deviceSync
            .useRawDeviceSyncProvider(fakeWindow, {
                counterType: COUNTER_TYPE_OK,
                id: getCounterId(),
            })
            .then(() => {
                chai.expect(requestLocalHostsStub.calledOnce).to.be.false;
                chai.expect(saveStub.calledOnce).to.be.false;
            });
    });

    it('should call requestLocalHosts and do not call save if receives a default data', () => {
        isDeviceDomain = true;
        reportStub.callsFake(() => {});
        requestLocalHostsStub.callsFake(
            (
                ctx: Window,
                counterOptions: CounterOptions,
                hosts: HostInfo[][],
            ) => {
                chai.expect(hosts).to.be.equal(deviceHosts);
                return taskOf({
                    responseData: { settings: {}, userData: {} },
                    urlIndex: deviceUrlIndex,
                });
            },
        );

        return deviceSync
            .useRawDeviceSyncProvider(fakeWindow, {
                counterType: COUNTER_TYPE_OK,
                id: getCounterId(),
            })
            .then(
                () => {
                    sinon.assert.calledOnce(requestLocalHostsStub);
                    sinon.assert.notCalled(saveStub);
                },
                () => {
                    // empty
                },
            );
    });
});
