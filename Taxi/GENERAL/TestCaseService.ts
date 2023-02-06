import {call, put, select} from 'typed-redux-saga';

import {pure as commonActions} from '_infrastructure/actions';
import {apiInstance} from '_pkg/api/hejmdal-test-case';
import {catchWith, confirm, daemon, Invoke, notifySuccess, operation, pipe, validate} from '_sagas/decorators';
import {showError} from '_sagas/showError';
import {createService} from '_sagas/utils';
import {Service} from '_types/common/infrastructure';
import {assertNotExists} from '_utils/strict/assertNotExists';

import {DEFAULT_TEST_CASE, OPERATIONS, TEXTS} from '../../consts';
import {getRequestModel, getSelectedSchemaId} from '../../selectors';
import {requestModelPath as path} from '../../utils';
import {VALIDATION_OPTIONS} from '../consts';
import {postFindTestCase, preSaveTestCase} from '../matchers';
import {saveTestCaseValidator} from '../validators';
import TestDataService from './TestDataService';

const TEST_CASE_PATH = path(m => m.testCase);

class TestCaseService {
    public static toString = () => 'TestCaseService';

    @operation(OPERATIONS.LOAD_TEST_CASE)
    public static *loadTestCaseList() {
        const schemaId = yield* select(getSelectedSchemaId);

        if (!schemaId) {
            return;
        }

        return yield* call(apiInstance.list, schemaId);
    }

    @operation
    @catchWith(showError)
    public static *findTestCase(testCaseId: number) {
        return yield* call(apiInstance.read, testCaseId);
    }

    @daemon()
    public static *changeTestCase(testCaseId: number) {
        if (testCaseId !== -1) {
            const result = yield* call(TestCaseService.findTestCase, testCaseId);
            const model = postFindTestCase(testCaseId, result);

            yield* put(commonActions.form.strict.change(TEST_CASE_PATH, model));
            yield* put(commonActions.form.resetValidity(TEST_CASE_PATH));
        } else {
            yield* put(
                commonActions.form.strict.merge(TEST_CASE_PATH, {
                    description: DEFAULT_TEST_CASE.description,
                    isEnabled: DEFAULT_TEST_CASE.isEnabled
                })
            );
        }
    }

    @daemon()
    @validate(saveTestCaseValidator, VALIDATION_OPTIONS)
    @catchWith(showError)
    @pipe(TestCaseService.loadTestCaseList, Invoke.After)
    @pipe(TestDataService.loadTestDataList, Invoke.After)
    @notifySuccess(TEXTS.TEST_CASE_CREATED)
    public static *createTestCase() {
        const model = yield* select(getRequestModel);

        const res = yield* call(apiInstance.create, preSaveTestCase(model));

        yield* put(
            commonActions.form.strict.change(
                path(m => m.testCase.id),
                res.test_case_id
            )
        );
    }

    @daemon()
    @confirm()
    @validate(saveTestCaseValidator, VALIDATION_OPTIONS)
    @catchWith(showError)
    @pipe(TestCaseService.loadTestCaseList, Invoke.After)
    @pipe(TestDataService.loadTestDataList, Invoke.After)
    @notifySuccess(TEXTS.TEST_CASE_UPDATED)
    public static *updateTestCase() {
        const model = yield* select(getRequestModel);

        assertNotExists(model.testCase.id);

        yield* call(apiInstance.update, model.testCase.id, preSaveTestCase(model));
    }

    @daemon()
    @confirm()
    @catchWith(showError)
    @pipe(TestCaseService.loadTestCaseList, Invoke.After)
    @pipe(TestDataService.loadTestDataList, Invoke.After)
    @notifySuccess(TEXTS.TEST_CASE_REMOVED)
    public static *removeTestCase() {
        const {testCase} = yield* select(getRequestModel);

        assertNotExists(testCase.id);

        yield* call(apiInstance.delete, testCase.id);

        yield* put(commonActions.form.strict.change(TEST_CASE_PATH, DEFAULT_TEST_CASE));
        yield* put(commonActions.form.resetValidity(TEST_CASE_PATH));
    }

    @daemon()
    @confirm()
    @catchWith(showError)
    @notifySuccess(TEXTS.TEST_CASE_STATUS_CHANGED)
    public static *changeStatus() {
        const {testCase} = yield* select(getRequestModel);

        assertNotExists(testCase.id);

        const res = yield* call(apiInstance.activate, testCase.id, !testCase.isEnabled);
        yield* put(
            commonActions.form.strict.merge(TEST_CASE_PATH, {
                isEnabled: res.is_enabled
            })
        );
    }
}

export const service = createService(TestCaseService, {
    bind: true
});

export default TestCaseService as Service<typeof TestCaseService>;
