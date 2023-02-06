import {RunTestsResponse, TestCaseResult} from '_pkg/api/hejmdal-test-case/types';

export enum TestStatus {
    Success,
    Error,
    Default
}

export type TestsResponse = Assign<
    RunTestsResponse,
    {
        test_case_results: TestResultItem[];
    }
>;

export type TestResultItem = Assign<
    TestCaseResult,
    {
        enabled?: boolean;
        status?: TestStatus;
    }
>;
