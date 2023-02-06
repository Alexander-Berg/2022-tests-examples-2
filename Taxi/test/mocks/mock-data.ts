import {convertStringItemToValueItem, convertStringSumsToValueSums} from 'tests/unit/test-factory';

import type {Document} from 'server/recognition/types/types';
import {DocumentType} from 'types/documents';
import type {ErpSupply} from 'types/erp';
import type {ErpRecognitionResult} from 'types/erp-recognition-results';

export const mockErpSupplies: ErpSupply[] = [
    {
        id: 'erpId_1',
        number: 'supplyNumber',
        warehouse: {
            id: '1',
            wms_id: '1',
            name: 'ул. Тестовская, д. 0'
        },
        supplier: {
            inn: '1234567890',
            name: 'Тестовый поставщик',
            id: '0',
            kpp: '09876554321'
        },
        items: [
            {
                id: '1',
                wms_id: '',
                supplier_id: 1,
                name: 'сырок Б. Ю. Александров',
                quantity: 1,
                price: 47.99,
                sum: 47.99,
                vat: 10,
                total_sum: 0,
                vat_sum: 0
            },
            {
                id: '2',
                wms_id: '',
                supplier_id: 1,
                name: 'кашка',
                quantity: 2,
                price: 55.55,
                sum: 111,
                vat: 10,
                total_sum: 0,
                vat_sum: 0
            }
        ],
        wms_orders: []
    },
    {
        id: 'erpId_2',
        number: 'supplyNumber',
        warehouse: {
            id: '1',
            wms_id: '',
            name: 'ул. Тестовская, д. 0'
        },
        supplier: {
            inn: '1234567890',
            name: 'Тестовый поставщик',
            id: '0',
            kpp: '09876554321'
        },
        items: [
            {
                id: '1',
                wms_id: '',
                supplier_id: 1,
                name: 'пельмени',
                quantity: 3,
                price: 200,
                sum: 600,
                vat: 10,
                total_sum: 0,
                vat_sum: 0
            }
        ],
        wms_orders: []
    }
];

export const mockRecognitionResults: Document[] = [
    {
        type: DocumentType.Invoice,
        total: convertStringSumsToValueSums({sumWithVat: '234', sum: '123'}),
        number: {confidence: {value: 1}, value: 'invoiceNumber'},
        pages: [
            {
                pageTotal: convertStringSumsToValueSums({sumWithVat: '234', sum: '123'}),
                items: [
                    {sum: '66.99', price: '88.99', title: 'сырок Б. Ю. Александров'},
                    {sum: '111', price: '55.55', title: 'кашка'}
                ].map(convertStringItemToValueItem),
                rawTable: []
            }
        ]
    },
    {
        type: DocumentType.ConsignmentNote,
        total: convertStringSumsToValueSums({sumWithVat: '234', sum: '123'}),
        number: {confidence: {value: 1}, value: 'consignmentNoteNumber'},
        pages: [
            {
                pageTotal: convertStringSumsToValueSums({sumWithVat: '234', sum: '123'}),
                items: [
                    {sum: '47.99', price: '48', title: 'кефирные грибки'},
                    {sum: '111', price: '55.55', title: 'тапочки'}
                ].map(convertStringItemToValueItem),
                rawTable: []
            }
        ]
    },
    {
        type: DocumentType.PackingList,
        total: convertStringSumsToValueSums({sumWithVat: '234', sum: '123'}),
        number: {confidence: {value: 1}, value: 'packinglistNumber'},
        pages: [
            {
                pageTotal: convertStringSumsToValueSums({sumWithVat: '234', sum: '123'}),
                items: [{sum: '600', price: '200', title: 'пельмени'}].map(convertStringItemToValueItem),
                rawTable: []
            }
        ]
    },
    {
        type: DocumentType.UniversalTransferDocument,
        total: convertStringSumsToValueSums({sumWithVat: '234', sum: '123'}),
        number: {confidence: {value: 1}, value: 'universalTransferDocumentNumber'},
        pages: [
            {
                pageTotal: convertStringSumsToValueSums({sumWithVat: '234', sum: '123'}),
                items: [{sum: '600', price: '200', title: 'вареники'}].map(convertStringItemToValueItem),
                rawTable: []
            }
        ]
    }
];

export const mockErpRecognitionResults: ErpRecognitionResult[] = [
    [
        {
            documentsIds: [],
            items: [
                {
                    erp: {
                        data: {
                            sum: '496.8',
                            vat: '20',
                            code: '',
                            name: 'Батончик Lucky Snacky из пастилы яблочный, 30 г',
                            price: '49.68',
                            units: '',
                            vatSum: '99.36',
                            quantity: '12',
                            totalSum: '596.16'
                        },
                        itemErpId: '11091'
                    },
                    isExtraItem: true,
                    isConfirmedItem: true
                },
                {
                    erp: {
                        data: {
                            sum: '118.08',
                            vat: '20',
                            code: '',
                            name: 'Батончик «Обыкновенное чудо» классическое, 40 г',
                            price: '11.80833333',
                            units: '',
                            vatSum: '23.62',
                            quantity: '12',
                            totalSum: '141.7'
                        },
                        itemErpId: '14003'
                    },
                    isExtraItem: true,
                    isConfirmedItem: true
                }
            ],
            totalSum: {
                withVat: {actual: '0', isConfirmed: false},
                withoutVat: {actual: '0', isConfirmed: false},
                vatSum: {actual: '0', isConfirmed: false}
            }
        }
    ]
];
