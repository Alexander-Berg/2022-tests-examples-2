import {utils} from '@constructor/compiler-common';
import {createApiClass, createApiInstance, createApiMethod, createMergedParameter, createUrl} from './ast';
import ts from 'typescript';

const {formatContent} = utils.format;
const {printAst} = utils.ast;

describe('createUrl', () => {
    test('without params', () => {
        const result = printAst(createUrl('/list'));
        expect(result).toBe(formatContent('"/list"'));
    });

    test('with single parameter', () => {
        const result = printAst(createUrl('/list/{id}'));
        expect(result).toBe(formatContent('`/list/${params.urlParams?.id}`'));
    });

    test('with multiple parameters', () => {
        const result = printAst(createUrl('/list/{id}/order/{type}'));
        expect(result).toBe(formatContent('`/list/${params.urlParams?.id}/order/${params.urlParams?.type}`'));
    });

    test('complex parameter name', () => {
        const result = printAst(createUrl('/list/{my_type-id}/create'));
        expect(result).toBe(formatContent('`/list/${params.urlParams?.myTypeId}/create`'));
    });
});

describe('createMergedParameter', () => {
    test('merge body', () => {
        const result = printAst(
            ts.factory.createExportDefault(
                ts.factory.createObjectLiteralExpression([
                    createMergedParameter('body', {
                        a: {b: {c: 1}},
                        d: '2',
                    }),
                ]),
            ),
        );

        expect(result).toBe(
            formatContent(`export default {
            body: {
                a: {b: {c: 1}},
                d: '2',
                ...(params.body || {})
            }
        }`),
        );
    });
});

describe('createApiClass', () => {
    test('empty class', () => {
        const result = printAst(createApiClass('TestAPI', []));
        expect(result).toBe(formatContent('class TestAPI extends BaseAPI {}'));
    });

    test('class with simple method', () => {
        const result = printAst(createApiClass('TestAPI', [createApiMethod('list', {method: 'GET', url: '/list'})]));

        expect(result).toBe(
            formatContent(`class TestAPI extends BaseAPI {
            list(params: RequestParams) {
                return this.request({
                    url: '/list',
                    method: 'GET',
                    ...params,
                });
            }
        }`),
        );
    });

    test('class with complex method', () => {
        const result = printAst(
            createApiClass('TestAPI', [
                createApiMethod('list', {
                    method: 'GET',
                    url: '/list/{type}',
                    query: {
                        limit: 50,
                    },
                    headers: {
                        'X-Test': 'test',
                    },
                }),
            ]),
        );

        expect(result).toBe(
            formatContent(`class TestAPI extends BaseAPI {
            list(params: RequestParams) {
                return this.request({
                    url: \`/list/\${params.urlParams?.type}\`,
                    method: 'GET',
                    ...params,
                    query: {
                        limit: 50,
                        ...(params.query || {}),
                    },
                    headers: {
                        'X-Test': 'test',
                        ...(params.headers || {}),
                    }
                });
            }
        }`),
        );
    });

    test('class with multiple methods', () => {
        const result = printAst(
            createApiClass('TestAPI', [
                createApiMethod('list', {method: 'GET', url: '/list'}),
                createApiMethod('find', {method: 'GET', url: '/find'}),
            ]),
        );

        expect(result).toBe(
            formatContent(`class TestAPI extends BaseAPI {
            list(params: RequestParams) {
                return this.request({
                    url: '/list',
                    method: 'GET',
                    ...params,
                });
            }
            find(params: RequestParams) {
                return this.request({
                    url: '/find',
                    method: 'GET',
                    ...params,
                });
            }
        }`),
        );
    });
});

describe('createApiInstance', () => {
    test('make instance', () => {
        const result = printAst(
            createApiInstance('TestAPI', {
                host: 'http://...',
            }),
        );

        expect(result).toBe(formatContent("new TestAPI({ host: 'http://...' });"));
    });
});
