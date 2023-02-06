import validateConnectDomain from '@blocks/registration/methods/validateDomain';
import checkIfInvalid from '@blocks/registration/methods/checkIfInvalid';
import {updateValues, updateHintStatus} from '@blocks/actions/form';

import * as extracted from '../domain_input.js';

jest.mock('@blocks/actions/form', () => ({
    updateValues: jest.fn(),
    updateHintStatus: jest.fn()
}));

jest.mock('@blocks/registration/methods/validateDomain');
jest.mock('@blocks/registration/methods/checkIfInvalid');

jest.mock('lodash/debounce', () => (method) => method);

global.clearTimeout = jest.fn();

describe('Connect.DomainInput', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            setState: jest.fn(),
            stopNumbers: {
                main: 0
            },
            state: {
                placeholderHidden: false
            },
            props: {
                dispatch: jest.fn(),
                isMobile: false
            }
        };
    });
    validateConnectDomain.mockImplementation(() => () => ({status: 'ok'}));
    checkIfInvalid.mockImplementation(() => () => ({status: 'ok'}));

    afterEach(() => {
        updateValues.mockClear();
        updateHintStatus.mockClear();
        validateConnectDomain.mockClear();
        checkIfInvalid.mockClear();
    });
    describe('handleBlur', () => {
        it('should dispatch updateHintStatus and call setState', () => {
            extracted.handleBlur.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(updateHintStatus).toHaveBeenCalledTimes(1);
            expect(updateHintStatus).toHaveBeenCalledWith(false);
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({focused: false});
        });
    });
    describe('handleFocus', () => {
        it('should dispatch updateHintStatus and checkIfInvalid, and call setState', () => {
            extracted.handleFocus.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(updateHintStatus).toHaveBeenCalledTimes(1);
            expect(updateHintStatus).toHaveBeenCalledWith(true);
            expect(checkIfInvalid).toHaveBeenCalledTimes(1);
            expect(checkIfInvalid).toHaveBeenCalledWith('domain');
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({focused: true});
        });
    });
    describe('stateHandler', () => {
        it('should dispatch updateHintStatus and call setState', () => {
            extracted.stateHandler.call(obj, false);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(updateHintStatus).toHaveBeenCalledTimes(1);
            expect(updateHintStatus).toHaveBeenCalledWith(false);
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({focused: false});
        });
    });
    describe('handleValidation', () => {
        it('should dispatch validateConnectDomain', () => {
            const value = 'value';

            extracted.handleValidation.call(obj, value);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(validateConnectDomain).toHaveBeenCalledTimes(1);
            expect(validateConnectDomain).toHaveBeenCalledWith(value);
        });
    });
    describe('construct', () => {
        test('if desktop', () => {
            extracted.construct.call(obj, obj.props);
            expect(obj.stopNumbers).toEqual({
                main: 17,
                sub: 19
            });
        });
        test('if mobile', () => {
            obj.props.isMobile = true;

            extracted.construct.call(obj, obj.props);
            expect(obj.stopNumbers).toEqual({
                main: 11,
                sub: 20
            });
        });
    });
    describe('handleInput', () => {
        it('should dispatch updateValues and validateConnectDomain', () => {
            extracted.handleInput.call(obj, {target: {value: ''}});
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(updateValues).toHaveBeenCalledTimes(1);
            expect(updateValues).toHaveBeenCalledWith({field: 'domain', value: ''});
            expect(validateConnectDomain).toHaveBeenCalledTimes(1);
            expect(validateConnectDomain).toHaveBeenCalledWith('');
        });
        it('sohuld call setState', () => {
            jest.useFakeTimers();
            extracted.handleInput.call(obj, {target: {value: 'asd'}});
            jest.runAllTimers();
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({placeholderHidden: true});
        });
        it('should call clearTimeout', () => {
            obj.timer = true;

            extracted.handleInput.call(obj, {target: {value: ''}});
            expect(clearTimeout).toHaveBeenCalledTimes(1);
            expect(clearTimeout).toHaveBeenCalledWith(true);
        });
        it('should call setState', () => {
            obj.state.placeholderHidden = true;

            extracted.handleInput.call(obj, {target: {value: ''}});
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({placeholderHidden: false});
        });
    });
});
