import * as chai from 'chai';
import * as sinon from 'sinon';
import * as eventUtils from '@src/utils/events';
import * as timeUtils from '@src/utils/time';
import * as browserUtils from '@src/utils/browser';
import { clearUserTimeDefer, setUserTimeDefer } from '../userTimeDefer';

const timeoutMock = () => {
    let timeoutsHash: { [id: number]: [Function, number] } = {};
    let timeoutId = 0;
    let now = 0;

    return {
        setTimeout: (callback: Function, time: number) => {
            timeoutId += 1;
            timeoutsHash[timeoutId] = [callback, time];

            return timeoutId;
        },
        clearTimeout: (id: number) => {
            delete timeoutsHash[id];
        },
        resetTimeouts: () => {
            now = 0;
            timeoutId = 0;
            timeoutsHash = {};
        },
        getNowTime: () => {
            return now;
        },
        makeTimePass: (time: number) => {
            now += time;
            Object.keys(timeoutsHash).forEach((id) => {
                const [callback, timeoutTime] = timeoutsHash[id as any];
                if (timeoutTime <= time) {
                    callback();
                    delete timeoutsHash[id as any];
                }

                timeoutsHash[id as any] = [callback, timeoutTime - time] as [
                    Function,
                    number,
                ];
            });
        },
    };
};

describe('userTimeDefer', () => {
    let timesCalled = 0;
    const sandbox = sinon.createSandbox();
    const callback = () => {
        timesCalled += 1;
    };
    let timeUtilsStub: any;
    let isIEStub: any;
    let eventsStub: any;

    beforeEach(() => {
        isIEStub = sandbox.stub(browserUtils, 'isIE');
        timeUtilsStub = sandbox.stub(timeUtils, 'TimeOne');
        eventsStub = sandbox.stub(eventUtils, 'cEvent');

        timesCalled = 0;
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('Just sets regular timeout for IE and clears it', () => {
        isIEStub.returns(true);
        timeUtilsStub.returns(() => 100);
        const ctx: any = timeoutMock();

        const { id } = setUserTimeDefer(ctx, callback, 100);
        clearUserTimeDefer(ctx, id);
        ctx.makeTimePass(1000);
        chai.expect(timesCalled).to.equal(0);

        setUserTimeDefer(ctx, callback, 100);
        ctx.makeTimePass(1000);
        chai.expect(timesCalled).to.equal(1);
    });

    it('Removes callback from non IE window', () => {
        isIEStub.returns(false);
        timeUtilsStub.returns(() => 100);
        eventsStub.returns({
            on: () => {},
            off: () => {},
        } as any);
        const ctx: any = timeoutMock();
        const { id } = setUserTimeDefer(ctx, callback, 100);
        clearUserTimeDefer(ctx, id);
        ctx.makeTimePass(1000);

        chai.expect(timesCalled).to.equal(0);
    });

    it('Works normally with blur and other events', () => {
        const ctx: any = timeoutMock();
        const eventsHash: Record<string, Function> = {};
        isIEStub.returns(false);
        timeUtilsStub.returns(() => ctx.getNowTime());
        eventsStub.returns({
            on: (target: any, eventNames: string[], cb: Function) => {
                eventNames.forEach((name) => {
                    eventsHash[name] = cb;
                });
            },
            un: () => {},
        } as any);
        ctx.document = {};

        setUserTimeDefer(ctx, callback, 1000);
        ctx.makeTimePass(300);
        eventsHash.scroll();
        chai.expect(timesCalled).to.equal(0);

        ctx.makeTimePass(100);
        eventsHash.blur();
        chai.expect(timesCalled).to.equal(0);

        eventsHash.focus();
        chai.expect(timesCalled).to.equal(0);

        ctx.makeTimePass(600);
        chai.expect(timesCalled).to.equal(1);
    });
});
