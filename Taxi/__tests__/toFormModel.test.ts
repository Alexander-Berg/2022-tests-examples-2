import {SettingsTree} from '../types';
import {toFormModel} from '../utils';

describe('toFormModel', () => {
    test('Корректно строит модельку', () => {
        const tree: SettingsTree = {
            children: [
                {
                    key: 'key1',
                    path: 'key1',
                    value: 'value1',
                    children: [
                        {
                            key: 'key2',
                            path: 'key1.key2',
                            value: 'value2'
                        }
                    ]
                }
            ]
        };

        const expected = {
            key1: {
                value: 'value1',
                key2: {
                    value: 'value2'
                }
            }
        };

        expect(toFormModel(tree)).toEqual(expected);
    });

    test('Пустое дерево возвращает пустой объект модельки', () => {
        const tree: SettingsTree = {
            children: []
        };

        expect(toFormModel(tree)).toEqual({});
    });
});
