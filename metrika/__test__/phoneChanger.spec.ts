import * as chai from 'chai';
import * as sinon from 'sinon';
import * as cookie from '@src/storage/cookie';
import { noop } from '@src/utils/function';
import * as functionUtils from '@src/utils/function';
import * as counterSettings from '@src/utils/counterSettings';
import * as counterOptions from '@src/utils/counterOptions';
import * as object from '@src/utils/object';
import { PolyPromise } from '@src/utils';
import { CounterOptions } from '@src/utils/counterOptions';
import { ReplaceElement } from '@src/utils/phones';
import { JSDOMWrapper } from '@src/__tests__/utils/jsdom';
import * as phoneChanger from '../phoneChanger';
import * as loggerLib from '../logger';
import { LoggerData } from '../const';
import * as isBrokenPhones from '../isBrokenPhones';

describe('phoneChanger / phoneChanger', () => {
    const { window } = new JSDOMWrapper();
    const { document } = window;
    const sandbox = sinon.createSandbox();
    let logger: LoggerData;

    let rootNode: HTMLElement;
    let node: HTMLElement;
    let link: HTMLAnchorElement;
    beforeEach(() => {
        logger = loggerLib.useLogger(window, {
            id: 123456,
            counterType: '0',
        });
        sandbox.stub(functionUtils, 'memo').callsFake((fn) => fn);

        node = document.createElement('div');
        node.innerHTML = '+8(777)666-55-11';
        link = document.createElement('a');
        link.innerHTML = '+8(777)666-55-22';
        link.href = 'tel:+8(777)666-55-22';
        rootNode = document.createElement('div');
        rootNode.appendChild(node);
        rootNode.appendChild(link);
        document.body.appendChild(rootNode);
    });
    afterEach(() => {
        document.body.removeChild(rootNode);
        sandbox.restore();
    });

    it('setPhonesFromCookie/return on whong cookies', async () => {
        const { setPhonesFromCookie } = phoneChanger;
        const cookieGetValStub = sandbox.stub().returns('');
        sandbox.stub(cookie, 'cookieStorage').callsFake(
            () =>
                ({
                    getVal: cookieGetValStub,
                    setVal: sandbox.spy(),
                    delVal: sandbox.spy(),
                } as any),
        );

        const getPhoneDomReplacerStub = sandbox.stub(
            phoneChanger,
            'getPhoneDomReplacer',
        );
        await setPhonesFromCookie(window, 12345, logger);
        chai.expect(getPhoneDomReplacerStub.called).to.equal(false);
    });

    it('setPhonesFromCookie/calls log', async () => {
        const { setPhonesFromCookie } = phoneChanger;
        const loggerLogStub = sandbox.stub(loggerLib, 'loggerLog');
        const serviceId = '1';
        const cliId = '1234';
        const orderId = '111';
        const settingsStr = JSON.stringify({
            orderId: '111',
            clientId: '1234',
            service_id: '1',
            phones: [['123', '234']],
        });
        const cookieGetValStub = sandbox.stub().returns(settingsStr);
        sandbox.stub(cookie, 'cookieStorage').callsFake(
            () =>
                ({
                    getVal: cookieGetValStub,
                    setVal: sandbox.spy(),
                    delVal: sandbox.spy(),
                } as any),
        );
        const getPhoneDomReplacerStub = sandbox.stub(
            phoneChanger,
            'getPhoneDomReplacer',
        );
        getPhoneDomReplacerStub.returns({
            replacePhonesDom: sandbox.stub().returns(
                PolyPromise.resolve({
                    phones: ['123', '234'],
                    perf: 2,
                }),
            ),
        });
        await setPhonesFromCookie(window, 12345, logger);
        sinon.assert.calledOnce(getPhoneDomReplacerStub);
        const loggerArgs = loggerLogStub.getCall(0).args;
        chai.expect(loggerArgs.length).to.equal(5);
        chai.expect(loggerArgs[1]).to.deep.equal({
            cliId,
            orderId,
            serviceId,
        });
    });

    it('usePhoneChangerProvider - broken', () => {
        const { usePhoneChangerProvider } = phoneChanger;
        sandbox.stub(isBrokenPhones, 'isBrokenPhones').returns(true);
        const provider = usePhoneChangerProvider(window, {
            id: 12345,
            counterType: '0',
        });
        chai.expect(provider).to.equal(noop);
    });
    it('usePhoneChangerProvider - no settings', async () => {
        const { usePhoneChangerProvider } = phoneChanger;
        sandbox.stub(isBrokenPhones, 'isBrokenPhones').returns(false);
        const getPhoneDomReplacerStub = sandbox.stub(
            phoneChanger,
            'getPhoneDomReplacer',
        );
        getPhoneDomReplacerStub.returns({
            replacePhonesDom: sandbox.spy(),
        });
        const loggerSetReadyStub = sandbox.spy();
        const cookieStorage = {
            getVal: sandbox.stub().returns(''),
            setVal: sandbox.spy(),
            delVal: sandbox.spy(),
        };
        sandbox.stub(cookie, 'cookieStorage').returns(cookieStorage);

        sandbox.stub(phoneChanger, 'setPhonesFromCookie');

        sandbox
            .stub(counterSettings, 'getCounterSettings')
            .callsFake((ctx, options, fn: any) => fn());

        sandbox.stub(counterOptions, 'getCounterKey');
        sandbox.stub(object, 'getPath').callsFake((_, id: string) => {
            switch (id) {
                case 'settings.phchange':
                    return {};
                default:
                    return '';
            }
        });
        const provider = await usePhoneChangerProvider(window, {
            id: 12345,
            counterType: '0',
        });
        chai.expect(provider).to.not.equal(noop);
        sinon.assert.notCalled(loggerSetReadyStub);
    });
    it('usePhoneChangerProvider - process', async () => {
        const { usePhoneChangerProvider } = phoneChanger;
        sandbox.stub(isBrokenPhones, 'isBrokenPhones').returns(false);
        const getPhoneDomReplacerStub = sandbox.stub(
            phoneChanger,
            'getPhoneDomReplacer',
        );
        getPhoneDomReplacerStub.returns({
            replacePhonesDom: sandbox.spy(),
        });
        const cookieStorage = {
            getVal: sandbox.stub().returns(''),
            setVal: sandbox.spy(),
            delVal: sandbox.spy(),
        };
        cookieStorage.setVal = sandbox.stub().returns(cookieStorage);
        sandbox.stub(cookie, 'cookieStorage').returns(cookieStorage);

        sandbox.stub(phoneChanger, 'setPhonesFromCookie');

        sandbox
            .stub(counterSettings, 'getCounterSettings')
            .callsFake((ctx, options, fn: any) => fn());
        sandbox.stub(counterOptions, 'getCounterKey');
        sandbox.stub(object, 'getPath').callsFake((_, id: string) => {
            switch (id) {
                case 'settings.phchange':
                    return {};
                case 'clientId':
                    return '1234';
                case 'orderId':
                    return '2345';
                case 'service_id':
                    return '1';
                case 'phones':
                    return [['12345', '23456']];
                default:
                    return '';
            }
        });
        const provider = await usePhoneChangerProvider(window, {
            id: 12345,
            counterType: '0',
        });
        chai.expect(provider).to.not.equal(noop);
        sinon.assert.called(cookieStorage.setVal);
    });

    it('transformPhone / text', async () => {
        const { transformPhone } = phoneChanger;
        const item: ReplaceElement = {
            replaceFrom: '87776665511',
            replaceHTMLNode: node.childNodes[0],
            textOrig: '+8(777)666-55-11',
            replaceTo: '7(222)333-44-12',
            replaceElementType: 'text',
        } as any;

        transformPhone(window, {} as CounterOptions, item);

        chai.expect(rootNode.textContent).to.include('+7(222)333-44-12');
    });

    it('transformPhone / link', async () => {
        const { transformPhone } = phoneChanger;
        const item: ReplaceElement = {
            replaceFrom: '87776665522',
            replaceHTMLNode: link,
            textOrig: 'tel:+8(777)666-55-22',
            replaceTo: '7(222)333-44-23',
            replaceElementType: 'href',
        } as any;

        transformPhone(window, {} as CounterOptions, item);

        chai.expect(link.href).to.eq('tel:+7(222)333-44-23');
    });
});
