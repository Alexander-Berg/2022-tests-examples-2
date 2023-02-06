import { Segment } from '../../typings';

const nonExistentFilters: Segment[] = [
    {
        id: 'NonExistentId',
        type: 'tree',
        data: {
            inverted: true,
            items: [],
        },
    },
];

const stringValueFilter: Segment[] = [
    {
        id: 'Site',
        type: 'substring',
        data: {
            value: '4',
        },
    },
];

const listFilter: Segment[] = [
    {
        id: 'Site',
        type: 'list',
        data: {
            items: ['4'],
            inverted: false,
        },
    },
];

const listFilters: Segment[] = [
    {
        id: 'Site',
        type: 'list',
        data: {
            items: ['4', '5'],
            inverted: false,
        },
    },
];

const listFilterInverted: Segment[] = [
    {
        id: 'Site',
        type: 'list',
        data: {
            items: ['4'],
            inverted: true,
        },
    },
];

const listFiltersInverted: Segment[] = [
    {
        id: 'Site',
        type: 'list',
        data: {
            items: ['4', '5'],
            inverted: true,
        },
    },
];

const treeFilter: Segment[] = [
    {
        id: 'OperatingSystemRoot',
        type: 'tree',
        data: {
            inverted: false,
            items: [[undefined, 'Windows 7']],
        },
    },
];

const treeFilterInverted: Segment[] = [
    {
        id: 'OperatingSystemRoot',
        type: 'tree',
        data: {
            inverted: true,
            items: [[undefined, 'Windows 7']],
        },
    },
];

const treeFilters: Segment[] = [
    {
        id: 'OperatingSystemRoot',
        type: 'tree',
        data: {
            inverted: false,
            items: [
                [undefined, 'Windows 7'],
                [undefined, 'Android Oreo'],
            ],
        },
    },
];

const treeFiltersInverted: Segment[] = [
    {
        id: 'OperatingSystemRoot',
        type: 'tree',
        data: {
            inverted: true,
            items: [
                ['windows', 'Windows 7'],
                ['android', 'Android Oreo'],
            ],
        },
    },
];

const treeDifferentFilters: Segment[] = [
    {
        id: 'OperatingSystemRoot',
        type: 'tree',
        data: {
            inverted: false,
            items: [
                ['windows', 'Windows 7'],
                ['android', 'Android Oreo'],
            ],
        },
    },
    {
        id: 'RegionCountry',
        type: 'tree',
        data: {
            inverted: false,
            items: [['225', '1', '213']],
        },
    },
];

const treeDifferentFiltersInverted: Segment[] = [
    {
        id: 'OperatingSystemRoot',
        type: 'tree',
        data: {
            inverted: true,
            items: [
                ['windows', 'Windows 7'],
                ['android', 'Android Oreo'],
            ],
        },
    },
    {
        id: 'RegionCountry',
        type: 'tree',
        data: {
            inverted: true,
            items: [['225', '1', '213']],
        },
    },
];

const mixedFilters: Segment[] = [
    {
        id: 'Site',
        type: 'list',
        data: {
            inverted: true,
            items: ['200', '3776', '98'],
        },
    },
    {
        id: 'Domain',
        type: 'list',
        data: {
            inverted: false,
            items: ['yastatic.net', 'yandex.ru'],
        },
    },
    {
        id: 'OperatingSystemRoot',
        type: 'tree',
        data: {
            inverted: false,
            items: [
                ['windows'],
                ['android', 'Android+Nougat'],
                ['android', 'Android+Oreo'],
            ],
        },
    },
];
export {
    nonExistentFilters,
    stringValueFilter,
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
