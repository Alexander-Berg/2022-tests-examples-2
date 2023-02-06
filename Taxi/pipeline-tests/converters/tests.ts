import {concat} from 'lodash';

import {isNotEmpty} from '_utils/strict/validators';

import {TestType} from '../enums';
import {PipelineTest, Resource, TestModel} from '../types';
import {
    prepareInputMocks,
    prepareOutputChecks,
    preparePipelineTestCases,
    preparePrefetchedMocks,
    prepareResourcedMocks,
    prepareTestcases,
    prepareTestCheckModels,
    prepareTestMockModels,
} from './index';

export const prepareTest = ({
    name,
    scope,
    testcases,
    prefetched_resources_mocks,
    resources_mocks,
    input_mocks,
    output_checks,
}: PipelineTest): TestModel => {
    const mocks = concat(
        preparePrefetchedMocks(prefetched_resources_mocks),
        prepareResourcedMocks(resources_mocks),
        prepareInputMocks(input_mocks),
    );

    const checks = prepareOutputChecks(output_checks);

    return {
        testName: name,
        testType: scope === TestType.Global ? TestType.Global : TestType.Pipeline,
        mocks,
        checks,
        testcases: prepareTestcases(testcases, mocks, checks),
    };
};

export const preparePipelineTest = (
    {mocks, checks, testcases, testName, testType}: TestModel,
    resources: Resource[],
    id: string,
): PipelineTest => {
    return {
        ...prepareTestMockModels(mocks, resources),
        ...(isNotEmpty(checks)
            ? {
                  output_checks: prepareTestCheckModels(checks),
              }
            : {}),
        testcases: preparePipelineTestCases(testcases, resources, mocks, checks),
        id,
        name: testName,
        scope: testType,
    };
};
