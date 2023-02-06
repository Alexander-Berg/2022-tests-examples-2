import * as chai from 'chai';
import * as sinon from 'sinon';
import { metrikaNamespace, yandexNamespace } from '@src/storage/global';
import * as functionUtils from '@src/utils/function';
import * as events from '@src/utils/events';
import * as global from '@src/storage/global';
import * as fnv32a from '@src/utils/fnv32a';
import { WV2_STOP_RECORDER_KEY } from '@private/src/providers/webvisor2/const';
import {
    isAllowedOrigin,
    isAllowedResource,
    remoteControl,
    onMessage,
    REMOTE_CONTROL,
    isAllowedExternalOrigin,
    getResourceUrl,
} from '../remoteControl';

describe('isAllowedStatic', () => {
    const origins = [
        'yastatic.net/s3/metrika',
        's3.mds.yandex.net/internal-metrika-betas',
        'username.dev.webvisor.com',
        'username.dev.metrika.yandex.ru',
    ];

    for (let i = 0; i < origins.length; i += 1) {
        const origin = origins[i];

        it(`works with ${origin}`, () => {
            chai.expect(isAllowedResource(`https://${origin}/1.js`)).to.be.true;
            chai.expect(
                isAllowedResource(`https://${origin}/1.2.3/1.js`),
                'одиночные точки',
            ).to.be.true;
            chai.expect(
                isAllowedResource(`https://${origin}/any/number/1.js`),
                'любой подпуть',
            ).to.be.true;

            chai.expect(isAllowedResource(`http://${origin}/1.js`), 'http').to
                .be.false;
            chai.expect(
                isAllowedResource(`https://${origin}aaa/1.js`),
                'проверка на путь',
            ).to.be.false;
            chai.expect(
                isAllowedResource(`https://${origin}/evil?1.js`),
                'проверка на query params',
            ).to.be.false;
            chai.expect(
                isAllowedResource(`https://${origin}/1.jssss`),
                'проверка на расширение файла',
            ).to.be.false;
            chai.expect(
                isAllowedResource(`https://sub.${origin}/1.js`),
                'проверка на субдомен',
            ).to.be.false;
            chai.expect(
                isAllowedResource(`https://${origin}/../../1.js`),
                'проверка на .. в пути',
            ).to.be.false;
        });
    }
});

describe('isAllowedOrigin', () => {
    const shouldMatch = [
        'http://webvisor.com',
        'http://webvisor.com/',
        'http://.sub.domain.webvisor.com/',
        'http://.sub.domain.webvisor.com',
        'https://test.metrika.yandex.ru',
        'https://metrika.yandex.ru',
        'https://metrica.yandex.com',
    ];
    const shouldNotMatch = [
        'https://webvisor.com',
        'https://webvisor.com/',
        'https://sub.domain.webvisor.com',
        'http://webvisor.com/path/to/smth',
        'http://metrika.yandex.ru',
    ];

    it('shouldMatch', () => {
        shouldMatch.forEach((origin) => {
            chai.expect(
                isAllowedOrigin(origin),
                `Origin ${origin} should be allowed`,
            ).to.be.true;
        });
    });
    it('shouldNotMatch', () => {
        shouldNotMatch.forEach((origin) => {
            chai.expect(
                isAllowedOrigin(origin),
                `Origin ${origin} should NOT be allowed`,
            ).to.be.false;
        });
    });

    it('Allow iframe-toloka', () => {
        chai.expect(isAllowedExternalOrigin('https://iframe-toloka.com')).to.be
            .true;
        chai.expect(isAllowedExternalOrigin('https://iframe-toloka.com/')).to.be
            .true;
        chai.expect(isAllowedExternalOrigin('https://toloka.yandex.ru/')).to.be
            .false;
    });
});

describe('getResourceUrl', () => {
    it('Only allowed langs', () => {
        ['ru', 'en', 'tr'].forEach((lang) => {
            chai.expect(
                getResourceUrl({ lang, appVersion: '1.2.3', fileId: 'button' }),
            ).to.eq(
                `https://yastatic.net/s3/metrika/1.2.3/form-selector/button_${lang}.js`,
            );
        });
        chai.expect(
            getResourceUrl({
                lang: 'de',
                appVersion: '1.2.3',
                fileId: 'button',
            }),
        ).to.eq('');
    });

    it('Only allowed ids', () => {
        ['button', 'form', 'phone'].forEach((fileId) => {
            chai.expect(
                getResourceUrl({ lang: 'ru', appVersion: '1.2.3', fileId }),
            ).to.eq(
                `https://yastatic.net/s3/metrika/1.2.3/form-selector/${fileId}_ru.js`,
            );
        });
        chai.expect(
            getResourceUrl({ lang: 'ru', appVersion: '1.2.3', fileId: '' }),
        ).to.eq('');
    });

    it('Validate version', () => {
        chai.expect(
            getResourceUrl({
                lang: 'ru',
                appVersion: '11.22.33',
                fileId: 'button',
            }),
        ).to.eq(
            'https://yastatic.net/s3/metrika/11.22.33/form-selector/button_ru.js',
        );
        chai.expect(
            getResourceUrl({
                lang: 'ru',
                appVersion: '1684933',
                fileId: 'button',
            }),
        ).to.eq(
            'https://yastatic.net/s3/metrika/1684933/form-selector/button_ru.js',
        );
        chai.expect(
            getResourceUrl({
                lang: 'ru',
                appVersion: 'invalidVer',
                fileId: 'button',
            }),
        ).to.eq('https://yastatic.net/s3/metrika/form-selector/button_ru.js');
        chai.expect(
            getResourceUrl({ lang: 'ru', appVersion: '1.a', fileId: 'button' }),
        ).to.eq('https://yastatic.net/s3/metrika/1/form-selector/button_ru.js');
        chai.expect(
            getResourceUrl({
                lang: 'ru',
                appVersion: '/.//.',
                fileId: 'button',
            }),
        ).to.eq('https://yastatic.net/s3/metrika/form-selector/button_ru.js');
    });

    it('Beta url', () => {
        chai.expect(
            getResourceUrl({
                lang: 'ru',
                appVersion: '1.2.3',
                fileId: 'button',
                beta: true,
            }),
        ).to.eq(
            'https://s3.mds.yandex.net/internal-metrika-betas/1.2.3/form-selector/button_ru.js',
        );
    });
});

describe('remoteControl', () => {
    const stopRecorer = sinon.stub();
    const eventHandlerUnsubscribe = sinon.stub();
    const eventHandlerOn = sinon.stub().returns(eventHandlerUnsubscribe);
    const eventHandlerUn = sinon.stub();
    const getGlobalValue = sinon.stub();
    const setGlobalValue = sinon.stub();
    const hashResult = 100;
    const sandbox = sinon.createSandbox();

    let cEvent: any;

    beforeEach(() => {
        sandbox.stub(fnv32a, 'fnv32a').returns(hashResult);
        sandbox
            .stub(functionUtils as any, 'bindArg') // as any потому что падает из-за рекурсионных типов
            .callsFake((arg: any, callback: (...args: any[]) => any) => {
                return callback;
            });
        getGlobalValue.withArgs(REMOTE_CONTROL).returns(false);
        getGlobalValue.withArgs(WV2_STOP_RECORDER_KEY).returns(stopRecorer);
        sandbox.stub(global, 'getGlobalStorage').returns({
            getVal: getGlobalValue,
            setSafe: setGlobalValue,
            setVal: setGlobalValue,
        } as any);
        cEvent = sandbox.stub(events, 'cEvent').returns({
            on: eventHandlerOn,
            un: eventHandlerUn,
        });
    });

    afterEach(() => {
        eventHandlerUnsubscribe.resetHistory();
        eventHandlerOn.resetHistory();
        eventHandlerUn.resetHistory();
        getGlobalValue.resetHistory();
        setGlobalValue.resetHistory();
        stopRecorer.resetHistory();
        sandbox.restore();
    });

    it('sets event listener only once', () => {
        const windowStub = {
            [yandexNamespace]: {
                [metrikaNamespace]: {},
            },
        } as unknown as Window;
        const errorMessage = 'addEventListener was called with wrong arguments';

        remoteControl(windowStub);

        chai.expect(cEvent.called).to.be.true;
        chai.expect(
            eventHandlerOn.getCall(0).args[1],
            errorMessage,
        ).to.deep.equal(['message']);
        chai.expect(eventHandlerOn.getCall(0).args[2], errorMessage).to.equal(
            onMessage,
        );
        getGlobalValue.withArgs(REMOTE_CONTROL).returns(true);

        remoteControl(windowStub);
        remoteControl(windowStub);

        chai.assert(
            eventHandlerOn.calledOnce,
            'addEventListener should be called only once',
        );
    });
});
