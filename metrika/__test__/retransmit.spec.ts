import * as chai from 'chai';
import * as sinon from 'sinon';
import * as sender from '@src/sender';
import * as timeUtils from '@src/utils/time';
import * as retransmitMW from '@src/middleware/retransmit';
import * as browserInfo from '@src/utils/browserInfo';
import * as settings from '@src/utils/counterSettings';
import * as errorLoggerUtils from '@src/utils/errorLogger';
import { useRetransmitProvider } from '../retransmit';

describe('provider / retransmit', () => {
    const counterId = 132;
    const sandbox = sinon.createSandbox();
    const counterOptions: any = { id: counterId, counterType: '0' };
    const senderStub = sinon.stub().callsFake(() => Promise.resolve());

    const firstReq = {
        resource: 'r1',
        counterId: '1234',
        counterType: '0',
        params: {
            a: 1,
        },
        postParams: {
            c: 1,
        },
        browserInfo: {
            a: 1,
            b: 1,
        },
        retransmitIndex: '1',
    };
    const secondReq = {
        resource: 'r2',
        counterId: '555',
        counterType: '0',
        params: {
            b: 1,
        },
        postParams: {
            z: 1,
        },
        browserInfo: {
            f: 1,
            r: 1,
        },
        retransmitIndex: '2',
    };
    const thirdReq = {
        resource: 'r3',
        counterId: '1233124',
        counterType: '0',
        params: {
            c: 1,
        },
        postParams: {
            z: 1,
        },
        browserInfo: {
            f: 1,
            r: 1,
        },
        retransmitIndex: '3',
    };

    let getSenderStub: sinon.SinonStub<any, any>;
    let timeStub: sinon.SinonStub<any, any>;
    let retransmitRequestsStub: sinon.SinonStub<any, any>;
    let getCoutnerSettingsStub: sinon.SinonStub<any, any>;
    let brInfoStub: sinon.SinonStub<any, any>;
    let errorLoggerStub: sinon.SinonStub<any, any>;

    beforeEach(() => {
        brInfoStub = sandbox.stub(browserInfo, 'browserInfo');
        errorLoggerStub = sandbox.stub();

        brInfoStub.callsFake((a: any) => a);
        timeStub = sandbox.stub(timeUtils, 'TimeOne');
        timeStub.returns(() => 0);
        getCoutnerSettingsStub = sandbox.stub(settings, 'getCounterSettings');
        getCoutnerSettingsStub.callsFake((_, _1, fn) => {
            return new Promise((resolve) => {
                return resolve(
                    fn({
                        settings: { pcs: '', eu: false },
                        userData: {},
                    }),
                );
            });
        });
        retransmitRequestsStub = sandbox.stub(
            retransmitMW,
            'getRetransmitRequests',
        );
        getSenderStub = sandbox.stub(sender, 'getSender');
        sandbox.stub(errorLoggerUtils, 'errorLogger').returns(errorLoggerStub);
        getSenderStub.returns(senderStub);
        retransmitRequestsStub.returns([firstReq, secondReq, thirdReq]);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('Makes retransmit calls and iterates through stored requests', () => {
        return useRetransmitProvider({} as any, counterOptions).then(() => {
            const senderCalls = senderStub.getCalls();
            chai.expect(senderCalls.length).to.equal(3);

            let [senderOptions, counterOptionsCalled, resource] =
                senderCalls[0].args;
            chai.expect(counterOptionsCalled).to.deep.equal({
                id: firstReq.counterId,
                counterType: firstReq.counterType,
            });
            chai.expect(senderOptions).to.deep.equal({
                rBody: firstReq.postParams,
                brInfo: firstReq.browserInfo,
                urlParams: firstReq.params,
                retransmitIndex: '1',
            } as any);
            chai.expect(resource).to.equal('r1');

            [senderOptions, counterOptionsCalled, resource] =
                senderCalls[1].args;
            chai.expect(counterOptionsCalled).to.deep.equal({
                id: secondReq.counterId,
                counterType: secondReq.counterType,
            });
            chai.expect(senderOptions).to.deep.equal({
                rBody: secondReq.postParams,
                brInfo: secondReq.browserInfo,
                urlParams: secondReq.params,
                retransmitIndex: '2',
            } as any);
            chai.expect(resource).to.equal('r2');

            [senderOptions, counterOptionsCalled, resource] =
                senderCalls[2].args;
            chai.expect(counterOptionsCalled).to.deep.equal({
                id: thirdReq.counterId,
                counterType: thirdReq.counterType,
            });
            chai.expect(senderOptions).to.deep.equal({
                rBody: thirdReq.postParams,
                brInfo: thirdReq.browserInfo,
                urlParams: thirdReq.params,
                retransmitIndex: '3',
            } as any);
            chai.expect(resource).to.equal('r3');
        });
    });

    it('catches transport errors', () => {
        let error: string;
        const buggyPromise = Promise.resolve()
            .then(() => {
                error = `smth ${Math.random()}`;
                return Promise.reject(error);
            })
            .catch((err) => {
                throw err;
            });
        getSenderStub.returns(() => buggyPromise);

        return useRetransmitProvider({} as any, counterOptions).then(() => {
            const actualErrors = errorLoggerStub
                .getCalls()
                .map(({ args }) => args[0]);
            chai.expect(actualErrors.length).to.eq(3);
            actualErrors.forEach((actualError) => {
                chai.expect(actualError).to.eq(error);
            });
        });
    });
});
