import * as chai from 'chai';
import * as sinon from 'sinon';
import * as time from '@src/utils/time';
import { CONTENT_TYPE_HEADER } from '@src/sender/default/const';
import { browserInfo } from '@src/utils/browserInfo';
import { telemetry } from '@src/utils/telemetry/telemetry';
import { useDefaultSender } from '../default';

describe('sender/default', () => {
    const url1 = 'https://example.com';
    const url2 = 'https://example2.com';
    const result = 'body-content';
    const transportException = 'Transport is broken';
    const sandbox = sinon.createSandbox();
    let transportSucceses: any;
    const transport1 = sandbox.stub().callsFake((url: string) => {
        return transportSucceses[url].tr1
            ? Promise.resolve(result)
            : Promise.reject(new Error(transportException));
    });
    const transport2 = sandbox.stub().callsFake((url: string) => {
        return transportSucceses[url].tr2
            ? Promise.resolve(result)
            : Promise.reject(new Error(transportException));
    });
    const createUrlResponses = (
        r1: boolean,
        r2: boolean,
        r3: boolean,
        r4: boolean,
    ) => {
        return {
            [url1]: {
                tr1: r1,
                tr2: r2,
            },
            [`${url1}/1`]: {
                tr1: r1,
                tr2: r2,
            },
            [url2]: {
                tr1: r3,
                tr2: r4,
            },
            [`${url2}/1`]: {
                tr1: r3,
                tr2: r4,
            },
        };
    };
    const transportList = [
        [0, transport1],
        [1, transport2],
    ];
    const urlsList = [url1, url2];
    let timeStub: sinon.SinonStub<any, any>;

    beforeEach(() => {
        timeStub = sandbox.stub(time, 'TimeOne');
        timeStub.returns(() => 100);
    });

    afterEach(() => {
        transport1.resetHistory();
        transport2.resetHistory();
        sandbox.restore();
    });

    it('works correcly if first transport is correct', () => {
        transportSucceses = createUrlResponses(true, true, true, true);
        const sender = useDefaultSender({} as any, transportList as any);
        return sender({ debugStack: [] }, urlsList, {}).then((response) => {
            const [url, transportOptions] = transport1.getCall(0).args;
            chai.expect(response.responseData).to.be.equal(result);
            chai.expect(response.urlIndex).to.be.equal(0);
            chai.expect(url).to.equal(url1);
            chai.expect(transportOptions).to.deep.eq({
                debugStack: [0],
                rBody: undefined,
                rQuery: {},
                verb: 'GET',
            });
            sinon.assert.calledOnce(transport1);
        });
    });

    it('adds redirect and adds browserinfo to url and makes urlencodes rBody', () => {
        transportSucceses = createUrlResponses(true, true, true, true);
        const sender = useDefaultSender({} as any, transportList as any);
        const rBody = 'body';
        const brInfo = browserInfo();
        const tel = telemetry();
        brInfo.setVal('rt', 123);
        return sender(
            {
                debugStack: ['smth'],
                noRedirect: true,
                brInfo,
                telemetry: tel,
            },
            urlsList,
            {
                rBody,
            },
        ).then((response) => {
            const [url, transportOptions] = transport1.getCall(0).args;
            chai.expect(response.responseData).to.be.equal(result);
            chai.expect(response.urlIndex).to.be.equal(0);
            chai.expect(url).to.equal(`${url1}/1`);

            brInfo.setVal('st', 100);

            chai.expect(transportOptions).to.be.deep.eq({
                rHeaders: {
                    [CONTENT_TYPE_HEADER]: 'application/x-www-form-urlencoded',
                },
                verb: 'POST',
                rBody: `site-info=${rBody}`,
                rQuery: {
                    ['browser-info']: brInfo.serialize(),
                    t: 'ti(0)',
                },
                debugStack: ['smth', 0],
            });
            sinon.assert.calledOnce(transport1);
        });
    });

    it('iterates all transports an all urls if they are broken', () => {
        transportSucceses = createUrlResponses(false, false, false, false);
        const sender = useDefaultSender({} as any, transportList as any);
        return sender({ debugStack: ['smth'] }, urlsList, {}).catch((err) => {
            sinon.assert.calledTwice(transport1);
            sinon.assert.calledTwice(transport2);
            chai.expect(err.message).to.eq(transportException);
        });
    });

    it('iterates all transports if all but last is broken', () => {
        transportSucceses = createUrlResponses(false, false, false, true);
        const sender = useDefaultSender({} as any, transportList as any);
        return sender({ debugStack: ['smth'] }, urlsList).then((response) => {
            const [url, transportOptions] = transport2.getCall(1).args;
            sinon.assert.calledTwice(transport1);
            sinon.assert.calledTwice(transport2);
            chai.expect(response.responseData).to.be.equal(result);
            chai.expect(response.urlIndex).to.be.equal(1);
            chai.expect(url).to.equal(url2);
            chai.expect(transportOptions).to.deep.eq({
                debugStack: ['smth', 0, 1, 0, 1],
                rBody: undefined,
                rQuery: {},
                verb: 'GET',
            });
        });
    });
});
