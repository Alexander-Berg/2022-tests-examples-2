import {ColumnsToRows, columnsToRows} from 'service/utils/object/rows-columns/columns-to-rows';
import {RowsToColumns, rowsToColumns} from 'service/utils/object/rows-columns/rows-to-columns';

describe('array-object', () => {
    it('object-to-array', () => {
        const first = {a: [1, 2], b: [3, 4], c: [5, 6]};
        expect(columnsToRows(first)).toStrictEqual<ColumnsToRows<typeof first>>([
            {a: 1, b: 3, c: 5},
            {a: 2, b: 4, c: 6}
        ]);

        const second = {a: [1, 2], b: undefined, c: [4]};
        expect(columnsToRows(second)).toStrictEqual<ColumnsToRows<typeof second>>([
            {a: 1, b: undefined, c: 4},
            {a: 2, b: undefined, c: undefined}
        ]);

        const third = {a: undefined, b: undefined, c: undefined};
        expect(columnsToRows(third)).toStrictEqual<ColumnsToRows<typeof third>>([]);
    });

    it('array-to-object', () => {
        const first = [
            {a: 1, b: 3, c: 5},
            {a: 2, b: 4, c: 6}
        ];
        expect(rowsToColumns(first)).toStrictEqual<RowsToColumns<typeof first[number]>>({
            a: [1, 2],
            b: [3, 4],
            c: [5, 6]
        });

        const second = [
            {a: 1, b: undefined, c: 4},
            {a: 2, b: undefined, c: undefined}
        ];
        expect(rowsToColumns(second)).toStrictEqual({
            a: [1, 2],
            b: [undefined, undefined],
            c: [4, undefined]
        });

        const third = [{}, {}];
        expect(rowsToColumns(third)).toStrictEqual({});
    });
});
