import {formValidator} from '_sagas/validate';
import {StrictModel} from '_types/common/infrastructure';
import modelPath from '_utils/modelPath';

import {CheckType} from '../../enums';
import {CheckModel} from '../../types';
import {makeFillError, makeJSONError, makeNameError} from './common';

const checkModelPath = modelPath<CheckModel>('', true);

export const makeCheckValidator = (model: StrictModel<CheckModel>) =>
    formValidator({
        modelPath: model,
        getValidationRules: () => ({}),
        getErrors: (
            {checkName, checkType, code}: Partial<CheckModel>,
            _state,
            {checkNameList}: {checkNameList?: string[]} = {},
        ) => {
            return {
                ...(checkType === CheckType.Combined
                    ? {
                          [checkModelPath(m => m.code)]: makeJSONError(code),
                      }
                    : {
                          [checkModelPath(m => m.code)]: makeFillError(code),
                      }),
                [checkModelPath(m => m.checkName)]: makeNameError(checkName, checkNameList),
            };
        },
    });
