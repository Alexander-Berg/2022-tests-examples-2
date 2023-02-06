import {call, put, select} from 'typed-redux-saga';

import {pure as commonActions} from '_infrastructure/actions';
import {apiInstance} from '_pkg/api/hejmdal-test-data';
import {catchWith, confirm, daemon, Invoke, notifySuccess, operation, pipe, validate} from '_sagas/decorators';
import {showError} from '_sagas/showError';
import {createService} from '_sagas/utils';
import {Service} from '_types/common/infrastructure';
import {assertNotExists} from '_utils/strict/assertNotExists';

import {DEFAULT_TEST_DATA, EMPTY_GRAPH_DATA, MODELS, OPERATIONS, TEXTS} from '../../consts';
import {getRequestModel, getSelectedSchemaId} from '../../selectors';
import {NamedTimeSeries} from '../../types';
import {requestModelPath as path} from '../../utils';
import {VALIDATION_OPTIONS} from '../consts';
import {postFindTestData, preSaveTestData} from '../matchers';
import {createGraphData, createGraphSettings} from '../utils';
import {saveTestDataValidator} from '../validators';

const TEST_DATA_PATH = path(m => m.testData);

function* updateGraph(timeSeries: NamedTimeSeries[]) {
    const graphBaseData = createGraphData(timeSeries);
    const graphTestData = EMPTY_GRAPH_DATA;
    const graphSettings = {
        selected: createGraphSettings(graphBaseData)
    };

    yield* put(
        commonActions.form.strict.merge(MODELS.REQUEST, {
            graphBaseData,
            graphTestData,
            graphSettings
        })
    );
}

class TestDataService {
    public static toString = () => 'TestDataService';

    @operation(OPERATIONS.LOAD_TEST_DATA)
    public static *loadTestDataList() {
        const schemaId = yield* select(getSelectedSchemaId);

        if (!schemaId) {
            return;
        }

        return yield* call(apiInstance.list, schemaId);
    }

    @catchWith(showError)
    public static *findTestData(testDataId: number) {
        const res = yield* call(apiInstance.read, testDataId);
        yield* call(updateGraph, res.test_data);
        return res;
    }

    @daemon()
    public static *changeTestData(testDataId: number) {
        if (testDataId !== -1) {
            const result = yield* call(TestDataService.findTestData, testDataId);
            const model = postFindTestData(testDataId, result);

            yield* put(commonActions.form.strict.change(TEST_DATA_PATH, model));
            yield* put(commonActions.form.resetValidity(TEST_DATA_PATH));
        } else {
            const descriptionPath = path(m => m.testData.description);
            yield* put(commonActions.form.change(descriptionPath, DEFAULT_TEST_DATA.description));
            yield* call(updateGraph, []);
        }
    }

    @daemon()
    @validate(saveTestDataValidator, VALIDATION_OPTIONS)
    @catchWith(showError)
    @pipe(TestDataService.loadTestDataList, Invoke.After)
    @notifySuccess(TEXTS.TEST_DATA_CREATED)
    public static *createTestData() {
        const model = yield* select(getRequestModel);

        const data = preSaveTestData(model);
        const res = yield* call(apiInstance.create, data);

        yield* put(
            commonActions.form.strict.change(
                path(m => m.testData.id),
                res.test_data_id
            )
        );
    }

    @daemon()
    @confirm()
    @validate(saveTestDataValidator, VALIDATION_OPTIONS)
    @catchWith(showError)
    @pipe(TestDataService.loadTestDataList, Invoke.After)
    @notifySuccess(TEXTS.TEST_DATA_UPDATED)
    public static *updateTestData() {
        const model = yield* select(getRequestModel);

        assertNotExists(model.testData.id);

        const data = preSaveTestData(model);
        yield* call(apiInstance.update, model.testData.id, data);
    }

    @daemon()
    @confirm()
    @catchWith(showError)
    @pipe(TestDataService.loadTestDataList, Invoke.After)
    @notifySuccess(TEXTS.TEST_DATA_REMOVED)
    public static *removeTestData() {
        const {testData} = yield* select(getRequestModel);

        assertNotExists(testData.id);

        yield* call(apiInstance.delete, testData.id);

        yield* put(commonActions.form.strict.change(TEST_DATA_PATH, DEFAULT_TEST_DATA));
        yield* put(commonActions.form.resetValidity(TEST_DATA_PATH));
    }
}

export const service = createService(TestDataService, {
    bind: true
});

export default TestDataService as Service<typeof TestDataService>;
