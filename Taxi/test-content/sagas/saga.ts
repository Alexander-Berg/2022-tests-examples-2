import {put, select} from 'typed-redux-saga';

import {pure as commonActions} from '_infrastructure/actions';
import {getStrictModel} from '_infrastructure/selectors';

import {TestSubmode} from '../../../enums';
import {CheckModel, MockModel} from '../../../types';
import {testModel} from '../../../utils';
import {makeDefaultTestCheckModel, makeDefaultTestMockModel, testCheckModel, testMockModel} from '../utils';

export const saga = {
    onLoad: function* (submode: TestSubmode, editIndex: number) {
        if (submode === TestSubmode.CheckEdit) {
            const model: Undefinable<CheckModel> = yield* select(getStrictModel(testModel(m => m.checks[editIndex])));
            yield* put(
                commonActions.form.strict.load(
                    testCheckModel(m => m),
                    model ?? makeDefaultTestCheckModel(),
                ),
            );
        } else if (submode === TestSubmode.MockEdit) {
            const model: Undefinable<MockModel> = yield* select(getStrictModel(testModel(m => m.mocks[editIndex])));
            yield* put(
                commonActions.form.strict.load(
                    testMockModel(m => m),
                    model ?? makeDefaultTestMockModel(),
                ),
            );
        }
    },
};
