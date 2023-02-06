import {call, put, select} from 'typed-redux-saga';

import {pure as commonActions} from '_infrastructure/actions';
import {getOperation} from '_infrastructure/selectors';
import {jsonParse} from '_utils/parser';
import {prettyJSONStringify} from '_utils/prettyJSONStringify';
import {isNumber} from '_utils/strict/validators';

import {DEFAULT_TESTING_MODEL, TESTING_MODEL} from '../../consts';
import TestingService from '../../sagas/services/TestingService';
import {TestingModel} from '../../types';
import {testingModel as testingModelPath} from '../../utils';

export function* onLoad(
    ruleId: string,
    testName?: string,
    importFrom?: string,
    importFromOrder?: string,
    source?: string,
    hash?: string, // To run this saga after run importTestFromJson
) {
    yield* put(commonActions.form.strict.reset(testingModelPath(m => m)));
    const operationSelector = getOperation(TestingService.getRuleTests.id);
    const ruleTestsRes = yield* select(operationSelector);
    if (!ruleTestsRes.result || ruleTestsRes.args?.[0] !== ruleId) {
        yield* call(TestingService.getRuleTests, ruleId);
    }
    if (importFromOrder) {
        yield* call(TestingService.importFromOrder, TESTING_MODEL, importFromOrder);
        return;
    }

    if (!testName) {
        const importedJson = yield* call(TestingService.getImportedTestJson);

        const res: TestingModel | undefined = importedJson ? jsonParse(importedJson) : undefined;

        if (!res) {
            yield* put(
                commonActions.form.strict.load(
                    testingModelPath(m => m),
                    DEFAULT_TESTING_MODEL,
                ),
            );
            return;
        }

        const testingModel = {
            ...res,
            $meta: {
                isTestChanged: false,
                showResult: true,
            },
        };

        // TODO validate before use?
        yield* put(
            commonActions.form.strict.load(
                testingModelPath(m => m),
                testingModel,
            ),
        );
    } else {
        const res =
            !importFrom || isNumber(importFrom)
                ? yield* call(TestingService.getTest, testName, importFrom || ruleId)
                : yield* call(TestingService.getTestByRuleName, testName, importFrom);

        const testingModel: TestingModel = {
            ...res,
            name: testName,
            source_code: '',
            trip_details: {
                total_distance: res?.trip_details?.total_distance || 0,
                total_time: res?.trip_details?.total_time || 0,
                waiting_time: res?.trip_details?.waiting_time || 0,
                waiting_in_transit_time: res?.trip_details?.waiting_in_transit_time || 0,
                waiting_in_destination_time: res?.trip_details?.waiting_in_destination_time || 0,
                user_options: Object.keys(res?.trip_details.user_options || {}).map(key => ({
                    key,
                    value: res?.trip_details.user_options?.[key]?.toString() || '',
                })),
                user_meta: Object.keys(res?.trip_details.user_meta || {}).map(key => ({
                    key,
                    value: res?.trip_details.user_meta?.[key]?.toString() || '',
                })),
            },
            initial_price: res?.initial_price ?? {
                boarding: 0,
                distance: 0,
                time: 0,
                waiting: 0,
                requirements: 0,
                transit_waiting: 0,
                destination_waiting: 0,
            },
            output_price: res?.output_price ?? {
                boarding: 0,
                distance: 0,
                time: 0,
                waiting: 0,
                requirements: 0,
                transit_waiting: 0,
                destination_waiting: 0,
            },
            price_calc_version: '',
            output_meta: Object.keys(res?.output_meta || {}).map(key => ({
                key,
                value: res?.output_meta?.[key] ? `${res?.output_meta[key]}` : '',
            })),
            backend_variables: prettyJSONStringify(res?.backend_variables),
            $meta: {
                isTestChanged: importFrom !== undefined,
                showResult: false,
            },
        };

        yield* put(
            commonActions.form.strict.load(
                testingModelPath(m => m),
                testingModel,
            ),
        );
    }
}
