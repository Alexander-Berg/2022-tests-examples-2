import {convertStringItemToValueItem} from 'tests/unit/test-factory';

import type {Documents} from '@/src/entities/documents/entity';
import {convertErpItemToSupplyItem} from '@/src/entities/erp-recognition-results/api/convert-erp-item-to-supply-item';
import {convertRecognitionResultItemToSupplyItem} from '@/src/entities/erp-recognition-results/api/convert-recognition-result-item-to-supply-item';
import {
    calcErpRecognitionItemSimilarity,
    ITEMS_SIMILARITY_THRESHOLD,
    matchRecognitionResultItemsWithErpItems
} from '@/src/entities/erp-recognition-results/api/create-erp-recognition-results';
import {serializeDocument} from '@/src/entities/recognition-results/api/serialize-result';
import type {RecognitionResults} from '@/src/entities/recognition-results/entity';
import type {CorrectDocument} from 'server/recognition/types/types';
import {DocumentType} from 'types/documents';
import type {ErpSupply} from 'types/erp';
import type {ErpRecognitionItem} from 'types/erp-recognition-results';
import {RecognitionResultStatus} from 'types/recognition-results';
import type {SupplyItem} from 'types/supply';

import {ItemPair, matchArrays} from './match-arrays';

describe('items should correctly matched', () => {
    function runTest(
        firstArray: SupplyItem[],
        secondArray: SupplyItem[],
        answer: ([number | undefined, number] | [number, number | undefined])[]
    ) {
        const matchedPairs = matchArrays(
            firstArray,
            secondArray,
            calcErpRecognitionItemSimilarity,
            ITEMS_SIMILARITY_THRESHOLD
        );

        for (const pair of matchedPairs) {
            expect(answer).toContainEqual(pair);
        }

        for (const pair of answer) {
            expect(matchedPairs).toContainEqual(pair);
        }
    }

    it('just working', () => {
        const firstArray: SupplyItem[] = [
            {
                name: 'Наименование',
                price: '123',
                vat: '20',
                vatSum: '23',
                sum: '246',
                quantity: '2',
                totalSum: '300',
                code: '12312421',
                units: ''
            }
        ];
        const secondArray: SupplyItem[] = [
            {
                name: 'Наименование',
                price: '123',
                vat: '20',
                vatSum: '23',
                sum: '246',
                quantity: '2',
                totalSum: '300',
                code: '344362325',
                units: ''
            }
        ];
        runTest(firstArray, secondArray, [[0, 0]]);
    });

    it('all items have a perfect pair', () => {
        const firstArray: SupplyItem[] = [
            {
                name: 'Кефир 3,6-4,6% ПЭТ 1000 г',
                quantity: '6',
                price: '98.09',
                sum: '588.55',
                vat: '10',
                totalSum: '647.40',
                vatSum: '58',
                code: 'akjndksajd',
                units: ''
            },
            {
                name: 'Молоко питьевое 3,6-4,6%, ПЭТ, 1л',
                quantity: '6',
                price: '95.41',
                sum: '572.45',
                vat: '10',
                totalSum: '629.70',
                vatSum: '57',
                code: 'lhsakdhasd',
                units: ''
            },
            {
                name: 'Сметана 20% стакан 200 г',
                quantity: '6',
                price: '70.64',
                sum: '423.82',
                vat: '10',
                totalSum: '466.20',
                vatSum: '42',
                code: 'hsjkdsdf',
                units: ''
            },
            {
                name: 'Творог 2%, стакан 200 г (4 ШТ)',
                quantity: '4',
                price: '81.82',
                sum: '327.27',
                vat: '10',
                totalSum: '360',
                vatSum: '32',
                code: 'vcusfsjd',
                units: ''
            },
            {
                name: 'Творог 9%, стакан 200 г (4 ШТ)',
                quantity: '4',
                price: '85.73',
                sum: '342.91',
                vat: '10',
                totalSum: '377.20',
                vatSum: '34',
                code: 'uydsgfusgfus',
                units: ''
            },
            {
                name: 'Сливки безлактозные м.д.ж.10% 0,33 кг',
                quantity: '6',
                price: '95.82',
                sum: '574.91',
                vat: '10',
                totalSum: '632.40',
                vatSum: '57',
                code: 'ucxyvudrvyu',
                units: ''
            }
        ];
        const secondArray: SupplyItem[] = [
            firstArray[2],
            firstArray[5],
            firstArray[0],
            firstArray[3],
            firstArray[1],
            firstArray[4]
        ];
        runTest(firstArray, secondArray, [
            [2, 0],
            [5, 1],
            [0, 2],
            [3, 3],
            [1, 4],
            [4, 5]
        ]);
    });

    it('all items have an imperfect pair', () => {
        const firstArray: SupplyItem[] = [
            {
                name: 'Кефир ПЭТ 1000 г',
                quantity: '6',
                price: '98.09',
                sum: '',
                vat: '10',
                totalSum: '647.40',
                vatSum: '58',
                code: 'htnhntngfbfbg',
                units: ''
            },
            {
                name: 'Молоко питьевое 3,6-4,6%, ПЭТ, 1л',
                quantity: '6',
                price: '95.41',
                sum: '572.45',
                vat: '10',
                totalSum: '629.70',
                vatSum: '57',
                code: 'fgbgfbbfdbbb',
                units: ''
            },
            {
                name: 'Сметана 20% стакан 200 г',
                quantity: '',
                price: '',
                sum: '',
                vat: '',
                totalSum: '',
                vatSum: '',
                code: 'xffdssdfdsfdsf',
                units: ''
            },
            {
                name: 'Творог 9%, стакан 200 г (4 ШТ)',
                quantity: '4',
                price: '81.82',
                sum: '327.27',
                vat: '10',
                totalSum: '360',
                vatSum: '32',
                code: 'sdfsddsfdsfbb',
                units: ''
            },
            {
                name: 'Творог 9%, стакан 200 г (4 ШТ)',
                quantity: '',
                price: '85.73',
                sum: '342.91',
                vat: '10',
                totalSum: '',
                vatSum: '34',
                code: 'bcxvbgfdfdfd',
                units: ''
            },
            {
                name: 'Сливки безлактозные м.д.ж.10% 0,33 кг',
                quantity: '6',
                price: '95.82',
                sum: '574.91',
                vat: '10',
                totalSum: '632.40',
                vatSum: '57',
                code: 'ubgfbdbddfdfdgrn',
                units: ''
            }
        ];

        const secondArray: SupplyItem[] = [
            {
                name: 'Кефир 3,6-4,6% ПЭТ 1000 г',
                quantity: '6',
                price: '98.09',
                sum: '588.55',
                vat: '10',
                totalSum: '647.40',
                vatSum: '58',
                code: 'akjndksajd',
                units: ''
            },
            {
                name: 'Молоко питьевое 3,6-4,6%, ПЭТ, 1л',
                quantity: '6',
                price: '95.41',
                sum: '572.45',
                vat: '10',
                totalSum: '629.70',
                vatSum: '57',
                code: 'lhsakdhasd',
                units: ''
            },
            {
                name: 'Сметана 20% стакан 200 г',
                quantity: '6',
                price: '70.64',
                sum: '423.82',
                vat: '10',
                totalSum: '466.20',
                vatSum: '42',
                code: 'hsjkdsdf',
                units: ''
            },
            {
                name: 'Творог 2%, стакан 200 г (4 ШТ)',
                quantity: '4',
                price: '81.82',
                sum: '327.27',
                vat: '10',
                totalSum: '360',
                vatSum: '32',
                code: 'vcusfsjd',
                units: ''
            },
            {
                name: 'Творог 9%, стакан 200 г (4 ШТ)',
                quantity: '4',
                price: '85.73',
                sum: '342.91',
                vat: '10',
                totalSum: '377.20',
                vatSum: '34',
                code: 'uydsgfusgfus',
                units: ''
            },
            {
                name: 'Сливки безлактозные м.д.ж.10% 0,33 кг',
                quantity: '6',
                price: '95.82',
                sum: '574.91',
                vat: '10',
                totalSum: '632.40',
                vatSum: '57',
                code: 'ucxyvudrvyu',
                units: ''
            }
        ];

        runTest(firstArray, secondArray, [
            [0, 0],
            [1, 1],
            [2, 2],
            [3, 3],
            [4, 4],
            [5, 5]
        ]);
    });

    it('some items dont have a pair', () => {
        const firstArray: SupplyItem[] = [
            {
                name: 'Кефир ПЭТ 1000 г',
                quantity: '6',
                price: '98.09',
                sum: '',
                vat: '10',
                totalSum: '647.40',
                vatSum: '58',
                code: 'xcvcxvxvcvcx',
                units: ''
            },
            {
                name: 'Молоко питьевое 3,6-4,6%, ПЭТ, 1л',
                quantity: '6',
                price: '95.41',
                sum: '572.45',
                vat: '10',
                totalSum: '629.70',
                vatSum: '57',
                code: 'tytfgfg',
                units: ''
            },
            {
                name: 'Сметана 20% стакан 200 г',
                quantity: '',
                price: '',
                sum: '',
                vat: '',
                totalSum: '',
                vatSum: '',
                code: 'sgbsdgbvxdsf',
                units: ''
            },
            {
                name: 'Творог 9%, стакан 200 г (4 ШТ)',
                quantity: '4',
                price: '81.82',
                sum: '327.27',
                vat: '10',
                totalSum: '360',
                vatSum: '32',
                code: 'gfbxzvdsvcxbc',
                units: ''
            },
            {
                name: 'Творог 9%, стакан 200 г (4 ШТ)',
                quantity: '',
                price: '85.73',
                sum: '342.91',
                vat: '10',
                totalSum: '',
                vatSum: '34',
                code: 'gfbccxvbxcvbc',
                units: ''
            },
            {
                name: 'Сливки безлактозные м.д.ж.10% 0,33 кг',
                quantity: '6',
                price: '95.82',
                sum: '574.91',
                vat: '10',
                totalSum: '632.40',
                vatSum: '57',
                code: 'fbhgjutjtjtyjy',
                units: ''
            }
        ];

        const secondArray: SupplyItem[] = [
            {
                name: 'Кефир 3,6-4,6% ПЭТ 1000 г',
                quantity: '6',
                price: '98.09',
                sum: '588.55',
                vat: '10',
                totalSum: '647.40',
                vatSum: '58',
                code: 'akjndksajd',
                units: ''
            },
            {
                name: 'ФьЮЗ ЧАЙ ЛИМ-ГР ПТ 0. 5/12',
                quantity: '6',
                price: '478.71',
                sum: '478.71',
                vat: '20',
                totalSum: '574.45',
                vatSum: '47',
                code: 'idhufiuf',
                units: ''
            },
            {
                name: 'Сметана 20% стакан 200 г',
                quantity: '6',
                price: '70.64',
                sum: '423.82',
                vat: '10',
                totalSum: '466.20',
                vatSum: '42',
                code: 'hsjkdsdf',
                units: ''
            },
            {
                name: 'Творог 2%, стакан 200 г (4 ШТ)',
                quantity: '4',
                price: '81.82',
                sum: '327.27',
                vat: '10',
                totalSum: '360',
                vatSum: '65',
                code: 'vcusfsjd',
                units: ''
            },
            {
                name: 'КОКА-КОЛА 1.5/9 ПЭТ',
                quantity: '',
                price: '608.72',
                sum: '2434.88',
                vat: '20',
                totalSum: '2921.86',
                vatSum: '487',
                code: 'kdjshfsjf',
                units: ''
            },
            {
                name: 'Сливки безлактозные м.д.ж.10% 0,33 кг',
                quantity: '6',
                price: '95.82',
                sum: '574.91',
                vat: '10',
                totalSum: '632.40',
                vatSum: '57',
                code: 'ucxyvudrvyu',
                units: ''
            }
        ];

        runTest(firstArray, secondArray, [
            [0, 0],
            [1, undefined],
            [2, 2],
            [3, 3],
            [4, undefined],
            [5, 5],
            [undefined, 1],
            [undefined, 4]
        ]);
    });

    it('real data', () => {
        const firstArray: SupplyItem[] = [
            {
                id: '8868',
                sum: 387.05,
                vat: 10,
                name:
                    'Пюре «ФрутоНяня» из яблок, земляники и ежевики ' +
                    'с овсяным печеньем для питания детей раннего возраста',
                price: 35.48,
                wms_id: 'ac04bc0ac91e4d338cf913439f2fe47c000200010000',
                vat_sum: 38.71,
                quantity: 12,
                total_sum: 425.76,
                supplier_id: 43000255
            },
            {
                id: '4876',
                sum: 602.67,
                vat: 10,
                name: 'Детская вода «ФрутоНяня», c рождения, 1,5 л',
                price: 36.83,
                wms_id: 'b945d9fe4b2c4fb39f5097b030885082000200010000',
                vat_sum: 60.27,
                quantity: 18,
                total_sum: 662.94,
                supplier_id: 43000469
            },
            {
                id: '7369',
                sum: 427.42,
                vat: 10,
                name: 'Пюре «ФрутоНяня» из говядины с овощами, 100 г',
                price: 39.18,
                wms_id: '26d715652bd543d0a7d2ca6de86f1db7000100010001',
                vat_sum: 42.74,
                quantity: 12,
                total_sum: 470.16,
                supplier_id: 43000187
            },
            {
                id: '7084',
                sum: 387.05,
                vat: 10,
                name: 'Пюре «ФрутоНяня» витаминный салатик, 90 г',
                price: 35.48,
                wms_id: '5c7805198b564a6491d7de612fe6ed2b000200010000',
                vat_sum: 38.71,
                quantity: 12,
                total_sum: 425.76,
                supplier_id: 43000235
            },
            {
                id: '7788',
                sum: 588,
                vat: 10,
                name: 'Сок «ФрутоНяня» яблоко и персик с мякотью, 500 мл',
                price: 43.12,
                wms_id: 'e38df76b1807417e9316435f4333a7c7000200010000',
                vat_sum: 58.8,
                quantity: 15,
                total_sum: 646.8,
                supplier_id: 43000504
            },
            {
                id: '20900',
                sum: 267.49,
                vat: 10,
                name: 'Коктейль молочный «ФрутоНяня» клубнично-земляничный, 200 мл',
                price: 24.52,
                wms_id: '14b92212698b4a7092f746678643077d000300020002',
                vat_sum: 26.75,
                quantity: 12,
                total_sum: 294.24,
                supplier_id: 43000397
            },
            {
                id: '4873',
                sum: 427.09,
                vat: 10,
                name: 'Сок «ФрутоНяня» из яблок осветленный, c 4 месяцев, 200 мл',
                price: 26.1,
                wms_id: '8ad20f9dfd2449a0a578148248117b74000100010001',
                vat_sum: 42.71,
                quantity: 18,
                total_sum: 469.8,
                supplier_id: 43000482
            },
            {
                id: '4875',
                sum: 550.8,
                vat: 10,
                name: 'Каша "ФрутоНяня" молочная злаковая, с 6 месяцев, 200 мл',
                price: 33.66,
                wms_id: '4db0733d6f084a3eb052ec3a0d734c8d000200010001',
                vat_sum: 55.08,
                quantity: 18,
                total_sum: 605.88,
                supplier_id: 43000360
            },
            {
                id: '4874',
                sum: 550.8,
                vat: 10,
                name: 'Каша "ФрутоНяня" молочная 5 злаков с персиком, с 6 месяцев, 200 мл',
                price: 33.66,
                wms_id: 'e3302a66732d4fae86df6803d8f0d721000200010000',
                vat_sum: 55.08,
                quantity: 18,
                total_sum: 605.88,
                supplier_id: 43000364
            },
            {
                id: '4877',
                sum: 2013.38,
                vat: 10,
                name: 'Детская вода «ФрутоНяня», c рождения, 5 л',
                price: 92.28,
                wms_id: '4a42c0a0e0d24a76b2d653697b36de0a000200010001',
                vat_sum: 201.34,
                quantity: 24,
                total_sum: 2214.72,
                supplier_id: 43000470
            },
            {
                id: '7833',
                sum: 155.05,
                vat: 20,
                name: 'Вода «Липецкий Бювет» минеральная лечебно-столовая газированная, 1,5 л',
                price: 31.01,
                wms_id: 'e7cd7664be6e4a948c0fa85ebafb4200000200010001',
                vat_sum: 31.01,
                quantity: 6,
                total_sum: 186.06,
                supplier_id: 43000334
            },
            {
                id: '7352',
                sum: 387.05,
                vat: 10,
                name: 'Пюре фруктовое «ФрутоНяня» «Салатик из фруктов», 90 г',
                price: 35.48,
                wms_id: '9258834659fa4f469af66126d24bc1c9000200010000',
                vat_sum: 38.71,
                quantity: 12,
                total_sum: 425.76,
                supplier_id: 43000241
            }
        ].map(convertErpItemToSupplyItem);

        const secondArray: SupplyItem[] = [
            {
                title: 'Пюре ФрутоНяня яблоко, шиповник, клюква - витаминный салатик, 90г.',
                code: 'asdasdsad', //'43000235',
                sum: '425.76',
                price: '35.48',
                amount: '12',
                amountUnit: 'шт',
                vat: '10',
                sumWithVat: '468.34',
                vatSum: '42.58',
                index: '1'
            },
            {
                title: 'Коктейль молочный ФрутоНяня клубника, земляника (м д.ж. 2,1%), 0,2л.',
                code: 'fgdfssad', //'43000397',
                sum: '294.24',
                price: '24.52',
                amount: '12',
                amountUnit: 'шт',
                vat: '10',
                sumWithVat: '323.66',
                vatSum: '29.42',
                index: '1'
            },
            {
                title: 'Вода детская питьевая ФрутоНяня, 1,5л.',
                code: 'ydsgfsgfjsf', //'43000469',
                sum: '601.92',
                price: '33.44',
                amount: '18',
                amountUnit: 'шт',
                vat: '10',
                sumWithVat: '662.11',
                vatSum: '60.19',
                index: '1'
            },
            {
                title: 'Кашка молочная ФрутоНяня гречневая, кукурузная, рисовая - злаковая, 0,2л.',
                code: '43000360',
                sum: '549.9',
                price: '30.55',
                amount: '18',
                amountUnit: 'шт',
                vat: '10',
                sumWithVat: '604.89',
                vatSum: '54.99',
                index: '1'
            },
            {
                title: 'Вода минеральная природная питьевая лечебно- столовая газированная Липецкий Бювет, 1,5л.',
                code: '43000334',
                sum: '169.14',
                price: '28.19',
                amount: '6',
                amountUnit: '',
                vat: '20',
                sumWithVat: '202.97',
                vatSum: '33.83',
                index: '1'
            },
            {
                title: 'Вода детская питьевая ФрутоНяня, 5л.',
                code: 'hfwuhfiweiwuh', //'43000470',
                sum: '2012.4',
                price: '83.85',
                amount: '24',
                amountUnit: 'шт',
                vat: '10',
                sumWithVat: '2213.64',
                vatSum: '201.24',
                index: '1'
            },
            {
                title: 'Сок ФрутоНяня яблоко, осветленный, 0,2л.',
                code: 'fuwgdihkjkjfhksf', //'43000482',
                sum: '426.24',
                price: '23.68',
                amount: '18',
                amountUnit: 'шт',
                vat: '10',
                sumWithVat: '468.86',
                vatSum: '42.62',
                index: '1'
            },
            {
                title: 'Ка Кашка молочная ФрутоНяня пять злаков, персик, 0,2л',
                code: 'fjashdoqdoqijdoqwij', //'43000364',
                sum: '549.9',
                price: '30.55',
                amount: '18',
                amountUnit: 'шт',
                vat: '10',
                sumWithVat: '604.89',
                vatSum: '54.99',
                index: '1'
            },
            {
                title: 'Пюре ФрутоНяня говядина, овощи, 100г.',
                code: 'gdueqgduygwduqgduq', //'43000187',
                sum: '470.16',
                price: '39.18',
                amount: '12',
                amountUnit: 'шт',
                vat: '10',
                sumWithVat: '517.18',
                vatSum: '47.02',
                index: '1'
            },
            {
                title: 'Сок ФрутоНяня яблоко, персик, 0,5л.',
                code: 'uygduyguwg', //'43000504',
                sum: '646.8',
                price: '43.12',
                amount: '15',
                amountUnit: 'шт',
                vat: '10',
                sumWithVat: '711.48',
                vatSum: '64.68',
                index: '1'
            },
            {
                title: 'Пюре с печеньем ФрутоНяня овсяное, яблоко, земляника, ежевика, 90г.',
                code: 'wteuqteuqwte', //'43000255',
                sum: '425.76',
                price: '35.48',
                amount: '12',
                amountUnit: 'шт',
                vat: '10',
                sumWithVat: '468.34',
                vatSum: '42.58',
                index: '1'
            },
            {
                title: 'Пюре ФрутоНяня яблоко, банан, груша, персик - салатик из фруктов, 90г.',
                code: 'gvdcbvjsfbvjsh', //'43000241',
                sum: '425.76',
                price: '35.48',
                amount: '12',
                amountUnit: 'шт',
                vat: '10',
                sumWithVat: '468.34',
                vatSum: '42.58',
                index: '1'
            }
        ]
            .map(convertStringItemToValueItem)
            .map(convertRecognitionResultItemToSupplyItem);

        runTest(firstArray, secondArray, [
            [0, 10],
            [1, 2],
            [2, 8],
            [3, 0],
            [4, 9],
            [5, 1],
            [6, 6],
            [7, 3],
            [8, 7],
            [9, 5],
            [10, 4],
            [11, 11]
        ]);
    });

    it('similar items', () => {
        const firstArray: SupplyItem[] = [
            {
                name: 'Один Два Три Четыре Пять Шесть Семь Восемь',
                quantity: '6',
                price: '98.09',
                sum: '123',
                vat: '10',
                totalSum: '647.40',
                vatSum: '58',
                code: '',
                units: ''
            },
            {
                name: 'Один Два Три Четыре Девять Шесть Семь Восемь',
                quantity: '6',
                price: '98.09',
                sum: '123',
                vat: '10',
                totalSum: '647.40',
                vatSum: '58',
                code: '',
                units: ''
            },
            {
                name: 'Один Четыре Три Четыре Пять Шесть Семь Восемь',
                quantity: '6',
                price: '98.09',
                sum: '123',
                vat: '10',
                totalSum: '647.40',
                vatSum: '58',
                code: '',
                units: ''
            },
            {
                name: 'Один Два Три Четыре Пять Шест Семь Восемь',
                quantity: '6',
                price: '98.09',
                sum: '123',
                vat: '10',
                totalSum: '647.40',
                vatSum: '58',
                code: '',
                units: ''
            },
            {
                name: 'Один Два Четыре Пять Шесть Семь Восемь',
                quantity: '6',
                price: '98.09',
                sum: '123',
                vat: '10',
                totalSum: '647.40',
                vatSum: '58',
                code: '',
                units: ''
            },
            {
                name: 'Один Два Три Четыре Пять Шесть Семь Восемь Девять',
                quantity: '6',
                price: '98.09',
                sum: '123',
                vat: '10',
                totalSum: '647.40',
                vatSum: '58',
                code: '',
                units: ''
            }
        ];

        const secondArray: SupplyItem[] = [
            firstArray[2],
            firstArray[5],
            firstArray[0],
            firstArray[3],
            firstArray[1],
            firstArray[4]
        ];

        runTest(firstArray, secondArray, [
            [2, 0],
            [5, 1],
            [0, 2],
            [3, 3],
            [1, 4],
            [4, 5]
        ]);
    });

    describe('names matching', () => {
        it('extra grammers in name', () => {
            const firstArray: SupplyItem[] = [
                {
                    name: 'Творожок банановый',
                    price: '123',
                    vat: '20',
                    vatSum: '23',
                    sum: '246',
                    quantity: '2',
                    totalSum: '300',
                    code: 'dfwdfdsfewfewf',
                    units: ''
                },
                {
                    name: 'Творожок клубничный 100г',
                    price: '123',
                    vat: '20',
                    vatSum: '23',
                    sum: '246',
                    quantity: '2',
                    totalSum: '300',
                    code: 'sfrewewewcewef',
                    units: ''
                }
            ];

            const secondArray: SupplyItem[] = [
                {
                    name: 'Творожок клубничный',
                    price: '123',
                    vat: '20',
                    vatSum: '23',
                    sum: '246',
                    quantity: '2',
                    totalSum: '300',
                    code: 'fygcjgxcjzhgcs',
                    units: ''
                }
            ];

            const matchedPairs = matchArrays(
                firstArray,
                secondArray,
                calcErpRecognitionItemSimilarity,
                ITEMS_SIMILARITY_THRESHOLD
            );

            const expected = [
                ['Творожок клубничный 100г', 'Творожок клубничный'],
                ['Творожок банановый', null]
            ];

            checkNamesMatching(firstArray, secondArray, matchedPairs, expected);
        });

        it('symbols in name', () => {
            const firstArray: SupplyItem[] = [
                {
                    name: 'Творожок',
                    price: '123',
                    vat: '20',
                    vatSum: '23',
                    sum: '246',
                    quantity: '2',
                    totalSum: '300',
                    code: 'sdwiufiwfuiwf',
                    units: ''
                },
                {
                    name: 'Творожок (100г)',
                    price: '123',
                    vat: '20',
                    vatSum: '23',
                    sum: '246',
                    quantity: '2',
                    totalSum: '300',
                    code: 'idsuhciruchiuwc',
                    units: ''
                }
            ];

            const secondArray: SupplyItem[] = [
                {
                    name: 'Творожок, 100г',
                    price: '123',
                    vat: '20',
                    vatSum: '23',
                    sum: '246',
                    quantity: '2',
                    totalSum: '300',
                    code: 'iduchiwuchwic',
                    units: ''
                }
            ];

            const matchedPairs = matchArrays(
                firstArray,
                secondArray,
                calcErpRecognitionItemSimilarity,
                ITEMS_SIMILARITY_THRESHOLD
            );

            const expected = [
                ['Творожок (100г)', 'Творожок, 100г'],
                ['Творожок', null]
            ];

            checkNamesMatching(firstArray, secondArray, matchedPairs, expected);
        });

        it('case insensitive names', () => {
            const firstArray: SupplyItem[] = [
                {
                    name: 'Творожок',
                    price: '123',
                    vat: '20',
                    vatSum: '23',
                    sum: '246',
                    quantity: '2',
                    totalSum: '300',
                    code: 'fhireiurwhiuwhifhw',
                    units: ''
                },
                {
                    name: 'КОТЛЕТА',
                    price: '123',
                    vat: '20',
                    vatSum: '23',
                    sum: '246',
                    quantity: '2',
                    totalSum: '300',
                    code: 'iduchiwuhihuiuf',
                    units: ''
                }
            ];

            const secondArray: SupplyItem[] = [
                {
                    name: 'Котлета',
                    price: '123',
                    vat: '20',
                    vatSum: '23',
                    sum: '246',
                    quantity: '2',
                    totalSum: '300',
                    code: 'aheqiuhdiquhiqd',
                    units: ''
                }
            ];

            const matchedPairs = matchArrays(
                firstArray,
                secondArray,
                calcErpRecognitionItemSimilarity,
                ITEMS_SIMILARITY_THRESHOLD
            );

            const expected = [
                ['КОТЛЕТА', 'Котлета'],
                ['Творожок', null]
            ];

            checkNamesMatching(firstArray, secondArray, matchedPairs, expected);
        });

        it('extra words in name', () => {
            const firstArray: SupplyItem[] = [
                {
                    name: 'Творожок банановый детский',
                    price: '123',
                    vat: '20',
                    vatSum: '23',
                    sum: '246',
                    quantity: '2',
                    totalSum: '300',
                    code: 'ewiuhdiewuhdiewuhd',
                    units: ''
                },
                {
                    name: 'Творожок идентичный натуральному ООО "Ромашка"',
                    price: '123',
                    vat: '20',
                    vatSum: '23',
                    sum: '246',
                    quantity: '2',
                    totalSum: '300',
                    code: 'ifuvhiufhfdivuh',
                    units: ''
                }
            ];

            const secondArray: SupplyItem[] = [
                {
                    name: 'Творожок идентичный 100г',
                    price: '123',
                    vat: '20',
                    vatSum: '23',
                    sum: '246',
                    quantity: '2',
                    totalSum: '300',
                    code: 'hdiuhiuwhfidshuf',
                    units: ''
                }
            ];

            const matchedPairs = matchArrays(
                firstArray,
                secondArray,
                calcErpRecognitionItemSimilarity,
                ITEMS_SIMILARITY_THRESHOLD
            );

            const expected = [
                ['Творожок идентичный натуральному ООО "Ромашка"', 'Творожок идентичный 100г'],
                ['Творожок банановый детский', null]
            ];

            checkNamesMatching(firstArray, secondArray, matchedPairs, expected);
        });
    });
});

describe('matchRecognitionResultItemsWithErpItems', () => {
    it('matching simple items', async () => {
        const erpSupply: ErpSupply = {
            id: '',
            number: '',
            warehouse: {
                id: '',
                wms_id: '1',
                name: ''
            },
            supplier: {
                inn: '',
                name: '',
                id: '',
                kpp: ''
            },
            items: [
                {
                    id: '0',
                    wms_id: '',
                    supplier_id: 'sdifuhdsifhdsfis',
                    name: 'сосиска',
                    quantity: 0,
                    price: 0,
                    sum: 0,
                    vat: 0,
                    vat_sum: 0,
                    total_sum: 0
                },
                {
                    id: '1',
                    wms_id: '',
                    supplier_id: 'scskjhkjdskc',
                    name: 'котлета',
                    quantity: 0,
                    price: 0,
                    sum: 0,
                    vat: 0,
                    vat_sum: 0,
                    total_sum: 0
                },
                {
                    id: '2',
                    wms_id: '',
                    supplier_id: 'diuhdifhdsifhsdif',
                    name: 'пельмени',
                    quantity: 0,
                    price: 0,
                    sum: 0,
                    vat: 0,
                    vat_sum: 0,
                    total_sum: 0
                }
            ],
            wms_orders: []
        };

        const recognitionResultsJSON: CorrectDocument[] = [
            {
                type: DocumentType.Invoice,
                total: {},
                number: {confidence: {value: 1}, value: '0'},
                pages: [
                    {
                        pageTotal: {},
                        items: [{title: 'котлета'}, {title: 'макароны'}].map(convertStringItemToValueItem),
                        rawTable: []
                    }
                ]
            },
            {
                type: DocumentType.ConsignmentNote,
                total: {},
                number: {confidence: {value: 1}, value: '0'},
                pages: [
                    {
                        pageTotal: {},
                        items: [{title: 'яблоки'}, {title: 'сосиска'}].map(convertStringItemToValueItem),
                        rawTable: []
                    }
                ]
            }
        ];

        const recognitionResults: RecognitionResults[] = [
            {
                id: 0,
                status: RecognitionResultStatus.SUCCESS,
                chunks: [],
                result: serializeDocument(recognitionResultsJSON[0]),
                document: (undefined as unknown) as Documents,
                documentId: 0
            },
            {
                id: 1,
                status: RecognitionResultStatus.SUCCESS,
                chunks: [],
                result: serializeDocument(recognitionResultsJSON[1]),
                document: (undefined as unknown) as Documents,
                documentId: 0
            }
        ];

        const matchedResults = matchRecognitionResultItemsWithErpItems(erpSupply, recognitionResults);

        expect(matchedResults.items).toHaveLength(5);
        expect(matchedResults.items).toContainEqual<ErpRecognitionItem>({
            index: undefined,
            erp: undefined,
            actual: {
                location: {
                    itemIndex: 1,
                    pageIndex: 0,
                    recognitionResultId: 0
                },
                data: {
                    name: 'макароны',
                    sum: '',
                    price: '',
                    vatSum: '',
                    vat: '',
                    quantity: '',
                    code: '',
                    totalSum: '',
                    units: ''
                }
            },
            isExtraItem: true
        });
        expect(matchedResults.items).toContainEqual<ErpRecognitionItem>({
            index: undefined,
            erp: undefined,
            actual: {
                location: {
                    itemIndex: 0,
                    pageIndex: 0,
                    recognitionResultId: 1
                },
                data: {
                    name: 'яблоки',
                    sum: '',
                    price: '',
                    vatSum: '',
                    vat: '',
                    quantity: '',
                    code: '',
                    totalSum: '',
                    units: ''
                }
            },
            isExtraItem: true
        });
        expect(matchedResults.items).toContainEqual<ErpRecognitionItem>({
            index: undefined,
            erp: {
                itemErpId: '2'
            },
            actual: undefined,
            isExtraItem: true
        });
        expect(matchedResults.items).toContainEqual<ErpRecognitionItem>({
            index: undefined,
            erp: {
                itemErpId: '1'
            },
            actual: {
                location: {
                    itemIndex: 0,
                    pageIndex: 0,
                    recognitionResultId: 0
                },
                data: {
                    name: 'котлета',
                    sum: '',
                    price: '',
                    vatSum: '',
                    vat: '',
                    quantity: '',
                    code: '',
                    totalSum: '',
                    units: ''
                }
            },
            isExtraItem: false
        });
        expect(matchedResults.items).toContainEqual<ErpRecognitionItem>({
            index: undefined,
            erp: {
                itemErpId: '0'
            },
            actual: {
                location: {
                    itemIndex: 1,
                    pageIndex: 0,
                    recognitionResultId: 1
                },
                data: {
                    name: 'сосиска',
                    sum: '',
                    price: '',
                    vatSum: '',
                    vat: '',
                    quantity: '',
                    code: '',
                    totalSum: '',
                    units: ''
                }
            },
            isExtraItem: false
        });
    });

    it('matching items with incorrect amount', async () => {
        const erpSupply: ErpSupply = {
            id: '',
            number: '',
            warehouse: {
                id: '',
                wms_id: '1',
                name: ''
            },
            supplier: {
                id: '0',
                name: '',
                kpp: '',
                inn: ''
            },
            items: [
                {
                    id: '0',
                    wms_id: '',
                    supplier_id: 'sdifuhdsifhdsfis',
                    name: 'мышка',
                    quantity: 1,
                    price: 4.5,
                    sum: 9,
                    vat: 0,
                    vat_sum: 0,
                    total_sum: 9
                },
                {
                    id: '1',
                    wms_id: '',
                    supplier_id: 'scskjhkjdskc',
                    name: 'кошка',
                    quantity: 9,
                    price: 1,
                    sum: 1,
                    vat: 0,
                    vat_sum: 0,
                    total_sum: 1
                }
            ],
            wms_orders: []
        };

        const recognitionResultsJSON: CorrectDocument[] = [
            {
                type: DocumentType.ConsignmentNote,
                total: {},
                number: {confidence: {value: 1}, value: '0'},
                pages: [
                    {
                        pageTotal: {},
                        items: [
                            {title: 'мышка', sumWithVat: '9', amount: '33'},
                            {title: 'кошка', sumWithVat: '1', amount: '33'}
                        ].map(convertStringItemToValueItem),
                        rawTable: []
                    }
                ]
            }
        ];

        const recognitionResults: RecognitionResults[] = [
            {
                id: 0,
                status: RecognitionResultStatus.SUCCESS,
                chunks: [],
                result: serializeDocument(recognitionResultsJSON[0]),
                document: (undefined as unknown) as Documents,
                documentId: 0
            }
        ];

        const matchedResults = matchRecognitionResultItemsWithErpItems(erpSupply, recognitionResults);

        expect(matchedResults.items).toHaveLength(2);
        expect(matchedResults.items.sort((d) => d.actual?.location?.itemIndex || 0)).toEqual<
            typeof matchedResults['items']
        >([
            {
                index: undefined,
                actual: {
                    data: {
                        code: '',
                        name: 'мышка',
                        price: '',
                        quantity: '1.00',
                        totalSum: '9.00',
                        sum: '',
                        units: '',
                        vat: '',
                        vatSum: ''
                    },
                    location: {itemIndex: 0, pageIndex: 0, recognitionResultId: 0}
                },
                erp: {itemErpId: '0'},
                isExtraItem: false
            },
            {
                index: undefined,
                actual: {
                    data: {
                        code: '',
                        name: 'кошка',
                        price: '',
                        quantity: '9.00',
                        totalSum: '1.00',
                        sum: '',
                        units: '',
                        vat: '',
                        vatSum: ''
                    },
                    location: {itemIndex: 1, pageIndex: 0, recognitionResultId: 0}
                },
                erp: {itemErpId: '1'},
                isExtraItem: false
            }
        ]);
    });
});

function checkNamesMatching(
    firstArray: SupplyItem[],
    secondArray: SupplyItem[],
    actual: ItemPair[],
    expected: (string | null)[][]
) {
    const actualNames = actual.map((result) => {
        const firstElement = result[0] !== null && result[0] !== undefined ? firstArray[result[0]].name : null;
        const secondElement = result[1] !== null && result[1] !== undefined ? secondArray[result[1]].name : null;

        return [firstElement, secondElement];
    });

    expect(actualNames).toEqual(expected);
}
