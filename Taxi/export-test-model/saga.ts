import {call, put} from 'redux-saga/effects';

import {pure as commonActions} from '_infrastructure/actions';
import {ReturnFuncType} from '_pkg/types/saga';

import {apiInstance} from '../../api/TestRulesAPI';
import {EXPORT_TEST_MODEL} from '../../consts';

export function* onLoad() {
    yield put(commonActions.form.reset(EXPORT_TEST_MODEL));
    const res: ReturnFuncType<typeof apiInstance.getAllTests> = yield call(apiInstance.getAllTests);
    return Object.keys(res).filter(key => res[key].rule_id).map(key => ({label: key, value: res[key].rule_id}));
}
