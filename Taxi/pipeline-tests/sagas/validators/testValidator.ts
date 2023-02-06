import {Errors, formValidator} from '_sagas/validate';
import {StrictModel} from '_types/common/infrastructure';
import modelPath from '_utils/modelPath';
import {isEmpty} from '_utils/strict/validators';

import {TestcaseMockResourceModel, TestcaseModel, TestModel} from '../../types';
import {testModel} from '../../utils';
import {makeFillError, makeNameError} from './common';

const testModelPath = modelPath<TestModel>('', true);

const makeResourceMockErrors = (
    model: StrictModel<TestcaseMockResourceModel>,
    {resourceName, mockName}: TestcaseMockResourceModel,
    resourceNameList: string[],
): Errors => {
    const path = modelPath(model);
    return {
        [path(m => m.resourceName)]: makeFillError(resourceName, resourceNameList),
        [path(m => m.mockName)]: makeFillError(mockName),
    };
};

const makeTestcaseErrors = (
    model: StrictModel<TestcaseModel>,
    {testcaseName, inputMock, resourcesMocks, checks}: TestcaseModel,
    testCaseNameList: string[],
): Errors => {
    const path = modelPath(model);
    const resourceNameList = resourcesMocks.map(({resourceName}) => resourceName);
    return {
        ...(isEmpty(resourcesMocks)
            ? {}
            : resourcesMocks.reduce<Errors>((acc, resourceMock, resourceMockIndex) => {
                  return {
                      ...acc,
                      ...makeResourceMockErrors(
                          path(m => m.resourcesMocks[resourceMockIndex]),
                          resourceMock,
                          resourceNameList.filter((_, i) => i !== resourceMockIndex),
                      ),
                  };
              }, {})),
        [path(m => m.testcaseName)]: makeNameError(testcaseName, testCaseNameList),
        [path(m => m.inputMock)]: makeFillError(inputMock),
        [path(m => m.checks)]: makeFillError(checks),
    };
};

export const testValidator = formValidator({
    modelPath: testModel(m => m),
    getValidationRules: () => ({}),
    getErrors: ({testName, testcases = []}: Partial<TestModel>) => {
        const testCaseNameList = testcases.map(({testcaseName}) => testcaseName);
        return {
            ...testcases.reduce<Errors>((acc, testcase, testCaseIndex) => {
                return {
                    ...acc,
                    ...makeTestcaseErrors(
                        testModelPath(m => m.testcases[testCaseIndex]),
                        testcase,
                        testCaseNameList.filter((_, i) => i !== testCaseIndex),
                    ),
                };
            }, {}),
            [testModelPath(m => m.testName)]: makeNameError(testName),
        };
    },
});
