import { ConfirmByPasswordModel } from '@client/features/confirm-by-password';
import { wait } from '@client/shared/libs/testing';

import * as api from '../api';
import { EMPTY_QUESTION_ID } from '../constants';
import { notifications } from '../libs/notifier';
import * as model from '../model';

jest.mock('next/router', () => require('@client/shared/libs/testing/router'));

describe('account-control-question-model', () => {
  let setQuestionFx: any;

  beforeEach(() => {
    setQuestionFx = api.setQuestionFx.use.getCurrent();
  });

  afterEach(() => {
    api.setQuestionFx.use(setQuestionFx);
  });

  test('should reset new answer when question not selected', () => {
    model.form.fields.newAnswer.onChange('answer');
    expect(model.form.fields.newAnswer.$value.getState()).toBe('answer');

    model.form.fields.selectedQuestionId.onChange(EMPTY_QUESTION_ID);
    expect(model.form.fields.newAnswer.$value.getState()).toBe('');
  });

  test('should reset new question when question is defined', () => {
    model.form.fields.newQuestion.onChange('question');
    expect(model.form.fields.newQuestion.$value.getState()).toBe('question');

    model.form.fields.selectedQuestionId.onChange('100500');
    expect(model.form.fields.newQuestion.$value.getState()).toBe('');
  });

  test('should reset form after dialog is closed', () => {
    model.form.fields.newAnswer.onChange('answer');
    model.dialog.hide();

    expect(model.form.fields.newAnswer.$value.getState()).toBe('');
  });

  test('should submit only valid form', () => {
    model.form.submit();

    expect(model.form.$isValid.getState()).toBeFalsy();

    model.form.fields.type.set(model.FormType.UPDATE);
    model.form.fields.oldAnswer.onChange('old answer');
    model.form.fields.selectedQuestionId.onChange('100500');
    model.form.fields.newAnswer.onChange('new answer');
    model.form.submit();

    expect(model.form.$isValid.getState()).toBeTruthy();
  });

  test('should close dialog after question is setted', async () => {
    const onDone = jest.fn();
    const onHide = jest.fn();
    const onUpdatedSuccessful = jest.fn();
    const fx = jest.fn(() => Promise.resolve(true));

    model.setQuestionFx.done.watch(onDone);
    model.dialog.hide.watch(onHide);
    notifications.updatedSuccessful.watch(onUpdatedSuccessful);
    api.setQuestionFx.use(fx);

    model.form.setForm({
      newAnswer: 'new answer',
      oldAnswer: 'old anaswer',
      selectedQuestionId: '1',
    });
    model.form.submit();

    await wait(0);

    expect(onDone).toBeCalled();
    expect(onHide).toBeCalled();
    expect(onUpdatedSuccessful).toBeCalled();
  });

  test('should set invalid error for old answer when set question is failed', async () => {
    const fx = jest.fn(() => {
      return Promise.reject({ reason: api.SetQuestionProblemKind.CompareNotMatched });
    });

    api.setQuestionFx.use(fx);

    model.form.setForm({
      newAnswer: 'new answer',
      oldAnswer: 'old anaswer',
      selectedQuestionId: '1',
    });
    model.form.submit();

    await wait(0);

    expect(model.form.fields.oldAnswer.$firstError.getState()).toMatchObject({ rule: 'invalid' });
  });

  test('should open password dialog when set question is failed', async () => {
    const onShow = jest.fn();
    const fx = jest.fn(() => {
      return Promise.reject({ reason: api.SetQuestionProblemKind.PasswordRequired });
    });

    ConfirmByPasswordModel.dialog.show.watch(onShow);
    api.setQuestionFx.use(fx);

    model.form.setForm({
      newAnswer: 'new answer',
      oldAnswer: 'old anaswer',
      selectedQuestionId: '1',
    });
    model.form.submit();

    await wait(0);

    expect(onShow).toBeCalled();
  });

  test('should show internal error when set question is failed', async () => {
    const onInternalError = jest.fn();
    const fx = jest.fn(() => {
      return Promise.reject({ reason: api.SetQuestionProblemKind.Internal });
    });

    notifications.internalError.watch(onInternalError);
    api.setQuestionFx.use(fx);

    model.form.setForm({
      newAnswer: 'new answer',
      oldAnswer: 'old anaswer',
      selectedQuestionId: '1',
    });
    model.form.submit();

    await wait(0);

    expect(onInternalError).toBeCalled();
  });
});
