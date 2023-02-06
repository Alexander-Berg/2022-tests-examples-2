import {convertStringItemToValueItem, convertStringSumsToValueSums} from 'tests/unit/test-factory';

import {fixSumColumns} from '@/src/entities/erp-recognition-results/api/create-erp-recognition-results';
import type {CorrectDocument} from 'server/recognition/types/types';
import {DocumentType} from 'types/documents';

describe('calculate empty sum cells', () => {
    it('just works', () => {
        const document: CorrectDocument = {
            type: DocumentType.PackingList,
            pages: [
                {
                    items: [
                        {
                            sum: '425.76',
                            sumWithVat: '468.34',
                            vatSum: '42.58'
                        },
                        {
                            sum: '294.24',
                            sumWithVat: '323.66',
                            vatSum: '29.42'
                        },
                        {
                            sum: '601.92',
                            sumWithVat: '662.11',
                            vatSum: '60.19'
                        },
                        {
                            sum: '549.9',
                            sumWithVat: '604.89',
                            vatSum: '54.99'
                        },
                        {
                            sum: '169.14',
                            sumWithVat: '202.97',
                            vatSum: '33.83'
                        },
                        {
                            sum: '2012.4',
                            sumWithVat: '2213.64',
                            vatSum: ''
                        },
                        {
                            sum: '426.24',
                            sumWithVat: '468.86',
                            vatSum: '42.62'
                        },
                        {
                            sum: '549.9',
                            sumWithVat: '604.89',
                            vatSum: '54.99'
                        }
                    ].map(convertStringItemToValueItem),
                    pageTotal: convertStringSumsToValueSums({
                        sum: '5029.5',
                        sumWithVat: '5549.36',
                        vatSum: '519.86'
                    }),
                    rawTable: []
                },
                {
                    items: [
                        {
                            sum: '470.16',
                            sumWithVat: '517.18',
                            vatSum: '47.02'
                        },
                        {
                            sum: '646.8',
                            sumWithVat: '711.48',
                            vatSum: '64.68'
                        },
                        {
                            sum: '425.76',
                            sumWithVat: '468.34',
                            vatSum: '42.58'
                        },
                        {
                            sum: '425.76',
                            sumWithVat: '468.34',
                            vatSum: '42.58'
                        }
                    ].map(convertStringItemToValueItem),
                    pageTotal: convertStringSumsToValueSums({
                        sum: '1968.48',
                        sumWithVat: '2165.34',
                        vatSum: '196.86'
                    }),
                    rawTable: []
                }
            ],
            total: convertStringSumsToValueSums({
                sum: '6997.98',
                sumWithVat: '7714.7',
                vatSum: '716.72'
            })
        } as CorrectDocument;

        const fixedDocument = fixSumColumns(document);

        expect(fixedDocument.pages[0].items[5].vatSum?.toFormattedString()).toBe('201.24');
    });
});
