import {isEmpty, isNotEmpty} from '_utils/strict/validators';

import {ERRORS, NAME_REGEXP} from '../../consts';

export const isValidName = (value: string) => isNotEmpty(value) && NAME_REGEXP.test(value);

export const makeNameError = (name?: string, nameList?: string[]) => {
    if (!name) {
        return ERRORS.FILL_FIELD;
    }
    if (!isValidName(name)) {
        return ERRORS.INVALID_NAME;
    }
    if (nameList?.some(n => n === name)) {
        return ERRORS.NAME_IS_OCCUPIED;
    }
    return '';
};

export const makeJSONError = (code?: string) => {
    if (!code) {
        return ERRORS.FILL_FIELD;
    }
    try {
        JSON.parse(code);
    } catch (e) {
        return ERRORS.INVALID_JSON;
    }
    return '';
};

export const makeFillError = (value?: string | unknown[], nameList?: string[]) => {
    if (isEmpty(value)) {
        return ERRORS.FILL_FIELD;
    }
    if (nameList?.some(n => n === value)) {
        return ERRORS.NAME_IS_OCCUPIED;
    }
    return '';
};
