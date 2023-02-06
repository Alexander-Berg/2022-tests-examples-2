import * as chai from 'chai';
import * as sinon from 'sinon';
import * as middlewareSender from '@src/sender/middleware';
import { DEFAULT_COUNTER_TYPE } from '@src/providers/counterOptions';
import { browserInfo } from '@src/utils/browserInfo';
import * as isp from '@src/providers/internetServiceProvider/host';
import { useSenderWatch, WATCH_URL_PARAM, WATCH_CLASS_PARAM } from '../watch';

describe('sender/watch', () => {
    const sandbox = sinon.createSandbox();
    let defaultSenderStub: sinon.SinonStub<any, any>;
    let rostelecomStub: sinon.SinonStub<any, any>;
    const responseText = 'this-is-response';
    const senderSpy = sandbox.stub().resolves(responseText);

    beforeEach(() => {
        rostelecomStub = sandbox.stub(isp, 'getITPProviderHostPrefix');
        defaultSenderStub = sandbox.stub(
            middlewareSender,
            'useMiddlewareSender',
        );
        defaultSenderStub.returns(senderSpy);
    });

    afterEach(() => {
        sandbox.restore();
        senderSpy.resetHistory();
    });

    it('sends request for default counter type', () => {
        rostelecomStub.returns('1');
        const counterOptions = {
            id: 123,
            counterType: DEFAULT_COUNTER_TYPE,
        } as any;
        const brInfo = browserInfo();
        const watchUrl = 'http://example.com';
        const senderParams = {
            debugStack: [],
            urlParams: {
                [WATCH_URL_PARAM]: watchUrl,
            },
            brInfo,
        } as any;
        const sender = useSenderWatch({} as any, [], []);
        return sender(senderParams, counterOptions).then((result) => {
            chai.expect(result).to.equal(responseText);
            const [callSenderParams, url, transportOptions] =
                senderSpy.getCall(0).args;

            chai.expect(url).to.equal(`watch/${counterOptions.id}`);
            chai.expect(transportOptions).to.be.deep.eq({
                wmode: false,
            });
            chai.expect(callSenderParams).to.be.deep.eq({
                debugStack: [],
                brInfo,
                hostPrefix: '1',
                urlParams: {
                    [WATCH_URL_PARAM]: watchUrl,
                    charset: 'utf-8',
                },
            });
        });
    });

    it('sends request with type for non-default counter type', () => {
        const nonDefaultCounterType = '666';
        rostelecomStub.returns('');
        const counterOptions = {
            id: 123,
            counterType: nonDefaultCounterType,
        } as any;
        const brInfo = browserInfo();
        const watchUrl = 'http://example.com';
        const senderParams = {
            debugStack: [],
            urlParams: {
                [WATCH_URL_PARAM]: watchUrl,
            },
            brInfo,
        } as any;
        const sender = useSenderWatch({} as any, [], []);
        return sender(senderParams, counterOptions).then((result) => {
            chai.expect(result).to.equal(responseText);
            const [callSenderParams, url, transportOptions] =
                senderSpy.getCall(0).args;
            chai.expect(url).to.equal(`watch/${counterOptions.id}`);
            chai.expect(transportOptions).to.be.deep.eq({
                wmode: false,
            });
            chai.expect(callSenderParams).to.be.deep.eq({
                debugStack: [],
                hostPrefix: '',
                brInfo,
                urlParams: {
                    [WATCH_URL_PARAM]: watchUrl,
                    [WATCH_CLASS_PARAM]: nonDefaultCounterType,
                    charset: 'utf-8',
                },
            });
        });
    });
});
