import {describe, expect, it} from 'tests/jest.globals';
import xlsx from 'xlsx';

import {ImportSpreadsheetTooManyCells, ImportSpreadsheetTooManyRows} from '@/src/errors';
import {config} from 'service/cfg';
import {parse as parseSpreadsheet} from 'service/import/spreadsheet';

describe('spreadsheet parse', () => {
    let originalRowsLimit: number;
    let originalCellsLimit: number;

    function makeXlsxFromArray(array: string[][]) {
        const book = xlsx.utils.book_new();
        const sheet = xlsx.utils.aoa_to_sheet(array, {sheetStubs: true});
        xlsx.utils.book_append_sheet(book, sheet, 'Products');
        const buffer = xlsx.write(book, {type: 'buffer'});
        return new Uint8Array(buffer);
    }

    beforeEach(() => {
        originalRowsLimit = config.import.maxSpreadsheetRows;
        originalCellsLimit = config.import.maxSpreadsheetCells;

        config.import.maxSpreadsheetRows = 100;
        config.import.maxSpreadsheetCells = config.import.maxSpreadsheetRows * 10;
    });

    afterEach(() => {
        config.import.maxSpreadsheetRows = originalRowsLimit;
        config.import.maxSpreadsheetCells = originalCellsLimit;
    });

    it('should throw on exceeding rows limit', async () => {
        const headers = ['id', 'header_1'];
        const row = Array.from({length: headers.length}, () => '');
        const rows = Array.from({length: config.import.maxSpreadsheetRows + 1}, () => row);
        const data = makeXlsxFromArray([headers, ...rows]);
        await expect(parseSpreadsheet(data)).rejects.toThrow(ImportSpreadsheetTooManyRows);
    });

    it('should throw on exceeding cells limit', async () => {
        const maxCols = Math.ceil(config.import.maxSpreadsheetCells / config.import.maxSpreadsheetRows);
        const headers = ['id'].concat(Array.from({length: maxCols + 1}, (_, i) => `header_${i}`));
        const row = Array.from({length: headers.length}, () => '');
        const rows = Array.from({length: config.import.maxSpreadsheetRows + 1}, () => row);
        const data = makeXlsxFromArray([headers, ...rows]);
        await expect(parseSpreadsheet(data)).rejects.toThrow(ImportSpreadsheetTooManyCells);
    });

    it('should ignore headers and ID column', async () => {
        const maxCols = Math.ceil(config.import.maxSpreadsheetCells / config.import.maxSpreadsheetRows);
        const headers = ['id'].concat(Array.from({length: maxCols}, (_, i) => `header_${i}`));
        const row = Array.from({length: headers.length}, () => '');
        const rows = Array.from({length: config.import.maxSpreadsheetRows}, () => row);
        const data = makeXlsxFromArray([headers, ...rows]);

        expect(data.length).toBeGreaterThan(config.import.maxSpreadsheetRows);
        expect(headers.length * rows.length).toBeGreaterThan(config.import.maxSpreadsheetCells);

        await expect(parseSpreadsheet(data)).resolves.not.toThrow();
    });
});
