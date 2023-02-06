import * as chai from 'chai';
import * as sinon from 'sinon';
import * as sender from '@src/sender';
import * as StorageLocalStorage from '@src/storage/localStorage';
import { CounterOptions } from '@src/utils/counterOptions';
import { SenderInfo } from '@src/sender/SenderInfo';
import { config, host } from '@src/config';
import { includes } from '@src/utils/array';
import { getUserDataStorage } from '../userDataStorage';
import { USER_STORAGE_RESOURCE } from '../const';

describe('userDataStorage', () => {
    const ctx = {} as any as Window;
    const ds = '1234354';
    const cm = '123';
    const almostPromise = { catch: () => {} };

    let localStorageStub: any;
    let senderStub: any;

    let storedDs: string;
    let storedCm: string;
    const counterOptions: CounterOptions = {
        id: 1111,
        counterType: '0',
    };

    beforeEach(() => {
        storedDs = '';
        storedCm = '';
        localStorageStub = sinon.stub(
            StorageLocalStorage,
            'globalLocalStorage',
        );
        localStorageStub.callsFake(() => ({
            getVal: (valName: string) =>
                valName === 'ds' ? storedDs : storedCm,
            setVal: (valName: string, value: any) => {
                valName === 'ds' ? (storedDs = value) : (storedCm = value);
            },
        }));
        senderStub = sinon
            .stub(sender, 'getSender')
            .returns(almostPromise as any);
    });

    afterEach(() => {
        localStorageStub.restore();
        senderStub.restore();
    });

    /* eslint-disable  no-underscore-dangle */
    it('should create storage with expected vars', () => {
        const storage = getUserDataStorage(ctx, { ds, cm }, counterOptions);
        chai.expect(storage.getVal('ds', 'wrong value')).to.eq(ds);
        chai.expect(storage.getVal('cm', 'wrong value')).to.eq(cm);
    });
    it('should get data from local storage if no init params passed', () => {
        storedDs = 'stored DS';
        storedCm = 'stored CM';
        const storage = getUserDataStorage(ctx, { cm }, counterOptions);
        chai.expect(storage.getVal('ds')).to.eq(storedDs);
        chai.expect(storage.getVal('cm')).to.eq(cm);
    });
    it('should set valid value, storte it in Local storage and send to backend', () => {
        senderStub.callsFake(() => (senderInfo: SenderInfo, urls: string[]) => {
            chai.expect(senderInfo).to.deep.eq({
                urlParams: {
                    key: 'ds',
                    value: ds,
                },
            });
            const url = `${config.cProtocol}//${host}/${USER_STORAGE_RESOURCE}`;
            chai.expect(includes(url, urls)).to.be.true;
            return almostPromise;
        });
        const storage = getUserDataStorage(ctx, {}, counterOptions);
        storage.setVal('ds', ds);
        chai.expect(localStorageStub().getVal('ds')).to.eq(ds);
        chai.expect(storage.getVal('ds')).to.eq(ds);
    });
});
