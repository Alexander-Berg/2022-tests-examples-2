import path from 'path';

import {UrlsCollector} from '../collectUrls';

const collector = new UrlsCollector();

describe('collectUrls', () => {
    test('string literal', () => {
        const {urls} = collector.collectUrls([path.resolve(__dirname, './cases/string-literal/index.ts')]);
        expect(urls).toEqual(['/test-url']);
    });

    test('variable', () => {
        const {urls} = collector.collectUrls([path.resolve(__dirname, './cases/variable/index.ts')]);
        expect(urls).toEqual(['/test-url']);
    });

    test('property access', () => {
        const {urls} = collector.collectUrls([path.resolve(__dirname, './cases/property-access/index.ts')]);
        expect(urls).toEqual(['/test-url']);
    });

    test('enum access', () => {
        const {urls} = collector.collectUrls([path.resolve(__dirname, './cases/enum-access/index.ts')]);
        expect(urls).toEqual(['/test-url']);
    });

    test('string template', () => {
        const {urls} = collector.collectUrls([path.resolve(__dirname, './cases/string-template/index.ts')]);
        expect(urls).toEqual(['/test-url/tab/users/2']);
    });

    test('import string literal', () => {
        const {urls} = collector.collectUrls([path.resolve(__dirname, './cases/import-string-literal/index.ts')]);
        expect(urls).toEqual(['/test-url']);
    });

    test('import property access', () => {
        const {urls} = collector.collectUrls([path.resolve(__dirname, './cases/import-property-access/index.ts')]);
        expect(urls).toEqual(['/test-url']);
    });

    test('import enum access', () => {
        const {urls} = collector.collectUrls([path.resolve(__dirname, './cases/import-enum-access/index.ts')]);
        expect(urls).toEqual(['/test-url']);
    });

    test('import string template', () => {
        const {urls} = collector.collectUrls([path.resolve(__dirname, './cases/import-string-template/index.ts')]);
        expect(urls).toEqual(['/test-url/tab/users/2']);
    });

    test('import asterisk', () => {
        const {urls} = collector.collectUrls([path.resolve(__dirname, './cases/import-asterisk/index.ts')]);
        expect(urls).toEqual(['/route']);
    });

    test('mixed', () => {
        const {urls} = collector.collectUrls([path.resolve(__dirname, './cases/mixed/index.ts')]);
        expect(urls).toEqual([
            '/test-url',
            '/test-url/2',
            '/test-url/users/3',
            '/test-url/orders/4',
            '/promocodes/5',
            '/promocodes/6'
        ]);
    });
});
