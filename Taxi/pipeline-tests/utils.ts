import uuid from 'uuid';

import {QueryParsers, stringParser} from '_utils/getFilterFromUrl';
import modelPath from '_utils/modelPath';
import {isNotEmpty} from '_utils/strict/validators';

import {CHECK_MODEL, MOCK_MODEL, TEST_MODEL} from './consts';
import {CheckType, FormMode, TabType, TestType} from './enums';
import {
    CheckModel,
    MockModel,
    QueryParams,
    Resource,
    RouteParams,
    TestcaseMockResourceModel,
    TestcaseModel,
    TestModel,
} from './types';

export const routeParamsParsers: QueryParsers<RouteParams> = {
    service: stringParser(),
};

export const queryParsers: QueryParsers<QueryParams> = {
    tabType: stringParser(TabType.Test),
    mode: stringParser<FormMode>(),
    id: stringParser(),
};

export const mockModel = modelPath(MOCK_MODEL);
export const checkModel = modelPath(CHECK_MODEL);
export const testModel = modelPath(TEST_MODEL);

export const makeDefaultMockModel = (): MockModel => ({
    mockName: '',
    isResourceMock: false,
    resource: '',
    code: '',
});

export const makeDefaultCheckModel = (): CheckModel => ({
    checkName: '',
    checkType: CheckType.Combined,
    ignoreAdditionalParams: false,
    code: '',
});

export const makeDefaultTestcaseMockResourceModel = (): TestcaseMockResourceModel => ({
    resourceName: '',
    mockName: '',
});

export const makeDefaultTestcaseModel = (): TestcaseModel => ({
    _id: uuid.v4(),
    testcaseName: '',
    resourcesMocks: [],
    inputMock: '',
    checks: [],
});

export const makeDefaultTestModel = (): TestModel => ({
    testName: '',
    testType: TestType.Pipeline,
    mocks: [],
    checks: [],
    testcases: [makeDefaultTestcaseModel()],
});

export const isPrefetchedResource = (resource: string, resources: Resource[]): boolean => {
    return resources.some(r => r.is_prefetch_only && r.name === resource);
};

export const filterResourcesMocks = <T extends {resource?: string}>(items: T[], resource: string): T[] => {
    return items.filter(item => isNotEmpty(resource) && item.resource === resource);
};

export const filterMocks = <T extends {resource?: string}>(items: T[]): T[] => {
    return items.filter(item => !item.resource);
};
