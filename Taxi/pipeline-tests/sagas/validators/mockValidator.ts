import {getOperation} from '_infrastructure/selectors';
import {formValidator} from '_sagas/validate';
import {StrictModel} from '_types/common/infrastructure';
import modelPath from '_utils/modelPath';

import {LOAD_RESOURCES_ID} from '../../../common/sagas/services/PipelineCommonService';
import {MockModel} from '../../types';
import {isPrefetchedResource} from '../../utils';
import {makeFillError, makeJSONError, makeNameError} from './common';

const mockModelPath = modelPath<MockModel>('', true);

export const makeMockValidator = (model: StrictModel<MockModel>) =>
    formValidator({
        modelPath: model,
        getValidationRules: () => ({}),
        getErrors: (
            {resource = '', mockName, code, isResourceMock}: Partial<MockModel>,
            state,
            {mockNameList}: {mockNameList?: string[]} = {},
        ) => {
            const {result: resources = []} = getOperation(LOAD_RESOURCES_ID)(state);
            const isPrefetched = isPrefetchedResource(resource, resources);
            return {
                ...(isResourceMock
                    ? {
                          ...(!isPrefetched
                              ? {
                                    [mockModelPath(m => m.code)]: makeFillError(code),
                                }
                              : {
                                    [mockModelPath(m => m.code)]: makeJSONError(code),
                                }),
                          [mockModelPath(m => m.resource)]: makeFillError(resource),
                      }
                    : {
                          [mockModelPath(m => m.code)]: makeFillError(code),
                      }),
                [mockModelPath(m => m.mockName)]: makeNameError(mockName, mockNameList),
            };
        },
    });
