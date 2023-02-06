import {walkThemesTree} from '../utils';

describe('walkThemesTree', function () {
    test('returns transformed items by provided path', () => {
        expect(
            walkThemesTree({
                keyName: 'id',
                path: ['1', '1-1'],
                tree: [
                    {
                        id: '1',
                        value: 'value1',
                        children: [
                            {
                                id: '1-1',
                                value: 'value1-1',
                            },
                            {
                                id: '1-2',
                                value: 'value1-2',
                            },
                        ],
                    },
                    {
                        id: '2',
                        value: 'value2',
                    },
                ],
                transformer: ({value}) => value,
            }),
        ).toEqual(['value1', 'value1-1']);
    });

    test('TXI-9006: should not throw when tree has no such path', () => {
        expect(
            walkThemesTree({
                keyName: 'id',
                path: ['1', '1-1'],
                tree: [
                    {
                        id: '4',
                        value: 'value1',
                        children: [
                            {
                                id: '4-1',
                                value: 'value1-1',
                            },
                            {
                                id: '4-2',
                                value: 'value1-2',
                            },
                        ],
                    },
                    {
                        id: '2',
                        value: 'value2',
                    },
                ],
                transformer: ({value}) => value,
            }),
        ).toEqual([]);
    });
});
