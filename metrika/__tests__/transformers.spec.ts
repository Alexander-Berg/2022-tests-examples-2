import * as sinon from 'sinon';
import * as time from '@src/utils/time';
import * as domUtils from '@src/utils/dom';
import * as defer from '@src/utils/defer';
import * as mouseUtils from '@src/utils/mouseEvents';
import * as formvisorGlobal from '../global';
import {
    appendElementsToQueue,
    handleInputTarget,
    onCopy,
    onFieldBlur,
    onFieldChange,
    onFieldFocus,
    onKeyDown,
    onKeyEvent,
    onKeyPress,
    onMouseLeaveFlush,
    onMouseUp,
    onSelectText,
    onSubmit,
    onWindowBlur,
    onWindowFocus,
    onWindowFocusIn,
    onWindowFocusOut,
} from '../transformers';
import { assertByteCode, createNode } from './common';

// На время эксперимента придётся заскипать потому что в виду специфики выполнения
// модлуей не получается без кривой инициализации замокать флаг
describe.skip('formvisor encoders: ', () => {
    let win: Window;
    const sandbox = sinon.createSandbox();

    const matchesFunction = function matches(this: any) {
        return false;
    };

    beforeEach(() => {
        win = {
            Element: { prototype: { oMatchesSelector: matchesFunction } },
            document: {},
            getSelection: () => ({
                toString: () => 'Hello World',
                anchorNode: createNode('div', 'Copy this text'),
            }),
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

        // время и setTimeOut
        sandbox.stub(defer, 'setDefer').callsFake((_, fn) => fn());
        sandbox.stub(time, 'getVisorNowEventTime').returns(1000);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('appendElementsToQueue', () => {
        const div = createNode('div', 'Hello World');
        assertByteCode(
            appendElementsToQueue(win, div),
            // prettier-ignore
            [1, 1, 84, 0, 26, 0, 0, 0, 0, 255, 97, 0],
        );
    });

    it('onWindowFocus onWindowBlur onWindowFocusIn onWindowFocusOut', () => {
        const params = { ctx: win, evt: {} as any as Event };
        // Важен порядок (по дефолту мы в фокусе). Сначала blur
        assertByteCode(onWindowBlur(params), [15, 232, 7]);
        assertByteCode(onWindowFocus(params), [14, 232, 7]);
        // Повторный фокус не сработает
        assertByteCode(onWindowFocus(params), []);
        assertByteCode(onWindowFocusOut(params), [15, 232, 7]);
        assertByteCode(onWindowFocusIn(params), [14, 232, 7]);
    });

    it('onSelectText', () => {
        const params = { ctx: win, evt: {} as any as Event };
        assertByteCode(
            onSelectText(params),
            // prettier-ignore
            [29, 232, 7, 11, 72, 101, 108, 108, 111, 32, 87, 111, 114, 108, 100, 0],
        );
        assertByteCode(onSelectText(params), []);
    });

    it('onCopy', () => {
        const params = { ctx: win, evt: {} as any as Event };
        // Обязательно после теста onSelectText
        assertByteCode(onCopy(params), [27, 232, 7]);
    });

    it('handleInputTarget', () => {
        const params = { ctx: win, evt: {} as any as Event };
        const input = document.createElement('input');

        assertByteCode(
            handleInputTarget(params, input),
            // prettier-ignore
            [1, 1, 68, 0, 47, 0, 0, 0, 0, 0],
        );
    });

    it('onFieldFocus onFieldBlur onFieldChange', () => {
        const input = document.createElement('input');
        input.value = 'Hello World';
        const evt = {
            target: input,
        };
        const params = { ctx: win, evt: evt as any as Event };

        assertByteCode(
            onFieldFocus(params),
            // prettier-ignore
            [1, 1, 68, 0, 47, 0, 0, 0, 0, 0, 17, 232, 7, 1],
        );

        assertByteCode(
            onFieldBlur(params),
            // prettier-ignore
            [18, 232, 7, 1],
        );

        assertByteCode(
            onFieldChange(params),
            // prettier-ignore
            [39, 232, 7, 1, 11, 0, 72, 0, 101, 0, 108, 0, 108, 0, 111, 0, 32, 0, 87, 0, 111, 0, 114, 0, 108, 0, 100, 0],
        );
    });

    it('onMouseUp onMouseEvent', () => {
        sandbox.stub(mouseUtils, 'getPosition').returns({ x: 0, y: 0 });

        const div = createNode('div', 'Hello World');
        const evt = {
            target: div,
        };
        const params = { ctx: win, evt: evt as any as Event };
        // Внутри onMouseUp находится onMouseEvent (проверяются сразу оба)
        // В данном тесте onSelectText вернет [] (он уже отработал в тестах выше)
        assertByteCode(
            onMouseUp(params),
            // prettier-ignore
            [1, 1, 84, 0, 26, 0, 0, 0, 0, 255, 97, 0],
        );
    });

    it('onKeyEvent onKeyDown onKeyPress', () => {
        const input = document.createElement('input');
        const evt = {
            target: input,
            keyCode: 100,
        } as any as Event;
        const params = { ctx: win, evt };

        assertByteCode(
            onKeyEvent(win, evt as KeyboardEvent, 100, 10),
            // prettier-ignore
            [1, 1, 68, 0, 47, 0, 0, 0, 0, 0, 38, 232, 7, 0, 100, 10, 1, 0],
        );

        // Порядок важен: сначала onKeyPress, затем onKeyDown
        assertByteCode(onKeyPress(params), [38, 232, 7, 0, 100, 0, 1, 0]);
        assertByteCode(onKeyDown(params), [38, 232, 7, 0, 100, 16, 1, 0]);
    });

    it('onSubmit', () => {
        sandbox.stub(domUtils, 'getFormNumber').returns(0);

        const formInnerHtml = '<input value="Hello World" />';
        const formMock = createNode('form', formInnerHtml);
        const evt = {
            target: formMock,
        } as any as Event;
        const params = { ctx: win, evt };

        assertByteCode(
            onSubmit(params),
            // prettier-ignore
            [1, 1, 68, 0, 32, 0, 0, 0, 0, 0, 1, 2, 77, 1, 47, 0, 0, 0, 7, 2, 0, 0, 0, 0, 11, 232, 7, 0, 1, 2],
        );
    });

    it('onMouseLeaveFlush', () => {
        const evt = {
            target: {
                tagName: 'BODY',
                ownerDocument: document,
            },
        } as any as Event;
        const callback = sandbox.stub();
        const params = { ctx: win, evt, flush: callback };

        onMouseLeaveFlush(params);
        sinon.assert.calledOnce(callback);
    });
});
