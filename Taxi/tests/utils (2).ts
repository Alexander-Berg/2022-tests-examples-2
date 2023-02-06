import {head, partition, replace, split} from 'lodash';

import {DOT} from '../../../consts';
import {TestDataPart} from '../../../enums';
import {ExtendedTestErrorDescription, TestErrorDescription} from '../../../types';
import {ALL_TILL_FIRST_DOT, EMPTY_STRING} from './consts';

export const getTestErrorMaps = (errors: TestErrorDescription[]) => {
    return partition(errors, error => error.name.startsWith(TestDataPart.Input)).map(errorsGroup => {
        const withoutFirstObject = errorsGroup.map(error => ({
            ...error,
            errorKey: replace(error.name, ALL_TILL_FIRST_DOT, EMPTY_STRING),
        }));
        return withoutFirstObject.reduce<Record<string, ExtendedTestErrorDescription[]>>((acc, error) => {
            const key = head(split(error.errorKey, DOT));
            if (key) {
                acc[key] = acc[key] ?? [];
                acc[key].push({
                    ...error,
                    errorKey: replace(error.errorKey, ALL_TILL_FIRST_DOT, EMPTY_STRING),
                });
            }
            return acc;
        }, {});
    });
};
