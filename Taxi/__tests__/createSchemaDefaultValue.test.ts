import {createSchemaDefaultValue} from '../createSchemaDefaultValue';

describe('createSchemaDefaultValue', () => {
    test('Устанавливает значение из фоллбэка', () => {
        const fallback = {foo: 'bar'};
        expect(createSchemaDefaultValue({}, fallback)).toBe(fallback);
    });

    describe('type: array', () => {
        test('Устанавливает значение по-умолчанию из default', () => {
            const actual = createSchemaDefaultValue({
                type: 'array',
                items: {},
                default: [1]
            });

            const expected = [1];

            expect(actual).toStrictEqual(expected);
        });

        test('Не устанавливает значение по-умолчанию из default, если оно некорректно', () => {
            const actual = createSchemaDefaultValue({
                type: 'array',
                items: {},
                default: 'foo'
            });

            expect(actual).toBeUndefined();
        });

        test('Устанавливает дефолтное значение по-умолчанию, если не указан default', () => {
            const actual = createSchemaDefaultValue({
                type: 'array',
                items: {}
            });

            expect(actual).toStrictEqual([]);
        });
    });

    describe('type: string', () => {
        test('Устанавливает значение по-умолчанию из default', () => {
            const actual = createSchemaDefaultValue({
                type: 'string',
                default: 'foo'
            });

            expect(actual).toBe('foo');
        });

        test('Не устанавливает значение по-умолчанию из default, если оно некорректно', () => {
            const actual = createSchemaDefaultValue({
                type: 'string',
                default: 1
            });

            expect(actual).toBeUndefined();
        });
    });

    describe('type: boolean', () => {
        test('Устанавливает значение по-умолчанию из default', () => {
            const actual = createSchemaDefaultValue({
                type: 'boolean',
                default: true
            });

            expect(actual).toBe(true);
        });

        test('Не устанавливает значение по-умолчанию из default, если оно некорректно', () => {
            const actual = createSchemaDefaultValue({
                type: 'boolean',
                default: 1
            });

            expect(actual).toBeUndefined();
        });
    });

    describe('type: object', () => {
        test('Устанавливает значение по-умолчанию из default', () => {
            const actual = createSchemaDefaultValue({
                type: 'object',
                properties: {},
                default: {
                    foo: 'bar'
                }
            });

            const expected = {foo: 'bar'};

            expect(actual).toStrictEqual(expected);
        });

        test('Не устанавливает значение по-умолчанию из default, если оно некорректно', () => {
            const actual = createSchemaDefaultValue({
                type: 'object',
                properties: {},
                default: 1
            });

            expect(actual).toBeUndefined();
        });

        test('Устанавливает значение по-умолчанию для дочерних полей, если не указан default', () => {
            const actual = createSchemaDefaultValue({
                type: 'object',
                properties: {
                    foo: {
                        type: 'string',
                        default: 'bar'
                    }
                }
            });

            const expected = {foo: 'bar'};

            expect(actual).toStrictEqual(expected);
        });

        test('Устанавливает дефолтное значение по-умолчанию, если не указан default', () => {
            const actual = createSchemaDefaultValue({
                type: 'object',
                properties: {}
            });

            expect(actual).toStrictEqual({});
        });
    });

    describe('type: number', () => {
        test('Устанавливает значение по-умолчанию из default', () => {
            const actual = createSchemaDefaultValue({
                type: 'number',
                default: 1
            });

            expect(actual).toBe(1);
        });

        test('Устанавливает значение по-умолчанию из default для falsy значений', () => {
            const actual = createSchemaDefaultValue({
                type: 'number',
                default: 0
            });

            expect(actual).toBe(0);
        });

        test('Не устанавливает значение по-умолчанию из default, если оно некорректно', () => {
            const actual = createSchemaDefaultValue({
                type: 'number',
                default: 'foo'
            });

            expect(actual).toBeUndefined();
        });
    });

    describe('type: integer', () => {
        test('Устанавливает значение по-умолчанию из default', () => {
            const actual = createSchemaDefaultValue({
                type: 'integer',
                default: 1
            });

            expect(actual).toBe(1);
        });

        test('Не устанавливает значение по-умолчанию из default, если оно некорректно', () => {
            const actual = createSchemaDefaultValue({
                type: 'integer',
                default: 'foo'
            });

            expect(actual).toBeUndefined();
        });
    });
});
