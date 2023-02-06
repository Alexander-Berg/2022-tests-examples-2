import uuid from 'uuid';

import {jsonParse} from '_utils/parser';
import {prettyJSONStringify} from '_utils/prettyJSONStringify';

import {CheckType} from '../enums';
import {Check, CheckModel, CombinedOutputCheck, ImperativeOutputCheck, OutputChecks, TestCheckModel} from '../types';

export const prepareCheckModel = ({name, check}: Omit<Check, 'id'>): CheckModel => {
    if ('source_code' in check) {
        return {
            checkName: name,
            checkType: CheckType.Imperative,
            ignoreAdditionalParams: false,
            code: check.source_code,
        };
    }

    return {
        checkName: name,
        checkType: CheckType.Combined,
        ignoreAdditionalParams: check.additional_properties,
        code: prettyJSONStringify(check.expected_output),
    };
};

const prepareOutputCheck = ({
    checkType,
    code,
    ignoreAdditionalParams,
}: Omit<CheckModel, 'checkName'>): CombinedOutputCheck | ImperativeOutputCheck => {
    return checkType === CheckType.Combined
        ? {
              expected_output: jsonParse(code),
              additional_properties: ignoreAdditionalParams,
          }
        : {
              source_code: code,
          };
};

export const prepareCheck = (model: CheckModel, id: string): Check => ({
    id,
    name: model.checkName,
    check: prepareOutputCheck(model),
});

export const prepareOutputChecks = (prefetchedMocks: Undefinable<OutputChecks>): TestCheckModel[] => {
    return Object.entries(prefetchedMocks ?? {}).map(([checkName, check]) => {
        return {
            ...prepareCheckModel({name: checkName, check}),
            _id: uuid.v4(),
        };
    });
};

export const prepareTestCheckModels = (checks: TestCheckModel[]): OutputChecks => {
    return checks.reduce<OutputChecks>((acc, {_id, checkName, ...check}) => {
        acc[checkName] = prepareOutputCheck(check);
        return acc;
    }, {});
};
