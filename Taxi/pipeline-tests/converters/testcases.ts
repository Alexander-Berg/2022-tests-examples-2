import uuid from 'uuid';

import {PipelineTestCase, Resource, TestcaseModel, TestCheckModel, TestMockModel} from '../types';
import {isPrefetchedResource} from '../utils';

export const prepareTestcases = (
    testcases: PipelineTestCase[],
    innerMocks: TestMockModel[],
    innerChecks: TestCheckModel[],
): TestcaseModel[] => {
    return testcases.map(({name, prefetched_resources, input_mock, resource_mocks, output_checks}) => {
        const resourcesMocks = Object.entries({
            ...prefetched_resources,
            ...resource_mocks,
        }).map(([resourceName, mockName]) => ({
            resourceName,
            mockName: innerMocks.find(mock => mock.mockName === mockName)?._id ?? mockName,
        }));

        return {
            _id: uuid.v4(),
            testcaseName: name,
            resourcesMocks,
            inputMock: innerMocks.find(mock => mock.mockName === input_mock)?._id ?? input_mock,
            checks: output_checks.map(checkName => {
                return innerChecks.find(check => check.checkName === checkName)?._id ?? checkName;
            }),
        };
    });
};

export const preparePipelineTestCases = (
    testcases: TestcaseModel[],
    resources: Resource[],
    innerMocks: TestMockModel[],
    innerChecks: TestCheckModel[],
): PipelineTestCase[] => {
    return testcases.map(({testcaseName, resourcesMocks, inputMock, checks}) => ({
        ...resourcesMocks.reduce<Pick<PipelineTestCase, 'resource_mocks' | 'prefetched_resources'>>(
            (acc, {resourceName, mockName: mockId}) => {
                const mockName = innerMocks.find(({_id}) => _id === mockId)?.mockName ?? mockId;
                if (isPrefetchedResource(resourceName, resources)) {
                    acc.prefetched_resources[resourceName] = mockName;
                } else {
                    acc.resource_mocks[resourceName] = mockName;
                }
                return acc;
            },
            {resource_mocks: {}, prefetched_resources: {}},
        ),
        name: testcaseName,
        output_checks: checks.map(checkId => {
            return innerChecks.find(({_id}) => _id === checkId)?.checkName ?? checkId;
        }),
        input_mock: innerMocks.find(({_id}) => _id === inputMock)?.mockName ?? inputMock,
    }));
};
