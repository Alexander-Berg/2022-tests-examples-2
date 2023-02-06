import {call, put} from 'typed-redux-saga';

import {pure as commonActions} from '_infrastructure/actions';

import {IMPORT_TEST_MODEL} from '../../consts';
import TestingService from '../../sagas/services/TestingService';

export function* onLoad() {
    yield* put(commonActions.form.reset(IMPORT_TEST_MODEL));

    yield* call(TestingService.getAllTests);
}
