import {push} from 'react-router-redux';

import {setEditMode, showRegPopup} from '@blocks/common/actions';
import {showHint} from '@blocks/morda/access/actions';
import {getTokensList} from '@blocks/morda/app_passwords/index';

import * as extracted from '../passwords.js';

jest.mock('@blocks/common/actions', () => ({
    setEditMode: jest.fn(),
    showRegPopup: jest.fn()
}));
jest.mock('@blocks/morda/access/actions', () => ({
    showHint: jest.fn()
}));
jest.mock('@blocks/morda/app_passwords/index', () => ({
    getTokensList: jest.fn()
}));
jest.mock('react-router-redux', () => ({
    push: jest.fn()
}));

describe('Morda.AuthBlock.AppPasswords.Passwords', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            props: {
                settings: {
                    isTouch: false
                },
                dispatch: jest.fn(),
                appPasswords: {
                    tokens: {}
                },
                retpath: 'retpath',
                is2faEnabled: false,
                passwordStrength: 0
            }
        };
    });
    afterEach(() => {
        push.mockClear();
        setEditMode.mockClear();
    });
    describe('showAppPasswordsModal', () => {
        it('should dispatch setEditMode', () => {
            extracted.showAppPasswordsModal.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledWith('apppasswords-list');
        });
        it('should dispatch setEditMode and getTokensList', () => {
            obj.props.appPasswords.tokens.appPasswordsCount = 1;

            extracted.showAppPasswordsModal.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(getTokensList).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledWith('apppasswords-list');
        });
    });
    describe('onLinkClick', () => {
        it('should dispatch setEditMode and showHint', () => {
            extracted.onLinkClick.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(setEditMode).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledWith('apppasswords-list');
            expect(showHint).toHaveBeenCalledTimes(1);
            expect(showHint).toHaveBeenCalledWith('');
        });
        it('should dispatch showRegPopup', () => {
            obj.props.passwordStrength = -1;

            extracted.onLinkClick.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(showRegPopup).toHaveBeenCalledTimes(1);
            expect(showRegPopup).toHaveBeenCalledWith(true);
        });
    });
});
