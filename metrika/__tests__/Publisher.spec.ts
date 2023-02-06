import * as chai from 'chai';
import * as sinon from 'sinon';
import * as DOM from '@src/utils/dom';
import * as eventUtils from '@src/utils/events';
import * as timeUtils from '@src/utils/time';
import * as globalStorage from '@src/storage/global';
import * as defer from '@src/utils/defer';
import * as errorLogger from '@src/utils/errorLogger';
import * as flags from '@src/inject';
import {
    Visor2Buffer,
    AGGREGATE_EVENT_KEY,
} from '@private/src/buffer/Visor2Buffer';
import { BufferData } from '@private/src/buffer/types';
import { PREPROD_FEATURE, SUPER_DEBUG_FEATURE } from '@generated/features';
import * as dConsole from '@src/providers/debugConsole';
import { JSDOMWrapper } from '@src/__tests__/utils/jsdom';
import * as locationUtils from '@src/utils/location';
import * as lsUtils from '@src/storage/localStorage';
import * as hidUtils from '@src/middleware/watchSyncFlags/brinfoFlags/hid';
import {
    ACTIVE_EVENTS,
    PUBLISHER_FUNCTION_KEY_PREFIX,
    ITERATOR_INTERVAL,
    PUBLISHER_ACTIVE_ARTICLE_LS_KEY,
} from '../consts';
import { PublisherProvider } from '../Publisher';
import { AbstractPublisherSchema } from '../schemas/AbstractPublisherSchema';

export class MockSchema extends AbstractPublisherSchema {
    fields = {};

    id = 'mock';

    contentItemsToReturn = 2;

    findContentDescriptionNodes() {
        return [];
    }

    findContent() {
        const result: any[] = [];
        for (let i = 0; i < this.contentItemsToReturn; i += 1) {
            result.push({
                id: i + 1,
                contentElement: {
                    getBoundingClientRect: () => ({
                        x: 100 * i,
                        y: 100 * i,
                        top: 100 * i,
                        bottom: 100 * (i + 1),
                        left: 100 * i,
                        right: 100 * (i + 1),
                        width: 100,
                        height: 100,
                    }),
                },
                element: i,
                stamp: 100,
                involvedTime: 0,
            });
        }
        return result;
    }
}

export class MockBuffer extends Visor2Buffer {
    aggregationCallbacks: Function[] = [];

    setFlushTimout() {
        // NOTHING
    }

    push(data: BufferData) {
        this.buffer.push(data);
    }

    getBuffer() {
        return this.buffer;
    }

    on(event: string, callback: Function) {
        if (event === AGGREGATE_EVENT_KEY) {
            this.aggregationCallbacks.push(callback);
        }
    }

    getCallbacks() {
        return this.aggregationCallbacks;
    }

    clearBuffer() {
        this.buffer = [];
    }
}

describe('PublisherProvider', () => {
    const { window } = new JSDOMWrapper();
    const { document } = window;
    const win = window;
    const sandbox = sinon.createSandbox();
    const eventsSpy: any = {
        on: sinon.spy(),
        un: sinon.spy(),
    };
    // Он подобран таким образом чтобы одна статья в него попала,
    // но вторая - нет
    const viewport = [100, 100, 1];
    const targetLink: any = {
        hostname: 'example.com',
    };
    const location: any = {
        hostname: 'example.com',
    };
    const hid = 123;
    let globalStore: Record<string, any> = {};
    let closestStub: sinon.SinonStub<any, any>;
    let eventMock: sinon.SinonStub<any, any>;
    let timeMock: sinon.SinonStub<any, any>;
    let deferMock: sinon.SinonStub<any, any>;
    let globalStorageMock: sinon.SinonStub<any, any>;
    let errorLoggerMock: any;
    let clock: ReturnType<typeof sinon.useFakeTimers>;
    const localStorage: any = {
        setVal: sandbox.stub(),
    };

    beforeEach(() => {
        clock = sinon.useFakeTimers();
        const startingTime = 100000000000000;
        let timeCalled = 0;
        sandbox.stub(dConsole, 'consoleLog');

        errorLoggerMock = sandbox.stub(errorLogger, 'errorLogger');
        errorLoggerMock.callsFake(
            ((ctx: any, namespace: string, fn: (...args: any[]) => any) =>
                fn) as any,
        );
        deferMock = sandbox.stub(defer, 'setDefer');
        timeMock = sandbox.stub(timeUtils, 'TimeOne');
        timeMock.returns(() => {
            timeCalled += 1;
            return startingTime + timeCalled * 100;
        });
        eventMock = sandbox.stub(eventUtils, 'cEvent');
        eventMock.returns(eventsSpy);
        closestStub = sandbox.stub(DOM, 'closest');
        globalStorageMock = sandbox.stub(globalStorage, 'getGlobalStorage');
        globalStorageMock.returns({
            getVal(key: string, defaultValue: any) {
                return globalStore[key] || defaultValue;
            },
            setSafe(key: string, val: any) {
                globalStore[key] = val;
            },
        } as any);
        sandbox.stub(DOM, 'getVisualViewportSize').returns(viewport as any);
        sandbox.stub(flags, 'flags').value({
            [SUPER_DEBUG_FEATURE]: false,
        });
        sandbox.stub(hidUtils, 'getHid').returns(hid);
        sandbox.stub(locationUtils, 'getLocation').returns(location);
        sandbox.stub(lsUtils, 'counterLocalStorage').returns(localStorage);
        sandbox.stub(DOM, 'getTargetLink').returns(targetLink);
    });

    afterEach(() => {
        eventsSpy.on.resetHistory();
        eventsSpy.un.resetHistory();
        clock.restore();
        sandbox.restore();
        globalStore = {};
    });

    it('sets current articleid in ls on internal link click', () => {
        const schema = new MockSchema(win, '');
        const buffer = new MockBuffer(win, {} as any, () => Promise.resolve());
        const provider = new PublisherProvider(win, schema, buffer, '123');
        closestStub.returns(document.documentElement);
        provider.start();
        const [eventCtx, [eventName], callback] = eventsSpy.on.getCall(1).args;
        chai.expect(eventCtx).to.equal(win);
        chai.expect(eventName).to.equal('click');

        callback({});
        const [lsKey, value] = localStorage.setVal.getCall(0).args;
        chai.expect(lsKey).to.equal(PUBLISHER_ACTIVE_ARTICLE_LS_KEY);
        chai.expect(value).to.equal(`${1}-${hid}`);
    });

    it('parse articles again after remove from DOM', () => {
        const schema = new MockSchema(win, '');
        const buffer = new MockBuffer(win, {} as any, () => Promise.resolve());
        const provider = new PublisherProvider(win, schema, buffer, '123');
        deferMock.restore();
        closestStub.returns(document.documentElement);

        provider.start();

        closestStub.withArgs('html', win, 0).returns(false);

        clock.tick(ITERATOR_INTERVAL);

        closestStub.withArgs('html', win, 0).returns(document.documentElement);

        clock.tick(ITERATOR_INTERVAL);

        chai.expect(buffer.getCallbacks().length).to.equal(1);
        const bufferData = [
            {
                type: 'articleInfo',
                stamp: 100,
                data: {
                    id: 1,
                    stamp: 100,
                },
            },
            {
                type: 'articleInfo',
                stamp: 100,
                data: {
                    id: 2,
                    stamp: 100,
                },
            },
            {
                type: 'articleInfo',
                stamp: 100,
                data: {
                    id: 1,
                    stamp: 100,
                },
            },
        ];
        chai.expect(buffer.getBuffer()).to.be.deep.eq(bufferData);
    });

    const checkInitAndBaseLogic = () => {
        const schema = new MockSchema(win, '');
        const buffer = new MockBuffer(win, {} as any, () => Promise.resolve());
        const provider = new PublisherProvider(win, schema, buffer, '123');
        deferMock.callsFake(() => 123);
        closestStub.returns(document.documentElement);
        provider.start();
        const [eventCtx, allEvents, eventsCallback] =
            eventsSpy.on.getCall(0).args;
        chai.expect(eventCtx).to.eq(win);
        chai.expect(allEvents).to.deep.equal(ACTIVE_EVENTS);
        chai.expect(buffer.getCallbacks().length).to.equal(1);

        const bufferData = [
            {
                type: 'articleInfo',
                stamp: 100,
                data: {
                    id: 1,
                    stamp: 100,
                },
            },
            {
                type: 'articleInfo',
                stamp: 100,
                data: {
                    id: 2,
                    stamp: 100,
                },
            },
        ];
        chai.expect(buffer.getBuffer()).to.deep.equal(bufferData);

        eventsCallback({ type: 'scroll' });
        const iterationCallback =
            globalStore[`${PUBLISHER_FUNCTION_KEY_PREFIX}${schema.id}`][0];
        iterationCallback([
            {
                id: 1,
                stamp: 100,
            },
            {
                id: 2,
                stamp: 100,
            },
        ]);
        const meta = buffer.getCallbacks()[0](bufferData);
        const expectMeta = {
            type: 'publishersHeader',
            data: {
                articleMeta: [
                    {
                        id: 1,
                        involvedTime: 5100,
                        maxScrolled: 1,
                        chars: 0,
                        x: 0,
                        y: 0,
                        height: 100,
                        width: 100,
                    },
                    {
                        id: 2,
                        involvedTime: 0,
                        maxScrolled: 0,
                        chars: 0,
                        x: 100,
                        y: 100,
                        height: 100,
                        width: 100,
                    },
                ],
                involvedTime: 5100,
            },
        };
        chai.expect(meta).to.deep.equal(expectMeta);

        provider.stop();

        const [target, events, cb] = eventsSpy.un.getCall(0).args;
        chai.expect(target).to.equal(win);
        chai.expect(events).to.equal(ACTIVE_EVENTS);
        chai.expect(cb).to.equal(eventsCallback);
    };

    it('Initiates itself and works correctly (old logic)', () => {
        sandbox.stub(flags, 'flags').value({
            [PREPROD_FEATURE]: false,
            [SUPER_DEBUG_FEATURE]: false,
        });
        checkInitAndBaseLogic();
    });

    it('Initiates itself and works correctly (new logic)', () => {
        sandbox.stub(flags, 'flags').value({
            [PREPROD_FEATURE]: true,
            [SUPER_DEBUG_FEATURE]: false,
        });
        checkInitAndBaseLogic();
    });
});
