import fs from 'fs';

import {serviceResolve} from '@/src/lib/resolve';
import {matchTextToTable} from 'server/recognition/match-text';
import {mergeCells, recognizeMissingCells} from 'server/recognition/recognize-missing-cells';
import type {Rect, Row, TextRectPage, TextRow, Word} from 'server/recognition/types/types';

import {createTableFromTextRectPage} from './utils';

describe('table recognition', () => {
    it('should match text to cells correctly', async () => {
        const recognizedText = JSON.parse(
            fs.readFileSync(serviceResolve('./src/server/recognition/samples/text_recognition_1.json'), 'utf8')
        );
        const recognizedTable = JSON.parse(
            fs.readFileSync(serviceResolve('./src/server/recognition/samples/table_recognition_1.json'), 'utf8')
        );

        const expectedJSON = JSON.parse(
            fs.readFileSync(serviceResolve('./src/server/recognition/samples/1.json'), 'utf8')
        );

        const resultJSON = matchTextToTable({pagesTexts: recognizedText, pagesRects: recognizedTable}).map((page) =>
            page.map((row) => row.rects.map((rect) => rect['words'].map((word) => word.text)))
        );

        expect(resultJSON).toStrictEqual(expectedJSON);
    });
});

describe('should recognize missing table cells', () => {
    function runTest(testNumber: number, rowsNumber: number, columnsNumber: number) {
        const textRectPage: TextRectPage = JSON.parse(
            fs.readFileSync(
                serviceResolve(
                    './src/server/recognition/samples/recognize-missing-cells/' +
                        testNumber.toString() +
                        '/table-with-missing-cells.json'
                ),
                'utf8'
            )
        );

        const words: Word[] = JSON.parse(
            fs.readFileSync(
                serviceResolve(
                    './src/server/recognition/samples/recognize-missing-cells/' +
                        testNumber.toString() +
                        '/full-table-words.json'
                ),
                'utf8'
            )
        );

        const wordsMatchedTableCells: Word[][][] = JSON.parse(
            fs.readFileSync(
                serviceResolve(
                    './src/server/recognition/samples/recognize-missing-cells/' +
                        testNumber.toString() +
                        '/full-table.json'
                ),
                'utf8'
            )
        );

        const table = createTableFromTextRectPage(textRectPage);
        const fullTable = recognizeMissingCells(table, words, 0);

        expect(fullTable.getRows()).toHaveLength(rowsNumber);
        expect(fullTable.getColumns()).toHaveLength(columnsNumber);

        fullTable.getRows().forEach((row, rowIndex) => {
            row.forEach((column, columnIndex) => {
                expect(column.words).toHaveLength(wordsMatchedTableCells[rowIndex][columnIndex].length);

                column.words.forEach((word, wordIndex) => {
                    expect(word.text).toStrictEqual(wordsMatchedTableCells[rowIndex][columnIndex][wordIndex]);
                });
            });
        });
    }

    it('merged cells', () => {
        runTest(1, 7, 5);
    });

    it('missed cells', () => {
        runTest(2, 7, 5);
    });

    it('rotated image', () => {
        runTest(3, 7, 5);
    });
});

describe('should merge extra cells', () => {
    function runTest(testNumber: number, angle: number, rowsNumber: number, columnsNumber: number) {
        const textRectPage: TextRectPage = JSON.parse(
            fs.readFileSync(
                serviceResolve(
                    './src/server/recognition/samples/recognize-missing-cells/merge-cells/' +
                        testNumber.toString() +
                        '/table-with-extra-cells.json'
                ),
                'utf8'
            )
        ).map(
            (row: Row): TextRow => ({...row, rects: row.rects.map((rect: Rect) => ({...rect, text: '', words: []}))})
        );

        const mergedTable = mergeCells(createTableFromTextRectPage(textRectPage), angle);
        expect(mergedTable.getRows()).toHaveLength(rowsNumber);
        expect(mergedTable.getColumns()).toHaveLength(columnsNumber);
    }

    it('just work', () => {
        runTest(1, 0, 5, 5);
    });

    it('rotated table', () => {
        runTest(2, -0.052, 5, 5);
    });
});
