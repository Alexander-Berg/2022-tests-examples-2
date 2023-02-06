import * as sinon from 'sinon';
import * as time from '@src/utils/time';
import * as domUtils from '@src/utils/dom';
import * as mouseUtils from '@src/utils/mouseEvents';
import { JSDOMWrapper } from '@src/__tests__/utils/jsdom';
import * as formvisorGlobal from '@private/src/providers/formvisor/global';
import {
    assertByteCode,
    createNode,
} from '@private/src/providers/formvisor/__tests__/common';
import {
    onMouseMove,
    onMouseWheel,
    onResize,
    onScroll,
    onScrollLocal,
    onTouchMove,
    onUnload,
} from '../transformers';

describe('webvisor transformers: ', () => {
    const { window } = new JSDOMWrapper();
    // @ts-ignore -- The tested functions call global "document:, which is not available in node.
    global.document = window.document;
    let win: Window;
    const sandbox = sinon.createSandbox();

    beforeEach(() => {
        win = {
            document: {},
        } as any as Window;

        // Важно сбрасывать elementId и cache для каждого теста
        const elementsCache = {
            counter: 0,
        };
        sandbox
            .stub(formvisorGlobal, 'getElementsCache')
            .returns(elementsCache);
        sandbox.stub(formvisorGlobal, 'incrementElementId').callsFake(() => {
            elementsCache.counter += 1;
            return elementsCache.counter;
        });

        // Время
        sandbox.stub(time, 'getVisorNowEventTime').returns(1000);
        sandbox.stub(time, 'TimeOne').returns(() => 1000 as any);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('onMouseMove', () => {
        sandbox.stub(mouseUtils, 'getPosition').returns({ x: 100, y: 100 });

        const div = createNode('div', 'Hello World');
        const evt = {
            target: div,
        };
        const params = { ctx: win, evt: evt as any as Event };

        assertByteCode(
            onMouseMove(params),
            // prettier-ignore
            [1, 1, 68, 0, 26, 0, 0, 0, 0, 0],
        );
    });

    it('onScroll onScrollLocal', () => {
        sandbox.stub(domUtils, 'getDocumentScroll').returns({
            x: 100,
            y: 100,
        });

        const div = createNode('div', 'Hello World');
        const evt = {
            target: div,
        } as any as Event;
        const params = { ctx: win, evt };

        assertByteCode(onScroll(params), [3, 232, 7, 100, 100]);
        assertByteCode(
            onScrollLocal(params),
            // prettier-ignore
            [1, 1, 68, 0, 26, 0, 0, 0, 0, 0, 16, 232, 7, 0, 0, 1],
        );
    });

    it('onMouseWheel', () => {
        sandbox.stub(mouseUtils, 'getPosition').returns({ x: 100, y: 100 });

        const div = createNode('div', 'Hello World');
        const evt = {
            target: div,
            type: 'wheel',
            deltaY: 100,
        } as any as Event;
        const params = { ctx: win, evt };

        assertByteCode(
            onMouseWheel(params),
            // prettier-ignore
            [1, 1, 68, 0, 26, 0, 0, 0, 0, 0, 31, 232, 7, 1, 100, 100, 0, 0, 1],
        );
    });

    it('onUnload', () => {
        const params = { ctx: win, evt: {} as any as Event };
        assertByteCode(onUnload(params), [13]);
    });

    it('onResize', () => {
        const params = { ctx: win, evt: {} as any as Event };
        sandbox.stub(domUtils, 'getViewportSize').returns([100, 100]);
        sandbox.stub(domUtils, 'getDocumentSize').returns([200, 200]);
        assertByteCode(
            onResize(params),
            // prettier-ignore
            [28, 232, 7, 100, 100, 200, 1, 200, 1],
        );
    });

    it('onTouchMove', () => {
        const div = createNode('div', 'Hello World');
        const evt = {
            target: div,
            touches: [
                {
                    pageX: 10,
                    pageY: 10,
                },
                {
                    pageX: 20,
                    pageY: 20,
                },
            ],
        } as any as Event;
        const params = { ctx: win, evt };

        sandbox.stub(div, 'getBoundingClientRect').returns({
            width: 50,
            height: 50,
            left: 0,
            top: 0,
        } as any);

        assertByteCode(
            onTouchMove(params),
            // prettier-ignore
            [1, 1, 68, 0, 26, 0, 0, 50, 50, 0, 12, 232, 7, 1, 10, 10, 12, 232, 7, 1, 20, 20],
        );
    });
});
