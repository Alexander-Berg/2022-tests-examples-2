import {call, put, select} from 'typed-redux-saga';

import {pure as commonActions} from '_infrastructure/actions';
import {apiInstance} from '_pkg/api/hejmdal-test-case';
import {HEJMDAL_TESTING_RESULT_MODAL} from '_pkg/consts';
import {catchWith, daemon, Invoke, operation, pipe} from '_sagas/decorators';
import {showError} from '_sagas/showError';
import createBasicListStrategy from '_sagas/update-strategies/basicListStrategy';
import {createService} from '_sagas/utils';
import {Service} from '_types/common/infrastructure';

import {HEJMDAL_TESTING_MODEL, LOAD_TESTS_LIST} from './consts';
import {getIsEnabledMap, getModel} from './selectors';
import {
    CircuitSchemaJson,
    HejmdalTestingModel,
    RunTestsResponse,
    TestCaseList,
    TestsListItem,
    TestStatus
} from './types';
import {createSelectedMap, extractIdsFromSelectedMap, getStatus} from './utils';

function updateItemStatus(item: TestsListItem, statuses?: Record<number, TestStatus | undefined>) {
    return {
        ...item,
        status: statuses?.[item.id] ?? item.status
    };
}

const updateTestsListStrategy = createBasicListStrategy<TestCaseList, RunTestsResponse>({
    mergeResults: (prev, next) => {
        if (!prev) {
            return prev;
        }

        const statusesMap = next?.test_case_results?.reduce<Record<number, TestStatus | undefined>>((result, item) => {
            const {test_case_id} = item;
            result[test_case_id] = getStatus(item.passed, item.ignored, !!item.error_message);
            return result;
        }, {});

        return {
            enabled: prev.enabled.map(item => updateItemStatus(item, statusesMap)),
            disabled: prev.disabled.map(item => updateItemStatus(item, statusesMap))
        };
    }
});

function* openTestingResultModal(resp: RunTestsResponse) {
    const isEnabledMap = yield* select(getIsEnabledMap);

    const response = {
        ...resp,
        test_case_results: resp.test_case_results.map(item => ({
            ...item,
            enabled: isEnabledMap[item.test_case_id],
            status: getStatus(item.passed, item.ignored, !!item.error_message)
        }))
    };

    yield* put(commonActions.modals.open(HEJMDAL_TESTING_RESULT_MODAL, {response}));
}

function* afterLoadList(schemaId: string, response: TestCaseList) {
    const model: HejmdalTestingModel = {
        enabled: createSelectedMap(response.enabled),
        disabled: createSelectedMap(response.disabled)
    };

    yield* put(commonActions.form.strict.load(HEJMDAL_TESTING_MODEL, model));
}

class HejmdalTestingService {
    @operation
    @catchWith(showError)
    @pipe(function* (_, __, ___, response: RunTestsResponse) {
        yield* call(openTestingResultModal, response);
    }, Invoke.After)
    @operation({
        id: LOAD_TESTS_LIST,
        updateStrategy: updateTestsListStrategy
    })
    private static *runTests(schemaId: string, schemaJson: CircuitSchemaJson, onlySelected: boolean) {
        const model = yield* select(getModel);

        return yield* call(apiInstance.run, {
            break_on_failure: false,
            schema_id: schemaId,
            schema_json: schemaJson,
            test_case_ids: extractIdsFromSelectedMap({...model.enabled, ...model.disabled}, onlySelected)
        });
    }

    public static toString = () => 'HejmdalTestingService';

    @operation(LOAD_TESTS_LIST)
    @pipe(afterLoadList, Invoke.After, false)
    public static *loadList(schemaId: string) {
        return yield* call(apiInstance.list, schemaId);
    }

    @daemon()
    public static *runAllTests(schemaId: string, schemaJson: CircuitSchemaJson) {
        yield* call(HejmdalTestingService.runTests, schemaId, schemaJson, false);
    }

    @daemon()
    public static *runSelectedTests(schemaId: string, schemaJson: CircuitSchemaJson) {
        yield* call(HejmdalTestingService.runTests, schemaId, schemaJson, true);
    }

    @daemon()
    @catchWith(showError)
    @pipe(function* (_, __, ___, response: RunTestsResponse) {
        yield* call(openTestingResultModal, response);
    }, Invoke.After)
    @operation({
        id: LOAD_TESTS_LIST,
        updateStrategy: updateTestsListStrategy
    })
    public static *runTest(schemaId: string, schemaJson: CircuitSchemaJson, id: number) {
        return yield* call(apiInstance.run, {
            break_on_failure: false,
            schema_id: schemaId,
            schema_json: schemaJson,
            test_case_ids: [id]
        });
    }
}

export const service = createService(HejmdalTestingService, {
    bind: true,
    *onBeforeRun(schemaId: string) {
        yield* put(commonActions.form.strict.reset(HEJMDAL_TESTING_MODEL));
        yield* call(HejmdalTestingService.loadList, schemaId);
    }
});

export default HejmdalTestingService as Service<typeof HejmdalTestingService>;
