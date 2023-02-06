import fs from 'fs';

import {serviceResolve} from '@/src/lib/resolve';
import {findDocumentName} from 'server/recognition/recognize-document-name';
import {recognizeNumber} from 'server/recognition/recognize-number';
import type {Cell, TextRectPage, Word} from 'server/recognition/types/types';
import {calcStringsSimilarity, createTableFromTextRectPage, fixText, Table} from 'server/recognition/utils';
import type {CorrectDocumentType} from 'types/documents';
import {DocumentType} from 'types/documents';

describe('document name must be found correctly', () => {
    function runTest(testNumber: number, documentName: string, answer: {text: string; x: number; y: number}[]) {
        const words: Word[] = JSON.parse(
            fs.readFileSync(
                serviceResolve(
                    './src/server/recognition/samples/recognize-number/recognize-document-name/' +
                        testNumber.toString() +
                        '/words.json'
                ),
                'utf8'
            )
        );

        const documentNameBlock = findDocumentName(documentName, words);
        documentNameBlock.words.forEach((word, index) => {
            expect(fixText(word.text)).toBe(fixText(answer[index].text));
            expect(word.x).toBe(answer[index].x);
            expect(word.y).toBe(answer[index].y);
        });
    }

    const answers = [
        [
            {text: 'Название', x: 298, y: 65},
            {text: 'документа', x: 385, y: 65}
        ],
        [
            {text: 'Название', x: 309, y: 74},
            {text: 'документа', x: 407, y: 74}
        ],
        [
            {text: 'Низвиние', x: 309, y: 74},
            {text: 'документа', x: 407, y: 74}
        ]
    ];

    it('just working', () => {
        runTest(1, 'Название документа', answers[0]);
    });

    it('selection from several identical blocks', () => {
        runTest(2, 'Название документа', answers[1]);
    });

    it('selection from several identical blocks in case of a small error in the correct version', () => {
        runTest(3, 'Название документа', answers[2]);
    });
});

describe('document number must be found correctly', () => {
    function runTest(testNumber: number, documentType: CorrectDocumentType, answer: string) {
        const words: Word[] = JSON.parse(
            fs.readFileSync(
                serviceResolve(
                    './src/server/recognition/samples/recognize-number/' + testNumber.toString() + '/words.json'
                ),
                'utf8'
            )
        );

        const textRectPage: TextRectPage = JSON.parse(
            fs.readFileSync(
                serviceResolve(
                    './src/server/recognition/samples/recognize-number/' +
                        testNumber.toString() +
                        '/text-rect-page.json'
                ),
                'utf8'
            )
        );

        const documentNumber = recognizeNumber(
            {
                type: documentType,
                items: [],
                itemsTable: new Table<Cell>([]),
                headerTable: new Table<Cell>([]),
                table: createTableFromTextRectPage(textRectPage),
                words,
                angle: 0,
                ocrText: {blocks: []},
                keyColumnsIndexes: {},
                mainTableBoundaries: undefined
            },
            documentType
        );
        expect(documentNumber).toBeDefined();
        expect(calcStringsSimilarity(documentNumber.value ?? '', answer)).toBeGreaterThan(0.8);
    }

    const answers = ['№ВЛ000003998', '2480'];

    it('счет-фактура', () => {
        runTest(1, DocumentType.Invoice, answers[0]);
    });

    it('упд. счёт фактура', () => {
        runTest(2, DocumentType.UniversalTransferDocument, answers[1]);
    });
});
