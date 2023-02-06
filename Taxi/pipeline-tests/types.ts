import {CheckType, FormMode, TabType, TestType} from './enums';

export type RouteParams = {
    service?: string;
};

export type QueryParams = {
    tabType: TabType;
    mode?: FormMode;
    id?: string;
};

export type MockModel = {
    mockName: string;
    isResourceMock: boolean;
    resource: string;
    code: string;
};

export type CheckModel = {
    checkName: string;
    checkType: CheckType,
    ignoreAdditionalParams: boolean;
    code: string;
};

export type TestcaseMockResourceModel = {
    resourceName: string;
    mockName: string;
};

export type TestcaseModel = {
    _id: string;
    testcaseName: string;
    resourcesMocks: TestcaseMockResourceModel[];
    inputMock: string;
    checks: string[];
};

export type TestCheckModel = CheckModel & {
    _id: string;
};

export type TestMockModel = MockModel & {
    _id: string;
};

export type TestModel = {
    testName: string;
    testType: TestType;
    mocks: TestMockModel[];
    checks: TestCheckModel[];
    testcases: TestcaseModel[];
};

export * from '../common/api/types';
