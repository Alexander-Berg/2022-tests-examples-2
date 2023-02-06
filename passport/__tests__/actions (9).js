import api from '../../../../api';
import {saveActionForRepeat} from '../../../../common/actions';

import * as actions from '../actions';

jest.mock('../../../../api', () => {
    class Request {
        request(path, opts) {
            this.path = path;
            this.options = opts;
            return this;
        }
        done(func) {
            this.onDone = func;
            return this;
        }
        fail(func) {
            this.onFail = func;
            return this;
        }
        always(func) {
            this.onAlways = func;
            return this;
        }
    }

    return new Request();
});

jest.mock('../../../../common/actions', () => ({
    saveActionForRepeat: jest.fn()
}));

describe('Morda.Security.UserQuestion.actions', () => {
    const getState = () => ({
        common: {
            uid: 'uid',
            track_id: 'value'
        },
        security: {
            controlQuestion: {
                available: [
                    {
                        val: 'value',
                        text: 'some'
                    }
                ],
                errors: []
            }
        },
        settings: {
            language: 'ru'
        }
    });
    const dispatch = jest.fn();

    afterEach(() => {
        dispatch.mockClear();
        saveActionForRepeat.mockClear();
    });

    test('showKvKo', () => {
        const visible = 'value';

        expect(actions.showKvKo(visible)).toEqual({
            type: actions.SHOW_KVKO_MODAL,
            visible
        });
    });
    test('setKvKoUpdateStatus', () => {
        const updated = 'value';

        expect(actions.setKvKoUpdateStatus(updated)).toEqual({
            type: actions.SET_KVKO_UPDATE_STATUS,
            updated
        });
    });
    test('validateForm', () => {
        const data = 'value';

        expect(actions.validateForm(data)).toEqual({
            type: actions.VALIDATE_KVKO_FORM,
            data
        });
    });
    test('setQuestions', () => {
        const questions = 'value';

        expect(actions.setQuestions(questions)).toEqual({
            type: actions.SET_QUESTIONS,
            questions
        });
    });
    test('changeQuestion', () => {
        const id = 'value';

        expect(actions.changeQuestion(id)).toEqual({
            type: actions.CHANGE_CONTROL_QUESTION,
            id
        });
    });
    describe('saveKvKo', () => {
        test('api params', () => {
            const state = getState();
            const {uid, track_id} = state.common;
            const {language} = state.settings;
            const data = {
                some: 'data'
            };

            actions.saveKvKo(data)(dispatch, getState);
            expect(api.path).toBe('saveQuestion');
            expect(api.options).toEqual(
                Object.assign({}, data, {
                    uid,
                    track_id,
                    language
                })
            );
        });
        it('should not dispatch any', () => {
            const state = getState();

            actions.saveKvKo()(dispatch, () =>
                Object.assign({}, state, {
                    security: {
                        controlQuestion: {
                            errors: [1]
                        }
                    }
                })
            );
            expect(dispatch).toHaveBeenCalledTimes(0);
        });
        describe('success', () => {
            test('if not ownQuestion', () => {
                const data = {
                    newQuestionId: 'value'
                };

                actions.saveKvKo(data)(dispatch, getState);
                api.onDone();
                expect(saveActionForRepeat).toHaveBeenCalledTimes(1);
                expect(dispatch).toHaveBeenCalledTimes(3);
                expect(dispatch.mock.calls[0][0]).toEqual({
                    type: actions.SAVE_KVKO
                });
                expect(dispatch.mock.calls[2][0]).toEqual({
                    type: actions.SAVE_KVKO_SUCCESS,
                    currentQuestion: {
                        id: data.newQuestionId,
                        text: 'some'
                    }
                });
            });
            it('if ownQuestion', () => {
                const data = {
                    newQuestionId: 'value',
                    ownQuestion: 'value'
                };

                actions.saveKvKo(data)(dispatch, getState);
                api.onDone();
                expect(saveActionForRepeat).toHaveBeenCalledTimes(1);
                expect(dispatch).toHaveBeenCalledTimes(3);
                expect(dispatch.mock.calls[0][0]).toEqual({
                    type: actions.SAVE_KVKO
                });
                expect(dispatch.mock.calls[2][0]).toEqual({
                    type: actions.SAVE_KVKO_SUCCESS,
                    currentQuestion: {
                        id: data.newQuestionId,
                        text: data.ownQuestion
                    }
                });
            });
        });
        test('fail', () => {
            const res = 'value';

            actions.saveKvKo()(dispatch, getState);
            api.onFail(res);
            expect(saveActionForRepeat).toHaveBeenCalledTimes(1);
            expect(dispatch).toHaveBeenCalledTimes(3);
            expect(dispatch.mock.calls[0][0]).toEqual({
                type: actions.SAVE_KVKO
            });
            expect(dispatch.mock.calls[2][0]).toEqual({
                type: actions.SAVE_KVKO_FAIL,
                res
            });
        });
    });
});
