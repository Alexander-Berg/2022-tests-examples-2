import {push} from 'react-router-redux';

import {clearPersonalInfoFieldsErrors} from '../../../personal_info/actions';
import {setEditMode} from '../../../../common/actions';

import metrics from '../../../../metrics';

import * as extracted from '../personal_info.js';

jest.mock('react-router-redux', () => ({
    push: jest.fn()
}));
jest.mock('../../../personal_info/actions', () => ({
    clearPersonalInfoFieldsErrors: jest.fn()
}));
jest.mock('../../../../common/actions', () => ({
    setEditMode: jest.fn()
}));
jest.mock('../../../../metrics', () => ({
    goal: jest.fn(),
    send: jest.fn()
}));

describe('Morda.PersonalInfo', () => {
    const event = {
        preventDefault: jest.fn()
    };

    let obj = null;

    beforeEach(() => {
        obj = {
            props: {
                settings: {
                    isTouch: false,
                    env: {}
                },
                dispatch: jest.fn(),
                securityLevel: 123
            }
        };
    });
    afterEach(() => {
        push.mockClear();
        setEditMode.mockClear();
        event.preventDefault.mockClear();
    });
    describe('sendGoal', () => {
        it('should send metrics', () => {
            extracted.sendGoal.call(obj);
            expect(metrics.goal).toHaveBeenCalledTimes(1);
            expect(metrics.goal).toHaveBeenCalledWith(`profile_page_security_level_${obj.props.securityLevel}`);
        });
    });
    describe('showDisplayNameEditForm', () => {
        it('should dispatch setEditMode and call preventDefault', () => {
            extracted.showDisplayNameEditForm.call(obj, event);
            expect(event.preventDefault).toHaveBeenCalledTimes(1);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledWith('display-name');
        });
        it('should dispatch push and call preventDefault', () => {
            obj.props.isTouch = true;

            extracted.showDisplayNameEditForm.call(obj, event);
            expect(event.preventDefault).toHaveBeenCalledTimes(1);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(push).toHaveBeenCalledTimes(1);
            expect(push).toHaveBeenCalledWith(extracted.DISPLAY_NAME);
        });
    });
    describe('showPersonalInfoEditForm', () => {
        it('should dispatch setEditMode and call preventDefault', () => {
            extracted.showPersonalInfoEditForm.call(obj, event);
            expect(event.preventDefault).toHaveBeenCalledTimes(1);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledWith('personal-info');
        });
        it('should dispatch push and call preventDefault', () => {
            obj.props.isTouch = true;

            extracted.showPersonalInfoEditForm.call(obj, event);
            expect(event.preventDefault).toHaveBeenCalledTimes(1);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(push).toHaveBeenCalledTimes(1);
            expect(push).toHaveBeenCalledWith(extracted.PERSONAL_INFO);
        });
    });
    describe('closePersonalInfoEditForm', () => {
        it('should dispatch clearPersonalInfoFieldsErrors and setEditMode, and send metrics', () => {
            extracted.closePersonalInfoEditForm.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(clearPersonalInfoFieldsErrors).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledWith('');
            expect(metrics.send).toHaveBeenCalledTimes(1);
            expect(metrics.send).toHaveBeenCalledWith([extracted.METRICS_HEADER, 'Отменить']);
        });
    });
});
