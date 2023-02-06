import {
    createColumnValueFromRecognizedString,
    createSumValueFromRecognizedString
} from 'server/recognition/column-value';
import {COLUMNS} from 'server/recognition/config';
import type {ColumnKeyType} from 'server/recognition/types/columns';
import type {Item, TotalSum, TotalSumFieldName} from 'server/recognition/types/types';
import {mapObject, mapObjectStrict} from 'service/utils/object/map-object/map-object';
import {uncapitalizeObject} from 'service/utils/object/object-keys-transformations/uncapitalize-object';
import {requireProperties} from 'service/utils/object/require-properties/require-properties';

export function convertStringItemToValueItem(item: {[key in keyof Item]?: string | undefined}): Item {
    const requiredItem: {[key in keyof Item]: string | undefined} = requireProperties(item, COLUMNS);

    return uncapitalizeObject(
        mapObjectStrict<typeof requiredItem, Item>(
            requiredItem,
            <ColumnName extends ColumnKeyType>(value: string, key: ColumnName) =>
                createColumnValueFromRecognizedString(key, value)
        )
    );
}

export function convertStringSumsToValueSums(sum: {[key in TotalSumFieldName]?: string}): TotalSum {
    return mapObject(sum, (value, key) => createSumValueFromRecognizedString(key, value)) as TotalSum;
}
