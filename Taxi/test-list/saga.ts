import {call} from 'redux-saga/effects';

import {ReturnFuncType} from '_pkg/types/saga';

import TestingService from '../../sagas/services/TestingService';

export function* onLoad(id: string) {
    const res: ReturnFuncType<typeof TestingService.getRuleTests> = yield call(TestingService.getRuleTests, id);
    return res;
}
