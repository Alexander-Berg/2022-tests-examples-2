import { sanitize } from '../sanitize';

describe('sanitize', () => {
    test('works as expected', () => {
        expect(sanitize('"+alert(\'document.domain+" param layoutType")+"'))
            .toEqual('&#34;+alert(&#39;document.domain+&#34; param layoutType&#34;)+&#34;');
    });
});
