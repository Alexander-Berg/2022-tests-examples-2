import {call} from 'typed-redux-saga';

import {fieldSagaFactory, makeSelect} from '_blocks/amber-async-entity-select';
import {apiInstance} from '_pkg/api/test-kinds/TestKindsAPI';
import {operationRunner} from '_sagas/createOperation';
import {cache} from '_sagas/utils';
import {arrayOfStringToOptions} from '_utils/stringToOption';

const EXPIRATION_TIME = 60 * 1000;

export const LOAD_TEST_KINDS_OPERATION_ID = 'LOAD_TEST_KINDS_OPERATION_ID';

const loadOperation = operationRunner(LOAD_TEST_KINDS_OPERATION_ID, function* () {
    const {test_kinds} = yield* call(apiInstance.request);

    return arrayOfStringToOptions(test_kinds.map(x => x.id));
});

const TestKindsSelect = makeSelect(fieldSagaFactory(cache(loadOperation.run, {expire: EXPIRATION_TIME})));

export default TestKindsSelect;
