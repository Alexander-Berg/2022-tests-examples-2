import sinon from 'sinon';
import {
    GOAL_PREFIX,
    handleClick,
    useClickTracking,
} from '@src/providers/clickTracking';
import { CounterOptions } from '@src/utils/counterOptions';
import * as eventUtils from '@src/utils/events';
import * as buttonUtils from '@src/utils/dom/button';
import * as counterSettingUtils from '@src/utils/counterSettings';
import * as goalUtils from '@src/providers/goal';
import { ID } from '@src/utils/dom';
import { stringify } from '@src/utils/querystring';
import * as debugConsole from '@src/providers/debugConsole';
import { CounterSettings } from '@src/utils/counterSettings';
import chai from 'chai';
import { JSDOMWrapper } from '@src/__tests__/utils/jsdom';

describe('clickTracking', () => {
    const { window } = new JSDOMWrapper();
    const { document } = window;
    const counterOptions = {} as CounterOptions;
    const sandbox = sinon.createSandbox();

    let cEventSpy: sinon.SinonSpy;

    let sendGoalSpy: sinon.SinonSpy;
    let useGoalStub: sinon.SinonStub;

    beforeEach(() => {
        cEventSpy = sandbox.spy();
        sandbox.stub(eventUtils, 'cEvent').returns({
            on: cEventSpy,
        } as any);
        sendGoalSpy = sandbox.spy();
        useGoalStub = sandbox.stub(goalUtils, 'useGoal').returns(sendGoalSpy);

        sandbox.stub(debugConsole, 'getLoggerFn').returns(() => {});
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('subscribe event', () => {
        const counterSettings = {
            userData: {},
            settings: {
                pcs: '',
                ['button_goals']: 1,
                eu: false,
            },
        } as CounterSettings;

        sandbox
            .stub(counterSettingUtils, 'getCounterSettings')
            .callsFake((_, _1, fn) => {
                fn(counterSettings);
                const [ctx, events] = cEventSpy.getCall(0).args;
                chai.expect(ctx).to.eq(window);
                chai.expect(events).to.deep.equal(['click']);

                return Promise.resolve();
            });

        useClickTracking(window, counterOptions);
    });

    it('click button', () => {
        const target = document.createElement('BUTTON');
        const data = { [ID]: 'id' };

        sandbox.stub(buttonUtils, 'closestButton').returns(target);
        sandbox.stub(buttonUtils, 'getButtonData').returns(data as any);

        handleClick(window, counterOptions, target);

        sinon.assert.calledWith(
            useGoalStub,
            window,
            counterOptions,
            GOAL_PREFIX,
        );
        sinon.assert.calledWith(sendGoalSpy, `?${stringify(data)}`);
    });

    it('click invalid button', () => {
        const target = document.createElement('BUTTON');

        sandbox.stub(buttonUtils, 'closestButton').returns(null);

        handleClick(window, counterOptions, target);

        sinon.assert.notCalled(useGoalStub);
    });
});
