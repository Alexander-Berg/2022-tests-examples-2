import {sortBy} from 'lodash';

import {toInitialFlat} from '../utils';

describe('toInitialFlat', () => {
    test('Корректно сворачивает модельку в массив настроек', () => {
        const model = {
            key1: {
                value: 'value1',
                key2: {
                    value: 'value2'
                }
            },
            key3: {
                key4: {
                    value: 'value4'
                }
            }
        };

        const expected = [
            {
                setting_key: 'key1',
                setting_value: 'value1'
            },
            {
                setting_key: 'key1.key2',
                setting_value: 'value2'
            },
            {
                setting_key: 'key3.key4',
                setting_value: 'value4'
            }
        ];

        expect(sortBy(toInitialFlat(model), 'setting_key')).toEqual(sortBy(expected, 'setting_key'));
    });

    test('Пустая моделька вернет пустой массив', () => {
        const model = {};

        expect(toInitialFlat(model)).toEqual([]);
    });
});
