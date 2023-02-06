import { TestIdsFieldItemValue } from './testids-field-props';

export function getItemDefaultValue(index: number): TestIdsFieldItemValue {
    if (index === 0) {
        return {
            name: 'Контрольный вариант',
            description: 'Используется как эталон для сравнения, флаги добавлять не обязательно',
            value: undefined,
        };
    }

    return {
        name: `Вариант ${index}`,
        value: [['', '']],
    };
}
