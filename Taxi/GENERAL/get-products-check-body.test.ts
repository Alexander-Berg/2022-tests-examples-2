import {describe, expect, it} from 'tests/jest.globals';

import {StructValidationError} from '@/src/errors';

import {validate} from './get-products';

const limitOffsetOk = {
    limit: 1,
    offset: 2
};

function executeValidation(body: unknown) {
    return validate({
        context: {} as never,
        payload: {body}
    });
}

describe('get products check body', () => {
    it('should be correct with limit and offset', async () => {
        expect(() => executeValidation({limit: 1})).toThrow(StructValidationError);
        expect(() => executeValidation({offset: 1})).toThrow(StructValidationError);
        expect(() => executeValidation(limitOffsetOk)).not.toThrow();
    });

    it('should be correct with empty "filters"', async () => {
        expect(() => executeValidation({...limitOffsetOk, filters: {}})).not.toThrow();
    });

    it('should be correct "range" on "filters.identifier"', async () => {
        const action = 'range';
        const correct = [
            [1, 2],
            [null, 1],
            [1, null]
        ];

        for (const values of correct) {
            expect(() =>
                executeValidation({
                    ...limitOffsetOk,
                    filters: {
                        identifier: {action, values}
                    }
                })
            ).not.toThrow();
        }

        const wrong = [[], [null], [1], [1, 2, 3], ['foo', 'bar'], 'bar', 1, [1, 'foo']];

        for (const values of wrong) {
            expect(() =>
                executeValidation({
                    ...limitOffsetOk,
                    filters: {
                        identifier: {action, values}
                    }
                })
            ).toThrow(StructValidationError);
        }
    });

    it('should be correct ["equal", "not-equal"] on "filters.identifier"', async () => {
        const actions = ['equal', 'not-equal'];

        for (const action of actions) {
            const correct = [[1], [1, 2], [1, 2, 3]];

            for (const values of correct) {
                expect(() =>
                    executeValidation({
                        ...limitOffsetOk,
                        filters: {
                            identifier: {action, values}
                        }
                    })
                ).not.toThrow();
            }

            const wrong = [[], [null], ['foo'], [true], 1, [1, 2, 'foo']];

            for (const values of wrong) {
                expect(() =>
                    executeValidation({
                        ...limitOffsetOk,
                        filters: {
                            identifier: {action, values}
                        }
                    })
                ).toThrow(StructValidationError);
            }
        }
    });

    it('should be correct on "filters.status"', async () => {
        const correct = [['foo'], ['foo', 'bar'], ['foo', 'bar', 'foobar']];

        for (const status of correct) {
            expect(() =>
                executeValidation({
                    ...limitOffsetOk,
                    filters: {
                        status
                    }
                })
            ).not.toThrow();
        }

        const wrong = [[], [null], [1], [1, 2], [true], 1, 'foo', ['foo', 1]];

        for (const status of wrong) {
            expect(() =>
                executeValidation({
                    ...limitOffsetOk,
                    filters: {
                        status
                    }
                })
            ).toThrow(StructValidationError);
        }
    });

    it('should be correct on "filters" ["masterCategoryIds", "masterCategoryIds", "infoModelIds"]', async () => {
        const keys = ['masterCategoryIds', 'masterCategoryIds', 'infoModelIds'];

        for (const key of keys) {
            const correct = [[1], [1, 2, 3]];

            for (const values of correct) {
                expect(() =>
                    executeValidation({
                        ...limitOffsetOk,
                        filters: {
                            [key]: values
                        }
                    })
                ).not.toThrow();
            }

            const wrong = [[], [null], 1, 'foo', ['foo'], [1, 'foo']];

            for (const values of wrong) {
                expect(() =>
                    executeValidation({
                        ...limitOffsetOk,
                        filters: {
                            [key]: values
                        }
                    })
                ).toThrow(StructValidationError);
            }
        }
    });

    it('should be correct on "filters" ["createdAtSeconds", "updatedAtSeconds"]', async () => {
        const keys = ['createdAtSeconds', 'updatedAtSeconds'];

        for (const key of keys) {
            const correct = [
                [1, 2],
                [null, 1],
                [1, null]
            ];

            for (const values of correct) {
                expect(() =>
                    executeValidation({
                        ...limitOffsetOk,
                        filters: {
                            [key]: values
                        }
                    })
                ).not.toThrow();
            }

            const wrong = [[], [null], [1], [1, 2, 3], ['foo', 'bar'], 'bar', 1, [1, 'foo']];

            for (const values of wrong) {
                expect(() =>
                    executeValidation({
                        ...limitOffsetOk,
                        filters: {
                            [key]: values
                        }
                    })
                ).toThrow(StructValidationError);
            }
        }
    });

    it('should be correct "range" on "filters.attributes"', async () => {
        const action = 'range';
        const correct = [
            [1, 2],
            [null, 1],
            [1, null]
        ];

        for (const values of correct) {
            expect(() =>
                executeValidation({
                    ...limitOffsetOk,
                    filters: {
                        attributes: {
                            foo: {action, values}
                        }
                    }
                })
            ).not.toThrow();
        }

        const wrong = [[], [null], [1], [1, 2, 3], ['foo', 'bar'], 'bar', 1, [1, 'foo']];

        for (const values of wrong) {
            expect(() =>
                executeValidation({
                    ...limitOffsetOk,
                    filters: {
                        attributes: {
                            foo: {action, values}
                        }
                    }
                })
            ).toThrow(StructValidationError);
        }
    });

    it('should be correct ["contain", "not-contain", "equal", "not-equal"] on "filters.attributes"', async () => {
        const actions = ['contain', 'not-contain', 'equal', 'not-equal'];

        for (const action of actions) {
            const correct = [
                ['foo'],
                ['foo', 'bar'],
                ['foo', 'bar', 'foobar'],
                ...(['contain', 'not-contain'].includes(action) ? [] : [[1], [1, 2], [1, 2, 3]])
            ];

            for (const values of correct) {
                expect(() =>
                    executeValidation({
                        ...limitOffsetOk,
                        filters: {
                            attributes: {
                                foo: {action, values}
                            }
                        }
                    })
                ).not.toThrow();
            }

            const wrong = [[], [null], [true], 1, 'foo', [1, 'foo']];

            for (const values of wrong) {
                expect(() =>
                    executeValidation({
                        ...limitOffsetOk,
                        filters: {
                            attributes: {
                                foo: {action, values}
                            }
                        }
                    })
                ).toThrow(StructValidationError);
            }
        }
    });

    it('should be correct "null" on "filters.attributes"', async () => {
        const action = 'null';

        const correct: Array<string | number | null> = [];
        const wrong: Array<string | number | null> = [null, '', 0];

        expect(() =>
            executeValidation({
                ...limitOffsetOk,
                filters: {
                    attributes: {
                        foo: {action, values: correct}
                    }
                }
            })
        ).not.toThrow();

        expect(() =>
            executeValidation({
                ...limitOffsetOk,
                filters: {
                    attributes: {
                        foo: {action, values: wrong}
                    }
                }
            })
        ).toThrow(StructValidationError);
    });

    it('should be correct "boolean" on "filters.attributes"', async () => {
        expect(() =>
            executeValidation({
                ...limitOffsetOk,
                filters: {
                    attributes: {
                        foo: true
                    }
                }
            })
        ).not.toThrow();
    });

    it('should be correct "select" on "filters.attributes"', async () => {
        expect(() =>
            executeValidation({
                ...limitOffsetOk,
                filters: {
                    attributes: {
                        foo: ['foo', 'bar']
                    }
                }
            })
        ).not.toThrow();
    });

    it('should be correct "boolean" on "withUnusedAttributes"', async () => {
        expect(() =>
            executeValidation({
                ...limitOffsetOk,
                withUnusedAttributes: true
            })
        ).not.toThrow();
    });
});
