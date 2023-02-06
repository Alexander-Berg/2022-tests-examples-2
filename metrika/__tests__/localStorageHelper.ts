import 'jest-localstorage-mock';
import { LocalStorageHelper } from '..';
import {
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
} from './fixtures/items';

const storageKey = 'testStorageKey';

beforeEach(() => {
    localStorage.clear();
    // @ts-ignore
    localStorage.setItem.mockClear();
    // @ts-ignore
    localStorage.getItem.mockClear();
    // @ts-ignore
    localStorage.removeItem.mockClear();
});

describe('Should set individual item to localStorage', () => {
    test('String item', () => {
        const helper = new LocalStorageHelper<typeof itemString>(
            itemStringValidationSchema,
            storageKey,
        );
        const [keyString, valueString] = Object.entries(itemString)[0] as [
            keyof typeof itemString,
            any,
        ];

        helper.setItem(keyString, valueString);

        const itemStorageKey = helper.getKey(keyString);
        const itemStorageValue = JSON.stringify(valueString);

        expect(localStorage.setItem).toHaveBeenLastCalledWith(
            itemStorageKey,
            itemStorageValue,
        );
        expect(localStorage.__STORE__[itemStorageKey]).toBe(itemStorageValue);
    });

    test('Number item', () => {
        const helper = new LocalStorageHelper<typeof itemNumber>(
            itemNumberValidationSchema,
            storageKey,
        );
        const [keyNumber, valueNumber] = Object.entries(itemNumber)[0] as [
            keyof typeof itemNumber,
            any,
        ];

        helper.setItem(keyNumber, valueNumber);

        const itemStorageKey = helper.getKey(keyNumber);
        const itemStorageValue = JSON.stringify(valueNumber);

        expect(localStorage.setItem).toHaveBeenLastCalledWith(
            itemStorageKey,
            itemStorageValue,
        );
        expect(localStorage.__STORE__[itemStorageKey]).toBe(itemStorageValue);
    });

    test('Boolean item', () => {
        const helper = new LocalStorageHelper<typeof itemBoolean>(
            itemBooleanValidationSchema,
            storageKey,
        );
        const [keyBoolean, valueBoolean] = Object.entries(itemBoolean)[0] as [
            keyof typeof itemBoolean,
            any,
        ];

        helper.setItem(keyBoolean, valueBoolean);

        const itemStorageKey = helper.getKey(keyBoolean);
        const itemStorageValue = JSON.stringify(valueBoolean);

        expect(localStorage.setItem).toHaveBeenLastCalledWith(
            itemStorageKey,
            itemStorageValue,
        );
        expect(localStorage.__STORE__[itemStorageKey]).toBe(itemStorageValue);
    });

    test('Object item', () => {
        const helper = new LocalStorageHelper<typeof itemObject>(
            itemObjectValidationSchema,
            storageKey,
        );
        const [keyObject, valueObject] = Object.entries(itemObject)[0] as [
            keyof typeof itemObject,
            any,
        ];

        helper.setItem(keyObject, valueObject);

        const itemStorageKey = helper.getKey(keyObject);
        const itemStorageValue = JSON.stringify(valueObject);

        expect(localStorage.setItem).toHaveBeenLastCalledWith(
            itemStorageKey,
            itemStorageValue,
        );
        expect(localStorage.__STORE__[itemStorageKey]).toBe(itemStorageValue);
    });

    test('Array item', () => {
        const helper = new LocalStorageHelper<typeof itemArray>(
            itemArrayValidationSchema,
            storageKey,
        );
        const [keyArray, valueArray] = Object.entries(itemArray)[0] as [
            keyof typeof itemArray,
            any,
        ];

        helper.setItem(keyArray, valueArray);

        const itemStorageKey = helper.getKey(keyArray);
        const itemStorageValue = JSON.stringify(valueArray);

        expect(localStorage.setItem).toHaveBeenLastCalledWith(
            itemStorageKey,
            itemStorageValue,
        );
        expect(localStorage.__STORE__[itemStorageKey]).toBe(itemStorageValue);
    });
});

test('Should set multiple items to localStorage', () => {
    const multipleItemsDict = {
        ...itemString,
        ...itemNumber,
        ...itemBoolean,
        ...itemObject,
        ...itemArray,
    };
    const multipleItemsDictValidationSchema = {
        ...itemStringValidationSchema,
        ...itemNumberValidationSchema,
        ...itemBooleanValidationSchema,
        ...itemObjectValidationSchema,
        ...itemArrayValidationSchema,
    };
    const helper = new LocalStorageHelper<typeof multipleItemsDict>(
        multipleItemsDictValidationSchema,
        storageKey,
    );

    helper.setItems(multipleItemsDict);

    expect(localStorage.setItem).toHaveBeenCalledTimes(5);

    Object.entries(multipleItemsDict).forEach(([key, value], nthTime) => {
        const itemStorageKey = helper.getKey(
            key as keyof typeof multipleItemsDict,
        );
        const itemStorageValue = JSON.stringify(value);

        expect(localStorage.setItem).toHaveBeenNthCalledWith(
            nthTime + 1,
            itemStorageKey,
            itemStorageValue,
        );
        expect(localStorage.__STORE__[itemStorageKey]).toBe(itemStorageValue);
    });
});

test('Should not set invalid item to localStorage', () => {
    const helper = new LocalStorageHelper<typeof itemString>(
        itemStringValidationSchema,
        storageKey,
    );
    const [keyString] = Object.entries(itemString)[0] as [
        keyof typeof itemString,
        any,
    ];
    const ivalidValueSting = 1;

    // @ts-ignore
    helper.setItem(keyString, ivalidValueSting);

    const itemStorageKey = helper.getKey(keyString);

    expect(localStorage.setItem).not.toHaveBeenCalled();
    expect(localStorage.__STORE__[itemStorageKey]).toBeUndefined();
});

describe('Should get individual item from localStorage', () => {
    test('String item', () => {
        const helper = new LocalStorageHelper<typeof itemString>(
            itemStringValidationSchema,
            storageKey,
        );
        const [keyString, valueString] = Object.entries(itemString)[0] as [
            keyof typeof itemString,
            any,
        ];

        helper.setItem(keyString, valueString);

        const itemStorageKey = helper.getKey(keyString);
        const recievedValue = helper.getItem(keyString);

        expect(localStorage.getItem).toHaveBeenLastCalledWith(itemStorageKey);
        expect(recievedValue).toEqual(valueString);
    });

    test('Number item', () => {
        const helper = new LocalStorageHelper<typeof itemNumber>(
            itemNumberValidationSchema,
            storageKey,
        );
        const [keyNumber, valueNumber] = Object.entries(itemNumber)[0] as [
            keyof typeof itemNumber,
            any,
        ];

        helper.setItem(keyNumber, valueNumber);

        const itemStorageKey = helper.getKey(keyNumber);
        const recievedValue = helper.getItem(keyNumber);

        expect(localStorage.getItem).toHaveBeenLastCalledWith(itemStorageKey);
        expect(recievedValue).toEqual(valueNumber);
    });

    test('Boolean item', () => {
        const helper = new LocalStorageHelper<typeof itemBoolean>(
            itemBooleanValidationSchema,
            storageKey,
        );
        const [keyBoolean, valueBoolean] = Object.entries(itemBoolean)[0] as [
            keyof typeof itemBoolean,
            any,
        ];

        helper.setItem(keyBoolean, valueBoolean);

        const itemStorageKey = helper.getKey(keyBoolean);
        const recievedValue = helper.getItem(keyBoolean);

        expect(localStorage.getItem).toHaveBeenLastCalledWith(itemStorageKey);
        expect(recievedValue).toEqual(valueBoolean);
    });

    test('Object item', () => {
        const helper = new LocalStorageHelper<typeof itemObject>(
            itemObjectValidationSchema,
            storageKey,
        );
        const [keyObject, valueObject] = Object.entries(itemObject)[0] as [
            keyof typeof itemObject,
            any,
        ];

        helper.setItem(keyObject, valueObject);

        const itemStorageKey = helper.getKey(keyObject);
        const recievedValue = helper.getItem(keyObject);

        expect(localStorage.getItem).toHaveBeenLastCalledWith(itemStorageKey);
        expect(recievedValue).toEqual(valueObject);
    });

    test('Array item', () => {
        const helper = new LocalStorageHelper<typeof itemArray>(
            itemArrayValidationSchema,
            storageKey,
        );
        const [keyArray, valueArray] = Object.entries(itemArray)[0] as [
            keyof typeof itemArray,
            any,
        ];

        helper.setItem(keyArray, valueArray);

        const itemStorageKey = helper.getKey(keyArray);
        const recievedValue = helper.getItem(keyArray);

        expect(localStorage.getItem).toHaveBeenLastCalledWith(itemStorageKey);
        expect(recievedValue).toEqual(valueArray);
    });
});

test('Should get multiple items from localStorage', () => {
    const multipleItemsDict = {
        ...itemString,
        ...itemNumber,
        ...itemBoolean,
        ...itemObject,
        ...itemArray,
    };
    const multipleItemsDictValidationSchema = {
        ...itemStringValidationSchema,
        ...itemNumberValidationSchema,
        ...itemBooleanValidationSchema,
        ...itemObjectValidationSchema,
        ...itemArrayValidationSchema,
    };
    const helper = new LocalStorageHelper<typeof multipleItemsDict>(
        multipleItemsDictValidationSchema,
        storageKey,
    );

    helper.setItems(multipleItemsDict);

    const recievedValues = helper.getItems(
        Object.keys(multipleItemsDict) as Array<keyof typeof multipleItemsDict>,
    );

    Object.entries(multipleItemsDict).forEach(
        ([key, value]: [keyof typeof multipleItemsDict, any], nthTime) => {
            const itemStorageKey = helper.getKey(key);

            expect(localStorage.getItem).toHaveBeenNthCalledWith(
                nthTime + 1,
                itemStorageKey,
            );
            expect(recievedValues[key]).toEqual(value);
        },
    );
});

test('Should return only valid items from localStorage and remove invalid items from localStorages', () => {
    const [keyString] = Object.entries(itemString)[0] as [
        keyof typeof itemString,
        any,
    ];
    const ivalidValueSting = 1;

    const multipleItemsDict = {
        ...{ [keyString]: ivalidValueSting },
        ...itemNumber,
    };
    const multipleItemsDictValidationSchema = {
        ...itemStringValidationSchema,
        ...itemNumberValidationSchema,
    };
    const helper = new LocalStorageHelper<typeof multipleItemsDict>(
        // @ts-ignore
        multipleItemsDictValidationSchema,
        storageKey,
    );

    Object.entries(multipleItemsDict).forEach(([key, value]) => {
        const itemStorageKey = helper.getKey(
            key as keyof typeof multipleItemsDict,
        );
        localStorage.setItem(itemStorageKey, JSON.stringify(value));
    });

    const recievedValues = helper.getItems(
        Object.keys(multipleItemsDict) as Array<keyof typeof multipleItemsDict>,
    );

    expect(localStorage.getItem).toHaveBeenCalledTimes(2);
    expect(localStorage.removeItem).toHaveBeenCalledTimes(1);

    const itemStringStorageKey = helper.getKey(keyString);
    expect(localStorage.removeItem).toHaveBeenLastCalledWith(
        itemStringStorageKey,
    );

    expect(recievedValues).toEqual({
        ...multipleItemsDict,
        [keyString]: undefined,
    });
});

test('Should remove indiviluad item from localStorage', () => {
    const helper = new LocalStorageHelper<typeof itemString>(
        itemStringValidationSchema,
        storageKey,
    );
    const [keyString, valueString] = Object.entries(itemString)[0] as [
        keyof typeof itemString,
        any,
    ];

    helper.setItem(keyString, valueString);

    const itemStorageKey = helper.getKey(keyString);
    helper.removeItem(keyString);

    expect(localStorage.removeItem).toHaveBeenLastCalledWith(itemStorageKey);
    expect(localStorage.__STORE__[itemStorageKey]).toBeUndefined();
});

test('Should remove multiple items from localStorage', () => {
    const multipleItemsDict = {
        ...itemString,
        ...itemNumber,
        ...itemBoolean,
        ...itemObject,
        ...itemArray,
    };
    const multipleItemsDictValidationSchema = {
        ...itemStringValidationSchema,
        ...itemNumberValidationSchema,
        ...itemBooleanValidationSchema,
        ...itemObjectValidationSchema,
        ...itemArrayValidationSchema,
    };
    const helper = new LocalStorageHelper<typeof multipleItemsDict>(
        multipleItemsDictValidationSchema,
        storageKey,
    );

    helper.setItems(multipleItemsDict);
    helper.removeItems(
        Object.keys(multipleItemsDict) as Array<keyof typeof multipleItemsDict>,
    );

    Object.entries(multipleItemsDict).forEach(([key], nthTime) => {
        const itemStorageKey = helper.getKey(
            key as keyof typeof multipleItemsDict,
        );

        expect(localStorage.removeItem).toHaveBeenNthCalledWith(
            nthTime + 1,
            itemStorageKey,
        );
        expect(localStorage.__STORE__[itemStorageKey]).toBeUndefined();
    });
});

test("Should remove item from localStorage if it's value coundn't be parsed via JSON.parse", () => {
    const helper = new LocalStorageHelper<typeof itemString>({}, storageKey);
    const [keyString] = Object.entries(itemString)[0] as [
        keyof typeof itemString,
        any,
    ];
    const invalidValue = '{ invalidValue: , }';
    const itemStorageKey = helper.getKey(keyString);

    localStorage.setItem(itemStorageKey, invalidValue);
    const recievedValue = helper.getItem(keyString);

    expect(localStorage.getItem).toHaveBeenCalledTimes(1);
    expect(localStorage.removeItem).toHaveBeenCalledTimes(1);
    expect(localStorage.removeItem).toHaveBeenLastCalledWith(itemStorageKey);
    expect(recievedValue).toBeUndefined();
});
