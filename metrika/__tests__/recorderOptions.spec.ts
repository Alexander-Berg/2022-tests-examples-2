import * as chai from 'chai';
import * as sinon from 'sinon';
import * as ls from '@src/storage/localStorage';
import * as cs from '@src/utils/counterSettings';
import * as isEU from '@src/providers/isEu';
import { taskFork } from '@src/utils/async';
import {
    getRecorderOptions,
    RECORD_WEBVISOR2_FORMS_KEY_PREFIX,
} from '../getRecorderOptions';

describe('getRecorderOptions', () => {
    const ctx = {} as any;
    const counterOptions = {
        childIframe: true,
        id: 123,
        counterType: 'a',
        trustedDomains: ['example.com'],
    } as any;
    let counterSettings: any = {};
    let isEu: boolean | undefined;
    let lsRecordForm: string | null = '0';
    const sandbox = sinon.createSandbox();

    const fakeLocalStorage = {
        getVal: sinon.stub().callsFake((key: string) => {
            if (key === `${RECORD_WEBVISOR2_FORMS_KEY_PREFIX}123:a`) {
                return lsRecordForm;
            }
            return null;
        }),
        setVal: sinon.stub(),
    } as any;
    let settingsPromise: any;

    beforeEach(() => {
        isEu = true;
        lsRecordForm = '0';
        sandbox.stub(isEU, 'isEu').callsFake(() => isEu);
        sandbox.stub(ls, 'globalLocalStorage').returns(fakeLocalStorage);
        counterSettings = {
            settings: {
                x3: 0,
                eu: true,
                webvisor: {
                    forms: false,
                },
            },
        };

        sandbox.stub(cs, 'getCounterSettings').callsFake((_, _1, fn) => {
            settingsPromise = Promise.resolve(fn(counterSettings as any));
            return settingsPromise;
        });
    });

    afterEach(() => {
        fakeLocalStorage.setVal.resetHistory();
        sandbox.restore();
    });

    it('gets counter options from local storage', (done) => {
        getRecorderOptions(
            ctx,
            counterOptions,
        )(
            taskFork(done, (result) => {
                chai.expect(result).to.deep.equal({
                    childIframe: true,
                    isEU: true,
                    recordForms: false,
                    trustedHosts: ['example.com'],
                });
                done();
            }),
        );
    });

    it('gets data from counter settings storage', (done) => {
        isEu = undefined;
        getRecorderOptions(
            ctx,
            counterOptions,
        )(
            taskFork(done, (result) => {
                chai.expect(result).to.deep.equal({
                    childIframe: true,
                    isEU: true,
                    recordForms: false,
                    trustedHosts: ['example.com'],
                });
                sinon.assert.calledWith(
                    fakeLocalStorage.setVal,
                    `${RECORD_WEBVISOR2_FORMS_KEY_PREFIX}123:a`,
                    0,
                );
                done();
            }),
        );
    });

    it("Doesn't record forms if x3=1", (done) => {
        isEu = undefined;
        counterSettings.settings.x3 = 1;
        counterSettings.settings.webvisor.forms = true;
        getRecorderOptions(
            ctx,
            counterOptions,
        )(
            taskFork(done, (result) => {
                chai.expect(result).to.deep.equal({
                    childIframe: true,
                    isEU: true,
                    recordForms: false,
                    trustedHosts: ['example.com'],
                });
                sinon.assert.calledWith(
                    fakeLocalStorage.setVal,
                    `${RECORD_WEBVISOR2_FORMS_KEY_PREFIX}123:a`,
                    0,
                );
                done();
            }),
        );
    });
});
