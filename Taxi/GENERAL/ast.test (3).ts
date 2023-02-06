import {utils} from '@constructor/compiler-common';
import {createQueries} from './ast';

const {formatContent} = utils.format;
const {printAst} = utils.ast;

describe('createQueries', () => {
    test('empty queries', () => {
        const result = printAst(createQueries({}));
        expect(result).toBe(formatContent('export const $queries = {}'));
    });

    test('queries without options', () => {
        const $api = {test: {foo: () => null}};
        const result = printAst(
            createQueries({
                xxx: () => $api.test.foo(),
            }),
        );

        expect(result).toBe(
            formatContent(
                `export const $queries = {
                    xxx: makeQuery('xxx', () => $api.test.foo(), undefined)
                }`,
            ),
        );
    });

    test('queries with options', () => {
        const $api = {test: {foo: () => null}};
        const result = printAst(
            createQueries({
                xxx: {
                    fn: () => $api.test.foo(),
                    options: {
                        debounce: 200,
                    },
                },
            }),
        );

        expect(result).toBe(
            formatContent(
                `export const $queries = {
                    xxx: makeQuery('xxx', () => $api.test.foo(), {debounce: 200})
                }`,
            ),
        );
    });
});
