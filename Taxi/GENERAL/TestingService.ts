import copy from 'copy-to-clipboard';
import {head} from 'lodash';
import {call, put, select} from 'typed-redux-saga';
import uuid from 'uuid';

import {apiInstance as offerApi} from '_api/pricing-admin/PricingAdminAPI';
import {pure as commonActions} from '_infrastructure/actions';
import {getOperation} from '_infrastructure/selectors';
import {catchWith, daemon, modal, notifySuccess, operation, validate} from '_sagas/decorators';
import {showError} from '_sagas/showError';
import createExtendListStrategy from '_sagas/update-strategies/extendListStrategy';
import silentReplaceStrategy from '_sagas/update-strategies/silentReplaceStrategy';
import {createService} from '_sagas/utils';
import {OperationId, Service} from '_types/common/infrastructure';
import {getFilterFromUrl} from '_utils/getFilterFromUrl';
import i18n from '_utils/localization/i18n';
import {prettyJSONStringify} from '_utils/prettyJSONStringify';
import {toNumber} from '_utils/strict/parser';

import {apiInstance} from '../../api/TestRulesAPI';
import {ModificationRequest, RuleWithTest, TestingRuleRequest, TestRequest} from '../../api/types';
import {
    DEFAULT_TESTING_MODEL,
    IMPORT_FROM_ORDER_MODAL,
    IMPORT_TEST_MODAL,
    IMPORT_TEST_MODEL,
    MODEL,
    OrderSource,
    SAVE_TEMPLATE_MODEL,
    TABS,
    TESTING_MODEL,
} from '../../consts';
import {
    operationId as selectedRulesOperationId,
    Service as SelectableService,
} from '../../sagas/services/SelectableService';
import {
    BundleState,
    ImportFromOrderModel, ImportTestModelType,
    MergedModification,
    SaveTemplateModel,
    TestingModel,
    VisitedLines,
} from '../../types';
import {mergeModifications, QUERY_PARSERS, testingModel} from '../../utils';
import importModalValidator from '../validators/importModalValidator';
import importTestModalValidator from '../validators/importTestModalValidator';
import newTestValidator from '../validators/newTestValidator';
import {VISITED_LINES_LIST_ID} from './consts';
import RulesService, {prepareData} from './RulesService';
import {getUserMetadata} from './utils';

const getPartial = <T extends Record<string, unknown>>(obj?: T): Partial<T> => {
    return obj ?? {};
};

export const GET_ALL_TESTS_ID = 'GET_ALL_TESTS_ID' as OperationId<Record<string, RuleWithTest>>;
export const IMPORTED_TEST_JSON_ID = 'IMPORTED_TEST_JSON_ID' as OperationId<string | undefined>;

class TestingService {
    @daemon()
    private static *importTestFromExists() {
        const {testName, ruleName} = yield* select((state: BundleState) => state[IMPORT_TEST_MODEL]);
        const {result: allTests} = yield* select(getOperation(GET_ALL_TESTS_ID));

        if (ruleName && allTests) {
            const importFrom = allTests?.[ruleName]?.rule_id?.toString() || ruleName;

            yield* call(TestingService.changeTestingRoute, {
                view: TABS.TEST,
                importFrom,
                testName,
            });
        }
    }

    @daemon()
    @validate(importTestModalValidator)
    private static *importTestFromJson() {
        const rawJson = yield* select((state: BundleState) => state[IMPORT_TEST_MODEL]?.json);

        if (rawJson) {
            yield* call(TestingService.importedTestJson, rawJson);
            yield* call(TestingService.importedTestJsonHash, uuid.v4());
            yield* call(TestingService.changeTestingRoute, {view: TABS.TEST});
        }
    }

    public static toString = () => 'TestingService';

    @daemon()
    @catchWith(showError)
    public static *runTest() {
        const model = yield* select((state: BundleState) => state[TESTING_MODEL]);
        const ruleModel = yield* select((state: BundleState) => state[MODEL]);
        const ruleName = ruleModel.name;
        const testData = prepareData(model, ruleModel.source_code);

        const data = model.$meta?.isTestChanged
            ? {
                  test_name: model.name,
                  rule_name: ruleName,
                  test_data: testData,
                  rule_id: ruleModel.id,
              }
            : {
                  test_name: model.name,
                  rule_name: ruleName,
                  rule_id: ruleModel.id,
              };
        const res = yield* call(apiInstance.runRuleTest, data);
        yield* put(
            commonActions.form.strict.change(
                testingModel(m => m.$meta.showResult),
                true,
            ),
        );
        yield* put(commonActions.form.setPristine(TESTING_MODEL));
        yield* call(TestingService.visitedLinesTest, model.name, res.visited_lines ?? []);

        return res;
    }

    @daemon()
    @validate(newTestValidator)
    public static *saveNewTest() {
        yield* call(TestingService.runAndSaveTest);
    }

    @daemon()
    public static *editTest() {
        yield* call(TestingService.runAndSaveTest);
    }

    public static *runAndSaveTest() {
        yield* call(TestingService.runTest);
        yield* call(TestingService.saveTest);
    }

    @operation
    @catchWith(showError)
    @notifySuccess('Тест успешно сохранен')
    public static *saveTest() {
        const testingModel: TestingModel = yield* select((state: BundleState) => state[TESTING_MODEL]);
        const model = yield* select((state: BundleState) => state[MODEL]);
        yield* call(TestingService.save, model.name, testingModel.name);
    }

    @daemon()
    @catchWith(showError)
    public static *save(ruleName: string, testName: string) {
        const testingModel: TestingModel = yield* select((state: BundleState) => state[TESTING_MODEL]);
        const model = yield* select((state: BundleState) => state[MODEL]);
        const data: ModificationRequest = {
            rule_name: ruleName,
            test_name: testName,
            test: prepareData(testingModel, model.source_code),
        };
        yield* call(apiInstance.createOrUpdateTest, data);
    }

    @daemon()
    @catchWith(showError)
    @notifySuccess('Шаблон успешно сохранен')
    public static *saveTemplate() {
        const model: SaveTemplateModel = yield* select((state: BundleState) => state[SAVE_TEMPLATE_MODEL]);
        if (model.templateLibrary && model.templateName) {
            yield* call(TestingService.save, model.templateLibrary, model.templateName);
        }
    }

    @daemon()
    @catchWith(showError)
    public static *getRuleTests(ruleId: string) {
        const ruleName = yield* call(TestingService.getRuleNameById, ruleId);
        if (ruleName) {
            const res = yield* call(apiInstance.getTestListForRule, {
                rule_name: ruleName,
                rule_id: toNumber(ruleId),
            });
            const visitedLines = res.reduce<VisitedLines>((acc, val) => {
                acc[val.name] = val.visited_lines ?? [];

                return acc;
            }, {});

            yield* call(TestingService.visitedLinesList, visitedLines);

            return res;
        }
    }

    @daemon()
    @catchWith(showError)
    public static *getTest(testName: string, ruleId?: string, ruleName?: string) {
        if (!ruleId && !ruleName) {
            throw new Error('Не хватает хотя бы одного параметра: ruleId/ruleName');
        }
        const name = ruleId ? yield* call(TestingService.getRuleNameById, ruleId) : ruleName;
        if (!name) {
            return;
        }
        const data: TestingRuleRequest & TestRequest = {
            rule_name: name,
            test_name: testName,
            rule_id: toNumber(ruleId),
        };
        const res = yield* call(apiInstance.getRuleTestByName, data);
        return res;
    }

    @daemon()
    @catchWith(showError)
    public static *getTestByRuleName(testName: string, ruleName?: string) {
        if (!ruleName) {
            return;
        }
        const data = {
            rule_name: ruleName,
            test_name: testName,
        };
        const res = yield* call(apiInstance.getRuleTestByName, data);
        return res;
    }

    @daemon()
    @catchWith(showError)
    public static *getRuleNameById(ruleId: string) {
        const operationSelector = getOperation(RulesService.loadRule.id);
        const operation = yield* select(operationSelector);
        if (operation.args?.[0] === ruleId) {
            return operation.result?.name;
        }
        const rule = yield* call(RulesService.loadRule, ruleId);
        return rule.name;
    }

    @daemon()
    @catchWith(showError)
    public static *deleteTest(ruleId: string, testName: string) {
        const ruleName = yield* call(TestingService.getRuleNameById, ruleId);
        if (!ruleName) {
            return;
        }
        yield* call(apiInstance.deleteTest, {rule_name: ruleName, test_name: testName});
        yield* call(TestingService.changeTestingRoute, {view: TABS.LIST});
        yield* call(TestingService.getRuleTests, ruleId);
    }

    @daemon()
    @catchWith(showError)
    public static *runAllRuleTests(ruleId: string) {
        const ruleName = yield* call(TestingService.getRuleNameById, ruleId);
        if (!ruleName) {
            return;
        }
        yield* call(apiInstance.runAllRuleTests, {rule_id: toNumber(ruleId), rule_name: ruleName});
        yield* call(TestingService.getRuleTests, ruleId);
    }

    @daemon()
    @catchWith(showError)
    public static *runSelectedRuleTests() {
        const {result: selectedRules = []} = yield* select(getOperation(selectedRulesOperationId));
        const selectedRuleIds = selectedRules.map(rule => Number(rule));

        yield* call(SelectableService.reset);
        yield* call(apiInstance.runSelectedRuleTests, {rule_ids: selectedRuleIds});
        yield* call(RulesService.loadRules, {reset: true});
    }

    @daemon()
    @catchWith(showError)
    public static *changeTestingRoute({
        view,
        history,
        testName,
        importFrom,
        importFromOrder,
        source,
    }: {
        view?: string;
        history?: boolean;
        testName?: string;
        importFrom?: string;
        importFromOrder?: string;
        source?: string;
    }) {
        yield* put(
            commonActions.router.pushWithQuery('', {view, history, testName, importFrom, importFromOrder, source}),
        );
    }

    @daemon()
    @catchWith(showError)
    public static *getOffer(offerId: string) {
        return yield* call(offerApi.getFastData, offerId);
    }

    @daemon()
    @catchWith(showError)
    public static *importFromOrder(model: string, orderId: string) {
        const {useYtData, source, modificationSource} = getFilterFromUrl(QUERY_PARSERS);
        const ruleModel = yield* select((state: BundleState) => state[MODEL]);
        const fastData = yield* call(TestingService.getOffer, orderId);
        const ytData = yield* call(offerApi.getYData, {order_id: orderId});
        const ytDataOrder = head(ytData?.orders);
        const ydataOffer = ytData?.offer;
        const tripDetails = getPartial(ytDataOrder?.[source].trip_details);
        const offer = fastData?.offer;
        const isDriverSource = source === OrderSource.Driver;
        const backendVariables = isDriverSource
            ? fastData?.backend_variables?.driver
            : fastData?.backend_variables?.user;
        const {user: userData, driver: driverData} = ydataOffer || {};
        const ytModifications = isDriverSource ? driverData?.modifications : userData?.modifications;
        const fastDataModifications = isDriverSource ? offer?.modifications?.driver : offer?.modifications?.user;

        const fastDataBasePrice = isDriverSource ? offer?.base_price?.driver : offer?.base_price?.user;
        const ytBasePrice = isDriverSource ? driverData?.base_price : userData?.base_price;
        const basePrice = useYtData ? ytBasePrice || fastDataBasePrice : fastDataBasePrice;

        const modifications: MergedModification[] =
            useYtData && ytModifications
                ? mergeModifications(fastDataModifications, ytModifications)
                : fastDataModifications;
        const currentModificationIndex = modifications.findIndex(item => item.id === ruleModel.id);
        const prevModificationIndex = currentModificationIndex - 1;
        const prevModification = modifications[prevModificationIndex];
        const metadata = getUserMetadata(ytData, modificationSource);
        const {
            boarding = 0,
            distance = 0,
            time = 0,
            waiting = 0,
            requirements = 0,
            transit_waiting = 0,
            destination_waiting = 0,
        } = prevModification?.price ?? {
            boarding: basePrice?.boarding,
            time: basePrice?.time,
            distance: basePrice?.distance,
            total: basePrice?.total,
        };
        yield* put(
            commonActions.form.strict.load(model as any, {
                ...DEFAULT_TESTING_MODEL,
                trip_details: {
                    ...DEFAULT_TESTING_MODEL.trip_details,
                    total_distance: tripDetails.total_distance,
                    total_time: tripDetails.total_time,
                    waiting_time: tripDetails.waiting_time,
                    waiting_in_transit_time: tripDetails.waiting_in_transit_time,
                    waiting_in_destination_time: tripDetails.waiting_in_destination_time,
                    user_meta: metadata,
                },
                initial_price: {
                    boarding: boarding,
                    distance: distance,
                    time: time,
                    waiting: waiting,
                    requirements: requirements,
                    transit_waiting: transit_waiting,
                    destination_waiting: destination_waiting,
                },
                backend_variables: prettyJSONStringify(backendVariables),
            }),
        );
    }

    @daemon()
    @modal(IMPORT_FROM_ORDER_MODAL)
    @validate(importModalValidator)
    public static *openImportModal(view?: string, model?: ImportFromOrderModel) {
        const {orderId, source} = model || {};
        yield* call(TestingService.changeTestingRoute, {view, importFromOrder: orderId, source});
    }

    @operation
    public static *visitedLinesDebug(values: Array<number>) {
        return values;
    }

    @operation({
        id: VISITED_LINES_LIST_ID,
        updateStrategy: createExtendListStrategy<VisitedLines, VisitedLines>({
            mergeResults: (prev, next) => {
                return {
                    ...(prev ?? {}),
                    ...(next ?? {}),
                };
            },
        }),
    })
    public static *visitedLinesTest(name: string, lines: Array<number>) {
        return {
            [name]: lines,
        };
    }

    @operation({
        id: VISITED_LINES_LIST_ID,
    })
    public static *visitedLinesList(val: VisitedLines) {
        return val;
    }

    @daemon()
    @notifySuccess(i18n.print('copied'))
    public static *copyTestAsJsonToClipboard() {
        const testingModel = yield* select((state: BundleState) => state[TESTING_MODEL]);
        copy(prettyJSONStringify(testingModel));
    }

    @daemon()
    @operation({
        id: GET_ALL_TESTS_ID,
    })
    public static *getAllTests() {
        return yield* call(apiInstance.getAllTests);
    }

    @daemon()
    @validate(importTestModalValidator)
    public static *importTest() {
        yield* put(commonActions.modals.close(IMPORT_TEST_MODAL));

        const tab = yield* select((state: BundleState) => state[IMPORT_TEST_MODEL].tab);
        if (tab === ImportTestModelType.Default) {
            yield* call(TestingService.importTestFromExists);
        } else {
            yield* call(TestingService.importTestFromJson);
        }
    }

    @daemon()
    @operation({
        id: IMPORTED_TEST_JSON_ID,
        updateStrategy: silentReplaceStrategy,
    })
    public static *importedTestJson(json: string | undefined) {
        return json;
    }

    /**
     * Get imported test json and clear
     */
    @daemon()
    public static *getImportedTestJson() {
        const json = (yield* select(getOperation(IMPORTED_TEST_JSON_ID))).result;
        yield* call(TestingService.importedTestJson, undefined);
        return json;
    }

    @daemon()
    @operation({
        updateStrategy: silentReplaceStrategy,
    })
    public static *importedTestJsonHash(hash: string) {
        return hash;
    }
}

export const service = createService(TestingService, {bind: true});
export default TestingService as Service<typeof TestingService>;
