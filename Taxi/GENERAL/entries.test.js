import {filterEntries, isIncluded} from './entries';

describe('webpack entries utils', () => {
    describe('isIncluded', () => {
        it('should be work with string and regexp', () => {
            const entry = 'webview/history';
            expect(isIncluded(entry, [/^webview/])).toBeTruthy();
            expect(isIncluded(entry, [/^not_webview/])).toBeFalsy();
            expect(isIncluded(entry, ['webview/history'])).toBeTruthy();
            expect(isIncluded(entry, ['not_webview/history'])).toBeFalsy();
        });

        it('should be true if some rule return true', () => {
            const entry = 'webview/history';
            expect(isIncluded(entry, [/^webview/, 'not_webview'])).toBeTruthy();
            expect(isIncluded(entry, [/^webview/, 'webview/history'])).toBeTruthy();
            expect(isIncluded(entry, [/^not_webview/, 'not_webview'])).toBeFalsy();
        });
    });

    describe('filter entries', () => {
        it('should be return as is', () => {
            const entries = {
                'webview/help': [],
                'webview/history': []
            };

            expect(filterEntries(entries)).toEqual(entries);
            expect(filterEntries(entries, {exclude: ['webview/help']})).not.toEqual(entries);
        });

        it('should be return include entries', () => {
            const entries = {
                'webview/help': [],
                'webview/history': []
            };
            const expectedEntries = {
                'webview/history': []
            };

            expect(filterEntries(entries, {include: ['webview/history']})).toEqual(expectedEntries);
        });

        it('should be return entries without exclude', () => {
            const entries = {
                'webview/help': [],
                'webview/history': []
            };
            const expectedEntries = {
                'webview/history': []
            };

            expect(filterEntries(entries, {exclude: ['webview/help']})).toEqual(expectedEntries);
        });

        it('should be return include entries without exclude', () => {
            const entries = {
                'app/tariff': [],
                'webview/help': [],
                'webview/history': []
            };
            const expectedEntries = {
                'webview/history': []
            };

            expect(filterEntries(entries, {include: [/^webview/], exclude: ['webview/help']})).toEqual(expectedEntries);
        });
    });
});
