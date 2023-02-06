import fs from 'fs';
import {convertStringItemToValueItem} from 'tests/unit/test-factory';

import {serviceResolve} from '@/src/lib/resolve';
import {
    findDocumentConfigByType,
    findHeaderRowIndexes,
    recognizeDocuments
} from 'server/recognition/recognize-document';
import type {CorrectDocument, Document, Item, TextRectPage} from 'server/recognition/types/types';
import {checkIfStringsSimilar, Table} from 'server/recognition/utils';
import {mapIfNotUndefined} from 'service/utils/map-if-undefined';
import {mapObject} from 'service/utils/object/map-object/map-object';
import type {CorrectDocumentType} from 'types/documents';
import {DocumentType} from 'types/documents';

describe('header row should be correctly identified', () => {
    function runTest(testNumber: number, documentType: CorrectDocumentType, answer: any) {
        const tableWords: {words: {text: string}[]}[][] = JSON.parse(
            fs.readFileSync(
                serviceResolve(
                    './src/server/recognition/samples/document-parsing/header-parsing/' +
                        testNumber.toString() +
                        '/table-words.json'
                ),
                'utf8'
            )
        );

        const documentTable = new Table(tableWords);

        const headerRowIndexes = findHeaderRowIndexes(findDocumentConfigByType(documentType), documentTable);
        const headerRowIndex = headerRowIndexes?.[0];

        expect(headerRowIndex).toBe(answer);
    }

    const answers = [6, undefined];

    it('real data test', () => {
        runTest(3, DocumentType.Invoice, answers[0]);
    });

    it('table without header', () => {
        runTest(4, DocumentType.Invoice, answers[1]);
    });
});

describe('at least half items should be recognized correctly', () => {
    type Answer = {
        keys: Array<keyof Item>;
        items: Item[];
    };

    function runTest(
        testNumber: number,
        documentType: CorrectDocumentType,
        keysToCheck: Array<keyof Item>,
        answer: Answer
    ) {
        const tableData: TextRectPage = JSON.parse(
            fs.readFileSync(
                serviceResolve(
                    `./src/server/recognition/samples/document-parsing/items-and-keys/${testNumber}/page.json`
                ),
                'utf8'
            )
        );

        const {json: document} = recognizeDocuments({
            textRectPages: [tableData],
            textRecognizedPages: [],
            documentType,
            auxiliaryData: {}
        }) as {json: CorrectDocument};

        expect(document).toBeDefined();
        expect(document.type).toBe(documentType);
        expect(document.pages).toHaveLength(1);
        expect(document.pages[0].items.length).toBeGreaterThan(0);

        answer.keys.map((key) => expect(key in document.pages[0].items[0]).toBeTruthy());

        let similarStringsNumber = 0;
        document.pages[0].items.map((parsedItem, itemIndex) => {
            keysToCheck.forEach((key) => {
                if (
                    checkIfStringsSimilar(
                        parsedItem[key]?.toFormattedString() ?? '',
                        answer.items[itemIndex]?.[key]?.toFormattedString() ?? ''
                    )
                ) {
                    ++similarStringsNumber;
                }
            });
        });

        expect(similarStringsNumber / (answer.items.length * keysToCheck.length)).toBeGreaterThanOrEqual(0.5);
    }

    it('Счёт-фактура', () => {
        const items: Item[] = [
            {
                title: 'Сэндвич К завтраку, (хот-дог, датский)130г_ГМС_B2B',
                price: '63,00'
            },
            {
                title: 'Сэндвич "С семгой",210г_ГМС_B2B',
                price: '96,49'
            },
            {
                title: 'Омлет с ветчиной и сыром,135г_ГМС_В2В_',
                price: '68,90'
            },
            {
                title: 'Мини-круассан с лососем, 90г_ГМС_В2В',
                price: '71,67'
            },
            {
                title: 'Запеканка творожная, 150г_ГМС_В2В',
                price: '51,30'
            },
            {
                title: 'Хлеб "Мультизлаковый",400г_B2B_',
                price: '86,90'
            },
            {
                title: 'Суп"Куриный",250г_B2B_ГМС',
                price: '64,50'
            },
            {
                title: 'Свинина запеченная, (со спагетти)250г_ГМС_В2В',
                price: '99,35'
            },
            {
                title: 'Свинина запеченная, (с картофелем)250г_ГМС_B2B',
                price: '99,33'
            },
            {
                title: 'Сэндвич с курицей и жареными томатами,205г_B2B',
                price: '82,07'
            },
            {
                title: 'Изделия хлебобулочные из слоеного теста "Пан-о-Шоколя",40г_B2B_',
                price: '29,00'
            },
            {
                title: 'Чизбургер, 250г_ГМС_В2В',
                price: '106,57'
            }
        ].map(convertStringItemToValueItem);

        const keys: Array<keyof Item> = [
            'price',
            'vat',
            'vatSum',
            'amount',
            'amountUnit',
            'code',
            'sum',
            'sumWithVat',
            'title'
        ];

        runTest(1, DocumentType.Invoice, ['title', 'price'], {items, keys});
    });

    it('Товарно-транспортная накладная', () => {
        const items: Item[] = [
            {
                title: 'Улитка с корицей 85 г',
                code: '43000006754',
                price: '35.46',
                amount: '2',
                amountUnit: 'шт',
                sumWithVat: '78'
            },
            {
                title: 'Датская слойка с персиком 55',
                code: '43000000384',
                price: '19.09',
                amount: '2',
                amountUnit: 'шт',
                sumWithVat: '42'
            },
            {
                title: 'Багет 270 г ОПТ',
                code: '43000009033',
                price: '26.37',
                amount: '2',
                amountUnit: 'шт',
                sumWithVat: '58'
            },
            {
                title: 'Круассан 65 г',
                code: '43000000878',
                price: '14.55',
                amount: '4',
                amountUnit: 'шт',
                sumWithVat: '64'
            },
            {
                title: 'Слойка с курой и соусом 105 г',
                code: '43000006080',
                price: '34.55',
                amount: '2',
                amountUnit: 'шт',
                sumWithVat: '76'
            },
            {
                title: 'Пирожное Наполеон 140 г (упак)',
                code: '43000009557',
                price: '68.33',
                amount: '3',
                amountUnit: 'шт',
                sumWithVat: '246'
            },
            {
                title: 'Кекс Шоколадный 60 г',
                code: '43000007328',
                price: '28.33',
                amount: '1',
                amountUnit: 'шт',
                sumWithVat: '34'
            },
            {
                title: 'Датская слойка с малиной (ягоды) 55 г',
                code: '43000000354',
                price: '19.09',
                amount: '2',
                amountUnit: 'шт',
                sumWithVat: '42'
            },
            {
                title: 'Круассан с миндальным кремом 135 г ОПТ',
                code: '43000008997',
                price: '65.45',
                amount: '3',
                amountUnit: 'шт',
                sumWithVat: '216'
            },
            {
                title: 'Хлеб Чиабатта 320 г',
                code: '43000002621',
                price: '48.18',
                amount: '2',
                amountUnit: 'шт',
                sumWithVat: '106'
            },
            {
                title: 'Пирожное Медовое 120 г (упак)',
                code: '43000009556',
                price: '60',
                amount: '2',
                amountUnit: 'шт',
                sumWithVat: '144'
            },
            {
                title: 'Пирожное брауни с вишней 0,075 кг БП',
                code: '43000010068',
                price: '58.34',
                amount: '2',
                amountUnit: 'шт',
                sumWithVat: '140'
            }
        ].map(convertStringItemToValueItem);

        const keys: Array<keyof Item> = ['price', 'amount', 'amountUnit', 'code', 'sumWithVat', 'title'];

        runTest(2, DocumentType.ConsignmentNote, keys, {items, keys});
    });
});

describe('Total prices parsing testes', () => {
    it('keywords inside the table', () => {
        const rectsAndOcrData = JSON.parse(
            fs.readFileSync(
                serviceResolve(
                    './src/server/recognition/samples/document-parsing/total-price-parsing/keywords-inside-table.json'
                ),
                'utf8'
            )
        );

        const recognized = recognizeDocuments({
            ...rectsAndOcrData,
            documentType: DocumentType.Invoice,
            auxiliaryData: {}
        });
        const document = recognized.json as Document & {type: DocumentType.Invoice};

        expect(
            mapIfNotUndefined(document.pages[0].pageTotal, (total) =>
                mapObject(total, (sum) => sum.toFormattedString())
            )
        ).toMatchObject({
            vatSum: '319.62',
            sumWithVat: '2291.85',
            sum: '1972.23'
        });
    });

    it('keywords outside the table', () => {
        const rectsAndOcrData = JSON.parse(
            fs.readFileSync(
                serviceResolve(
                    './src/server/recognition/samples/document-parsing/total-price-parsing/keywords-outside-table.json'
                ),
                'utf8'
            )
        );

        const recognized = recognizeDocuments({
            ...rectsAndOcrData,
            documentType: DocumentType.PackingList,
            auxiliaryData: {}
        });
        const document = recognized.json as Document & {type: DocumentType.PackingList};

        expect(
            mapIfNotUndefined(document.pages[0].pageTotal, (total) =>
                mapObject(total, (sum) => sum.toFormattedString())
            )
        ).toMatchObject({
            vatSum: '548.75',
            sumWithVat: '4709.74',
            sum: '4160.99'
        });

        expect(
            mapIfNotUndefined(document.total, (total) => mapObject(total, (sum) => sum.toFormattedString()))
        ).toMatchObject({
            vatSum: '548.75',
            sumWithVat: '4709.74',
            sum: '4160.99'
        });
    });

    it('multipage PDF', () => {
        const rectsAndOcrData = JSON.parse(
            fs.readFileSync(
                serviceResolve('./src/server/recognition/samples/document-parsing/total-price-parsing/multipage.json'),
                'utf8'
            )
        );

        const recognized = recognizeDocuments({
            ...rectsAndOcrData,
            documentType: DocumentType.Invoice,
            auxiliaryData: {}
        });
        const document = recognized.json as Document & {type: DocumentType.Invoice};

        expect(
            mapIfNotUndefined(document.pages[0].pageTotal, (total) =>
                mapObject(total, (sum) => sum.toFormattedString())
            )
        ).toMatchObject({
            vatSum: '229.13',
            sum: '2188.76',
            sumWithVat: '2417.89'
        });

        expect(
            mapIfNotUndefined(document.pages[1].pageTotal, (total) =>
                mapObject(total, (sum) => sum.toFormattedString())
            )
        ).toMatchObject({
            sum: '1972.23',
            sumWithVat: '2291.85'
        });

        expect(
            mapIfNotUndefined(document.total, (total) => mapObject(total, (sum) => sum.toFormattedString()))
        ).toMatchObject({
            sumWithVat: '4709.74',
            sum: '4160.99'
        });
    });

    it('next page contains only row with total', () => {
        const rectsAndOcrData = JSON.parse(
            fs.readFileSync(
                serviceResolve(
                    './src/server/recognition/samples/document-parsing/total-price-parsing/total-on-other-page.json'
                ),
                'utf8'
            )
        );

        const recognized = recognizeDocuments({
            ...rectsAndOcrData,
            documentType: DocumentType.Invoice,
            auxiliaryData: {}
        });
        const document = recognized.json as Document & {type: DocumentType.Invoice};

        expect(document.pages[0].pageTotal).toBe(undefined);

        expect(document.pages[1].pageTotal).toBe(undefined);

        expect(
            mapIfNotUndefined(document.total, (total) => mapObject(total, (sum) => sum.toFormattedString()))
        ).toMatchObject({
            vatSum: '230.00',
            sumWithVat: '1380.00'
        });
    });
});

describe('Double headers', () => {
    it('double headers on single page', () => {
        const rectsAndOcrData = JSON.parse(
            fs.readFileSync(
                serviceResolve('./src/server/recognition/samples/document-parsing/double-headers/single-page.json'),
                'utf8'
            )
        );

        const {json: document} = recognizeDocuments({
            ...rectsAndOcrData,
            documentType: DocumentType.UniversalTransferDocument,
            auxiliaryData: {}
        }) as {json: Document & {type: DocumentType.UniversalTransferDocument}};
        const itemsTitles = document.pages[0].items.map((item) => item.title?.toFormattedString());

        expect(document.pages[0].items).toHaveLength(6);
        expect(itemsTitles).toMatchObject([
            'Ролл Филадельфия Кунсей.',
            'Ролл Калифорния.',
            'Суп Том ям.',
            'Ролл Эби Спайс',
            'Ролл Кунсей Бонито.',
            'Ролл Тори Цезарь'
        ]);

        expect(document.pages[0].pageTotal).toBe(undefined);

        expect(
            mapIfNotUndefined(document.total, (total) => mapObject(total, (sum) => sum.toFormattedString()))
        ).toMatchObject({
            vatSum: '230.00',
            sumWithVat: '1380.00'
        });
    });

    it.skip('one item on other page', () => {
        const rectsAndOcrData = JSON.parse(
            fs.readFileSync(
                serviceResolve(
                    './src/server/recognition/samples/document-parsing/double-headers/one-item-on-other-page.json'
                ),
                'utf8'
            )
        );

        const {json: document} = recognizeDocuments({
            ...rectsAndOcrData,
            documentType: DocumentType.UniversalTransferDocument
        }) as {json: Document & {type: DocumentType.UniversalTransferDocument}};

        const itemsTitlesPage1 = document.pages[0].items.map((item) => item.title);
        const itemsTitlesPage2 = document.pages[1].items.map((item) => item.title);

        expect(document.pages[0].items).toHaveLength(6);
        expect(itemsTitlesPage1).toMatchObject([
            'Вок Рамен с креветками в соево- чесночном соусе',
            'Суп Том ям.',
            'Ролл Калифорния.',
            'Ролл Тори Цезарь',
            'Ролл Кунсей Бонито.',
            'Ролл Эби Спайс'
        ]);

        expect(document.pages[1].items).toHaveLength(1);
        expect(itemsTitlesPage2).toMatchObject(['Ролл Филадельфия Кунсей.']);

        expect(document.pages[0].pageTotal).toMatchObject({});
        expect(document.pages[1].pageTotal).toMatchObject({});

        expect(document.total).toMatchObject({
            sumWithVat: '2655.00'
        });
    });
});
