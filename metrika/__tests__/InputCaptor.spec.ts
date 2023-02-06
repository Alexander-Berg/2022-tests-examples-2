import * as sinon from 'sinon';
import * as domUtils from '@src/utils/dom';
import * as async from '@src/utils/async';
import * as inputUtils from '@src/utils/webvisor/inputUtils';
import { JSDOMWrapper } from '@src/__tests__/utils/jsdom';
import {
    NODE_ADD_EVENT_KEY_PREFIX,
    NODE_REMOVAL_EVENT_KEY_PREFIX,
} from '../../../indexer/Indexer';
import * as collectUtils from '../../../utils/collectNodeInfo';
import { INPUT_EVENT_NAME, InputCaptor } from '../InputCaptor';
import { EVENT_EVENT_TYPE } from '../../AbstractCaptor/AbstractCaptor';
import { createRecorderMock } from '../../AbstractCaptor/__tests__/createMockRecorder';

describe('InputCaptor', () => {
    const { window } = new JSDOMWrapper();
    const { document } = window;
    const INITIAL_VALUE = '';
    const NEW_VALUE = 'new_value';
    const INVALID_VALUE = 'invalid_value';

    const body = {
        appendChild: () => {},
        removeChild: () => {},
    };
    const win = {
        document: {
            body,
            documentElement: body,
            compatMode: 'CSS1Compat',
        },
        Object: {
            getOwnPropertyDescriptor: Object.getOwnPropertyDescriptor,
            defineProperty: Object.defineProperty,
        },
    } as any;
    let recorder: any;
    let inputCaptor: any;
    let isValidInput = true;
    let isPrivate = false;
    let isForce = false;

    let getElemCreateFunctionStub: sinon.SinonStub;

    beforeEach(() => {
        isValidInput = true;
        isPrivate = false;
        isForce = false;
        recorder = createRecorderMock();
        recorder.getIndexer().indexNode = (node: any) => {
            return node.indexerId;
        };

        getElemCreateFunctionStub = recorder.test.sandbox
            .stub(domUtils, 'getElemCreateFunction')
            .returns(document.createElement.bind(document));
        recorder.test.sandbox
            .stub(collectUtils, 'normalizeAttibute')
            .callsFake(
                (
                    ctx: Window,
                    input: HTMLInputElement,
                    attr: string,
                    value: any,
                ) => ({ value }),
            );
        recorder.test.sandbox
            .stub(inputUtils, 'isValidInput')
            .callsFake(() => isValidInput);
        recorder.test.sandbox
            .stub(inputUtils, 'isPrivateInformationField')
            .callsFake(() => isPrivate);
        recorder.test.sandbox
            .stub(inputUtils, 'isForceRecordingEnabled')
            .callsFake(() => isForce);

        recorder.test.sandbox
            .stub(async, 'runAsync')
            .callsFake((aCtx: any, cb: Function) => cb());
        inputCaptor = new InputCaptor(win, recorder, 'a');
    });

    afterEach(() => {
        inputCaptor.stop();
        recorder.test.restore();
    });

    let id = 0;
    const addInput = (
        element?: HTMLInputElement,
    ): HTMLInputElement & { indexerId: number } => {
        const input: any = element || document.createElement('input');

        if (!input.indexerId) {
            id += 1;
            input.indexerId = id;
        }
        recorder.test.createEvent(
            `${NODE_ADD_EVENT_KEY_PREFIX}${domUtils.INPUT_NODES[0].toLowerCase()}`,
            { data: { node: input, id } },
        );

        return input;
    };

    // FIXME: Failing test after switching to node env.
    it.skip('send data on change value', () => {
        inputCaptor.start();
        const input = addInput();
        input.value = NEW_VALUE;

        recorder.test.checkSendEvent(
            EVENT_EVENT_TYPE,
            {
                value: NEW_VALUE,
                hidden: false,
                target: input.indexerId,
            },
            INPUT_EVENT_NAME,
        );
    });

    it('send data on dispatch event', () => {
        inputCaptor.start();
        const input = addInput();
        input.value = NEW_VALUE;

        recorder.test.createEvent('input', { target: input });

        recorder.test.checkSendEvent(
            EVENT_EVENT_TYPE,
            {
                value: NEW_VALUE,
                hidden: false,
                target: input.indexerId,
            },
            INPUT_EVENT_NAME,
        );
    });

    it('remove input', () => {
        inputCaptor.start();
        const input = addInput();

        recorder.test.createEvent(
            `${NODE_REMOVAL_EVENT_KEY_PREFIX}${domUtils.INPUT_NODES[0].toLowerCase()}`,
            { data: { node: input, id: input.indexerId } },
        );

        input.value = NEW_VALUE;

        recorder.test.checkNoEvent();
    });

    // FIXME: Failing test after switching to node env.
    it.skip('checkbox', () => {
        inputCaptor.start();
        const input = document.createElement('input');
        input.setAttribute('type', 'checkbox');
        input.checked = false;
        addInput(input);

        input.checked = true;
        recorder.test.checkSendEvent(
            EVENT_EVENT_TYPE,
            {
                checked: true,
                target: (input as any).indexerId,
            },
            INPUT_EVENT_NAME,
        );
    });

    it('empty target', () => {
        inputCaptor.start();
        recorder.test.createEvent('input', {});

        recorder.test.checkNoEvent();
    });

    it('dispatch event on invalid input', () => {
        inputCaptor.start();
        isValidInput = false;
        const input = addInput();

        recorder.test.createEvent('input', { target: input });

        recorder.test.checkNoEvent();
    });

    // FIXME: Failing test after switching to node env.
    it.skip('hidden', () => {
        inputCaptor.start();
        isPrivate = true;
        const input = addInput();

        input.value = NEW_VALUE;

        recorder.test.checkSendEvent(
            EVENT_EVENT_TYPE,
            {
                value: NEW_VALUE,
                hidden: true,
                target: input.indexerId,
            },
            INPUT_EVENT_NAME,
        );

        isForce = true;

        input.value = INITIAL_VALUE;

        recorder.test.checkSendEvent(
            EVENT_EVENT_TYPE,
            {
                value: INITIAL_VALUE,
                hidden: false,
                target: input.indexerId,
            },
            INPUT_EVENT_NAME,
            1,
        );
    });

    it('not overridable descriptor', () => {
        win.Object.defineProperty = undefined;
        inputCaptor.start();

        const input = addInput();
        input.value = NEW_VALUE;

        recorder.test.createEvent('input', { target: input });

        recorder.test.checkSendEvent(
            EVENT_EVENT_TYPE,
            {
                value: NEW_VALUE,
                hidden: false,
                target: input.indexerId,
            },
            INPUT_EVENT_NAME,
        );
        win.Object.defineProperty = Object.defineProperty;
    });

    it('broken descriptor', () => {
        const brokenInput = document.createElement('input');
        Object.defineProperty(brokenInput, 'value', {
            configurable: true,
            get(this: HTMLInputElement) {
                return INVALID_VALUE;
            },
            set(this: HTMLInputElement) {
                return INVALID_VALUE;
            },
        });
        getElemCreateFunctionStub.returns(() => brokenInput);

        inputCaptor.start();
        const input = addInput();
        input.value = NEW_VALUE;

        recorder.test.createEvent('input', { target: input });

        recorder.test.checkSendEvent(
            EVENT_EVENT_TYPE,
            {
                value: NEW_VALUE,
                hidden: false,
                target: input.indexerId,
            },
            INPUT_EVENT_NAME,
        );
        win.Object.defineProperty = Object.defineProperty;
    });
});
