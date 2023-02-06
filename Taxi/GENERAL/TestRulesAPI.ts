import {adminApi} from '_utils/httpApi';

import {TestRule} from '../types';
import {
    ModificationRequest,
    RuleTest,
    RuleTestSummary,
    RuleTestWithResult,
    RuleWithTest,
    TestingResponse,
    TestingRuleRequest,
    TestingRuleResult,
    TestRequest,
    TestRuleData,
    TestRuleQuery,
    TestRuleResponse,
    TestRulesQuery,
} from './types';

const URL_ROOT = 'pricing-admin/v1/testing';

export default class TestRulesAPI {
    public static toString = () => 'TestRulesAPI';

    public runSingleTest(data: TestRule): Promise<TestingResponse> {
        return adminApi.post<TestRule, TestingResponse>(`${URL_ROOT}/run`, data);
    }

    public getTestListForRule(data: TestingRuleRequest): Promise<RuleTestSummary[]> {
        return adminApi.get<TestingRuleRequest, TestingRuleResult>(`${URL_ROOT}/rule`, data).then(res => res.tests);
    }

    public runAllRuleTests(data: TestingRuleRequest): Promise<void> {
        return adminApi.post<{}, void>(`${URL_ROOT}/rule`, {}, {
            query: data,
        });
    }

    public createOrUpdateTest(data: ModificationRequest) {
        return adminApi.put<
            {
                test: RuleTest;
            },
            void
        >(`${URL_ROOT}/test`, {test: data.test}, {query: {rule_name: data.rule_name, test_name: data.test_name}});
    }

    public deleteTest(data: TestRequest): Promise<void> {
        return adminApi.del<TestRequest, void>(`${URL_ROOT}/test`, null, {query: data});
    }

    public getRuleTestByName(data: TestingRuleRequest & TestRequest): Promise<RuleTestWithResult> {
        return adminApi.get<TestingRuleRequest & TestRequest, RuleTestWithResult>(`${URL_ROOT}/test`, data);
    }

    public runRuleTest(data: TestRuleQuery & TestRuleData): Promise<TestRuleResponse> {
        return adminApi.post<TestRuleData, TestRuleResponse>(
            `${URL_ROOT}/test`,
            {
                test_data: data.test_data,
                rule_id: data.rule_id,
            },
            {query: {test_name: data.test_name, rule_name: data.rule_name}},
        );
    }

    public getAllTests(): Promise<Record<string, RuleWithTest>> {
        return adminApi.get<void, Record<string, RuleWithTest>>(`${URL_ROOT}/rules`);
    }

    public runSelectedRuleTests(data: TestRulesQuery): Promise<void> {
        return adminApi.post<TestRulesQuery, void>(`${URL_ROOT}/rules`, data);
    }
}

export const apiInstance = new TestRulesAPI();
