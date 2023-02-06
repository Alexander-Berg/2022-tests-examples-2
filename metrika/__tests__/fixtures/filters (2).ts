import { SegmentsData } from 'shared/types/api';

const nonExistentFilters: SegmentsData = [
    {
        id: 'NonExistentId',
        data: {
            inverted: true,
            values: [],
        },
    },
];

/**
 * todo добавление нового типа в типы влечёт большую доработку в TS
 */
// const nullValueFilter: SegmentsData = [
//     {
//         id: 'Site',
//         data: {
//             values: [
//                 {
//                     value: null,
//                     operator: '==',
//                 },
//             ],
//             inverted: false,
//         },
//     },
// ];

const stringValueFilter: SegmentsData = [
    {
        id: 'Site',
        data: {
            values: [
                {
                    value: '4',
                    operator: '==',
                },
            ],
            inverted: false,
        },
    },
];

const listFilter: SegmentsData = [
    {
        id: 'Site',
        data: {
            values: [
                {
                    value: '4',
                    operator: '==',
                },
            ],
            inverted: false,
        },
    },
];

const listFilters: SegmentsData = [
    {
        id: 'Site',
        data: {
            values: [
                {
                    value: '4',
                    operator: '==',
                },
                {
                    value: '5',
                    operator: '==',
                },
            ],
            inverted: false,
        },
    },
];

const booleanFilters: SegmentsData = [
    {
        id: 'sound',
        data: {
            value: 'Yes',
        },
    },
];

const booleanFiltersFalse: SegmentsData = [
    {
        id: 'sound',
        data: {
            value: 'No',
        },
    },
];

const listFilterInverted: SegmentsData = [
    {
        id: 'Site',
        data: {
            values: [
                {
                    value: '4',
                    operator: '==',
                },
            ],
            inverted: true,
        },
    },
];

const listFiltersInverted: SegmentsData = [
    {
        id: 'Site',
        data: {
            values: [
                {
                    value: '4',
                    operator: '==',
                },
                {
                    value: '5',
                    operator: '==',
                },
            ],
            inverted: true,
        },
    },
];

const treeFilter: SegmentsData = [
    {
        id: 'OperatingSystemRoot',
        data: {
            inverted: false,
            paths: [
                {
                    path: ['windows', 'Windows 7'],
                },
            ],
        },
    },
];

const treeFilterInverted: SegmentsData = [
    {
        id: 'OperatingSystemRoot',
        data: {
            inverted: true,
            paths: [
                {
                    path: ['windows', 'Windows 7'],
                },
            ],
        },
    },
];

const treeFilters: SegmentsData = [
    {
        id: 'OperatingSystemRoot',
        data: {
            inverted: false,
            paths: [
                {
                    path: ['windows', 'Windows 7'],
                },
                {
                    path: ['android', 'Android Oreo'],
                },
            ],
        },
    },
];

const treeFiltersInverted: SegmentsData = [
    {
        id: 'OperatingSystemRoot',
        data: {
            inverted: true,
            paths: [
                {
                    path: ['windows', 'Windows 7'],
                },
                {
                    path: ['android', 'Android Oreo'],
                },
            ],
        },
    },
];

const treeDifferentFilters: SegmentsData = [
    {
        id: 'OperatingSystemRoot',
        data: {
            inverted: false,
            paths: [
                {
                    path: ['windows', 'Windows 7'],
                },
                {
                    path: ['android', 'Android Oreo'],
                },
            ],
        },
    },
    {
        id: 'RegionCountry',
        data: {
            inverted: false,
            paths: [
                {
                    path: ['225', '1', '213'],
                },
            ],
        },
    },
];

const treeDifferentFiltersInverted: SegmentsData = [
    {
        id: 'OperatingSystemRoot',
        data: {
            inverted: true,
            paths: [
                {
                    path: ['windows', 'Windows 7'],
                },
                {
                    path: ['android', 'Android Oreo'],
                },
            ],
        },
    },
    {
        id: 'RegionCountry',
        data: {
            inverted: true,
            paths: [
                {
                    path: ['225', '1', '213'],
                },
            ],
        },
    },
];

const mixedFilters: SegmentsData = [
    {
        id: 'Site',
        data: {
            inverted: true,
            values: [
                { value: '200', operator: '==' },
                { value: '3776', operator: '==' },
                { value: '98', operator: '==' },
            ],
        },
    },
    {
        id: 'Domain',
        data: {
            inverted: false,
            values: [
                { value: 'yastatic.net', operator: '==' },
                { value: 'yandex.ru', operator: '==' },
            ],
        },
    },
    {
        id: 'OperatingSystemRoot',
        data: {
            inverted: false,
            paths: [
                { path: ['windows'] },
                { path: ['android', 'Android+Nougat'] },
                { path: ['android', 'Android+Oreo'] },
            ],
        },
    },
];
export {
    nonExistentFilters,
    stringValueFilter,
    booleanFilters,
    booleanFiltersFalse,
    listFilter,
    listFilters,
    listFilterInverted,
    listFiltersInverted,
    treeFilter,
    treeFilterInverted,
    treeFilters,
    treeFiltersInverted,
    treeDifferentFilters,
    treeDifferentFiltersInverted,
    mixedFilters,
};
