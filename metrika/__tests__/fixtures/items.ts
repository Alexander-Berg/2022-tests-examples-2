import { isString, isNumber, isBoolean, isPlainObject, isArray } from 'lodash';
import { ValidationSchema } from '../..';

const itemString = {
    keyString: 'valueString',
};

const itemStringValidationSchema: ValidationSchema<typeof itemString> = {
    keyString: (value: any): value is string => isString(value),
};

const itemNumber = {
    keyNumber: 2,
};

const itemNumberValidationSchema: ValidationSchema<typeof itemNumber> = {
    keyNumber: (value: any): value is number => isNumber(value),
};

const itemBoolean = {
    keyBoolean: true,
};

const itemBooleanValidationSchema: ValidationSchema<typeof itemBoolean> = {
    keyBoolean: (value: any): value is boolean => isBoolean(value),
};

const itemObject: { keyObject: object } = {
    keyObject: {
        test: true,
        array: ['string', 2, { test: true }],
    },
};

const itemObjectValidationSchema: ValidationSchema<typeof itemObject> = {
    keyObject: (value: any): value is object => isPlainObject(value),
};

const itemArray = {
    keyArray: ['string', 2, { test: true }],
};

const itemArrayValidationSchema: ValidationSchema<typeof itemArray> = {
    keyArray: (value: any): value is any[] => isArray(value),
};

export {
    itemString,
    itemStringValidationSchema,
    itemNumber,
    itemNumberValidationSchema,
    itemBoolean,
    itemBooleanValidationSchema,
    itemObject,
    itemObjectValidationSchema,
    itemArray,
    itemArrayValidationSchema,
};
