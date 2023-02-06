import {push} from 'react-router-redux';

import {setEditMode} from '../../../../common/actions';
import {changeEmailsState, EMAILS_GOAL_PREFIX, EMAILS_URLS} from '../../../emails/actions';

import metrics from '../../../../metrics';

import * as extracted from '../mails_restore.js';

jest.mock('react-router-redux', () => ({
    push: jest.fn()
}));
jest.mock('../../../../common/actions', () => ({
    setEditMode: jest.fn()
}));
jest.mock('../../../emails/actions', () => ({
    changeEmailsState: jest.fn(),
    EMAILS_GOAL_PREFIX: 'EMAILS_GOAL_PREFIX',
    EMAILS_URLS: {
        list: '/profile/emails/list',
        'list-initial': '/profile/emails/list',
        add: '/profile/emails/add',
        'add-initial': '/profile/emails/add'
    }
}));
jest.mock('../../../../metrics', () => ({
    goal: jest.fn()
}));

describe('Morda.MailsBlock.MailsRestore', () => {
    const event = {preventDefault: () => {}};

    let obj = null;

    beforeEach(() => {
        obj = {
            props: {
                dispatch: jest.fn(),
                isTouch: false
            }
        };
    });
    afterEach(() => {
        metrics.goal.mockClear();
        changeEmailsState.mockClear();
    });
    describe('showModal', () => {
        it('should dispatch changeEmailsState and setEditMode, and send add goal', () => {
            const state = extracted.ADD_STATE;

            extracted.showModal.call(obj, state, event);
            expect(metrics.goal).toHaveBeenCalledTimes(1);
            expect(metrics.goal).toHaveBeenCalledWith(`${EMAILS_GOAL_PREFIX}_add_open`);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(changeEmailsState).toHaveBeenCalledTimes(1);
            expect(changeEmailsState).toHaveBeenCalledWith(state);
            expect(setEditMode).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledWith('emails');
        });
        it('should dispatch changeEmailsState and push, and send list goal', () => {
            obj.props.isTouch = true;
            const state = extracted.LIST_STATE;

            extracted.showModal.call(obj, state, event);
            expect(metrics.goal).toHaveBeenCalledTimes(1);
            expect(metrics.goal).toHaveBeenCalledWith(`${EMAILS_GOAL_PREFIX}_list_open`);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(changeEmailsState).toHaveBeenCalledTimes(1);
            expect(changeEmailsState).toHaveBeenCalledWith(state);
            expect(push).toHaveBeenCalledTimes(1);
            expect(push).toHaveBeenCalledWith(EMAILS_URLS[state]);
        });
    });
});
