import * as chai from 'chai';
import * as sinon from 'sinon';
import * as eventUtils from '@src/utils/events';
import { browserInfo } from '@src/utils/browserInfo';
import { prerender } from '../prerender';

describe('Prerender', () => {
    let eventsStub: any;
    const onSpy = sinon.spy();
    const unSpy = sinon.spy();

    beforeEach(() => {
        eventsStub = sinon.stub(eventUtils, 'cEvent').returns({
            on: onSpy,
            un: unSpy,
        } as any);
    });

    afterEach(() => {
        onSpy.resetHistory();
        unSpy.resetHistory();
        eventsStub.restore();
    });

    it('pass if visibilitystate null', () => {
        const next = sinon.spy();
        const ctx: any = {
            document: {},
        };
        const middleware = prerender(ctx, 'h', {
            id: 1,
            counterType: '1',
        });

        middleware.beforeRequest!(
            {
                brInfo: browserInfo(),
            },
            next,
        );
        chai.expect(next.called).to.be.ok;
    });

    it('do nothing if empty brInfo just pass', () => {
        const next = sinon.spy();
        const middleware = prerender(
            { document: { visibilityState: 'prerender' } } as any,
            'h',
            { id: 1, counterType: '1' },
        );

        middleware.beforeRequest!({}, next);
        chai.expect(next.called).to.be.ok;
    });

    it('waits for visibility state not prenender', () => {
        const next = sinon.spy();
        const ctx = { document: { visibilityState: 'prerender' } } as any;
        const senderParams = {
            brInfo: browserInfo({}),
        };
        const middleware = prerender(ctx, 'h', {
            id: 1,
            counterType: '1',
        });
        middleware.beforeRequest!(senderParams, next);
        // eslint-disable-next-line prefer-const
        let [target, events, callback] = onSpy.getCall(0).args;
        chai.expect(target).to.eq(ctx.document);
        chai.expect(events).to.be.deep.equal([
            'webkitvisibilitychange',
            'visibilitychange',
        ]);
        chai.expect(next.called).to.be.not.ok;
        ctx.document.visibilityState = 'rendered';

        callback({});
        chai.expect(next.called).to.be.ok;
        [target, events] = unSpy.getCall(0).args;
        chai.expect(target).to.eq(ctx.document);
        chai.expect(events).to.be.deep.equal([
            'webkitvisibilitychange',
            'visibilitychange',
        ]);
        chai.expect(next.called).to.be.ok;
        chai.expect(senderParams.brInfo.getVal('pr')).to.be.equal('1');
    });
});
