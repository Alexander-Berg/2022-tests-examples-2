import * as sinon from 'sinon';
import * as domUtils from '@src/utils/dom';
import {
    encodeByte,
    encodeChangeRegion,
    encodeCopy,
    encodeElement,
    encodeEvent,
    encodeFieldBlur,
    encodeFieldChange,
    encodeFieldFocus,
    encodeInputNode,
    encodeKeyDown,
    encodeMouseEvent,
    encodeScaled,
    encodeScaledString,
    encodeSelectText,
    encodeString,
    encodeSubmit,
    encodeWindowBlur,
    encodeWindowFocus,
    encodeWord,
} from '../encoders';
import { setElementId, ELEMENT_ID_PROPERTY } from '../global';
import { K_SHIFT, P_CLICK } from '../config';
import {
    assertByteCode,
    createNode,
    createInputInForm,
    createSimpleDiv,
} from './common';

describe('formvisor encoders: ', () => {
    const win = {
        document: {},
    } as unknown as Window;
    const sandbox = sinon.createSandbox();

    beforeEach(() => {
        sandbox.stub(domUtils, 'getFormNumber').returns(0);
    });
    afterEach(() => {
        sandbox.restore();
    });

    it('encodeWord', () => {
        const encodeWordBuffer: any[] = [];
        encodeWord(encodeWordBuffer, 123);
        assertByteCode(encodeWordBuffer, [0, 123]);
    });

    it('encodeString', () => {
        const encodeStringBuffer: any[] = [];
        encodeString(encodeStringBuffer, 'Hello World');
        // prettier-ignore
        assertByteCode(encodeStringBuffer, [11, 0, 72, 0, 101, 0, 108, 0, 108, 0, 111, 0, 32, 0, 87, 0, 111, 0, 114, 0, 108, 0, 100]);
    });

    it('encodeScaled', () => {
        const encodeScaledBuffer: any[] = [];
        encodeScaled(encodeScaledBuffer, 100500);
        assertByteCode(encodeScaledBuffer, [148, 145, 6]);
    });

    it('encodeScaledString', () => {
        const encodeScaledStringBuffer: any[] = [];
        encodeScaledString(encodeScaledStringBuffer, 'Hello World');
        // prettier-ignore
        assertByteCode(encodeScaledStringBuffer, [11, 72, 101, 108, 108, 111, 32, 87, 111, 114, 108, 100]);
    });

    it('encodeByte', () => {
        const encodeByteBuffer: any[] = [];
        encodeByte(encodeByteBuffer, 100);
        assertByteCode(encodeByteBuffer, [100]);
    });

    it('encodeEvent', () => {
        const encodeEventBuffer: any[] = [];
        encodeEvent(win, encodeEventBuffer, P_CLICK);
        assertByteCode(encodeEventBuffer, [32]);
    });

    it('encodeCopy', () => {
        assertByteCode(encodeCopy(win, 1000), [27, 232, 7]);
    });

    it('encodeWindowFocus', () => {
        assertByteCode(encodeWindowFocus(1000), [14, 232, 7]);
    });

    it('encodeWindowBlur', () => {
        assertByteCode(encodeWindowBlur(win, 1000), [15, 232, 7]);
    });

    it('encodeWindowBlur', () => {
        assertByteCode(
            encodeSelectText(win, 1000, 'Selected text'),
            // prettier-ignore
            [29, 232, 7, 13, 83, 101, 108, 101, 99, 116, 101, 100, 32, 116, 101, 120, 116, 0],
        );
    });

    it('encodeChangeRegion', () => {
        const simpleDiv = createSimpleDiv(100500);

        assertByteCode(
            encodeChangeRegion(win, 1000, simpleDiv),
            // prettier-ignore
            [9, 232, 7, 148, 145, 6, 0, 0, 10, 232, 7, 148, 145, 6, 0, 0],
        );
    });

    it('encodeFieldFocus, encodeFieldBlur, encodeFieldChange', () => {
        const fieldMock = {
            [ELEMENT_ID_PROPERTY]: 123,
        } as any as HTMLElement;

        assertByteCode(
            encodeFieldFocus(win, 1000, fieldMock),
            // prettier-ignore
            [17, 232, 7, 123],
        );
        assertByteCode(
            encodeFieldBlur(win, 1000, fieldMock),
            // prettier-ignore
            [18, 232, 7, 123],
        );
        assertByteCode(
            encodeFieldChange(win, 1000, fieldMock, 'Text', false),
            // prettier-ignore
            [39, 232, 7, 123, 4, 0, 84, 0, 101, 0, 120, 0, 116, 0],
        );
    });

    it('encodeElement', () => {
        const simpleDiv = createSimpleDiv(123);

        assertByteCode(
            encodeElement(win, simpleDiv),
            // prettier-ignore
            [1, 123, 68, 0, 26, 0, 0, 0, 0, 0],
        );
    });

    it('encodeInputNode', () => {
        const inputMock = createInputInForm(1009);
        setElementId(inputMock, 1010);
        assertByteCode(
            encodeInputNode(win, inputMock as HTMLInputElement),
            // prettier-ignore
            [7, 242, 7, 0, 0, 0, 0],
        );
    });

    it('encodeMouseEvent', () => {
        const simpleDiv = createSimpleDiv(2020);
        sandbox.stub(simpleDiv, 'getBoundingClientRect').returns({
            width: 50,
            height: 50,
            left: 0,
            top: 0,
        } as any);

        assertByteCode(
            encodeMouseEvent(win, 1000, 'click', simpleDiv, [100, 200], 0, 0),
            // prettier-ignore
            [32, 232, 7, 228, 15, 100, 200, 1, 1],
        );
    });

    it('encodeKeyDown', () => {
        const simpleDiv = createSimpleDiv(2021);

        assertByteCode(
            encodeKeyDown(win, 1000, 100, K_SHIFT, simpleDiv, false),
            // prettier-ignore
            [38, 232, 7, 0, 100, 2, 229, 15, 0],
        );
    });

    it('encodeSubmit', () => {
        const formInnerHtml = '<input value="Hello World" />';
        const formMock = createNode('form', formInnerHtml, 2022);
        setElementId(formMock.firstChild!, 2023);

        assertByteCode(
            encodeSubmit(win, 1000, formMock as HTMLFormElement),
            // prettier-ignore
            [11, 232, 7, 0, 1, 231, 15],
        );
    });
});
