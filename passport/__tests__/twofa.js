import {showRegPopup, setEditMode} from '../../../../common/actions';

import * as extracted from '../twofa.js';

jest.mock('../../../../common/actions', () => ({
    setEditMode: jest.fn(),
    showRegPopup: jest.fn()
}));

describe('Morda.TwoFA', () => {
    afterEach(() => {
        setEditMode.mockClear();
    });

    it('should dispatch setEditMode', () => {
        const obj = {
            props: {
                dispatch: jest.fn()
            }
        };

        extracted.closeErrorModal.call(obj);
        expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
        expect(setEditMode).toHaveBeenCalledTimes(1);
        expect(setEditMode).toHaveBeenCalledWith(null);
    });
    describe('onLinkClick', () => {
        const event = {
            preventDefault: jest.fn()
        };

        let obj = null;

        beforeEach(() => {
            obj = {
                props: {
                    passwordStrength: -1,
                    dispatch: jest.fn(),
                    is2faEnabled: false
                }
            };
        });
        afterEach(() => {
            event.preventDefault.mockClear();
        });
        it('should dispatch showRegPopup and preventDefault', () => {
            extracted.onLinkClick.call(obj, event);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(event.preventDefault).toHaveBeenCalledTimes(1);
            expect(showRegPopup).toHaveBeenCalledTimes(1);
            expect(showRegPopup).toHaveBeenCalledWith(true);
        });
        it('should dispatch setEditMode and preventDefault', () => {
            obj.props.canChangePassword = false;

            extracted.onLinkClick.call(obj, event);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(event.preventDefault).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledWith(extracted.TWOFA_ERROR_MODAL);
        });
        it('shouldnt call dispatch or preventDefault', () => {
            obj.props.passwordStrength = 0;

            extracted.onLinkClick.call(obj, event);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(0);
            expect(event.preventDefault).toHaveBeenCalledTimes(0);
        });
    });
});
