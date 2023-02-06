import {parse as parseHtml} from './parser';

describe('parser', () => {
    it('should lex', () => {
        const code = `<html>
        <!-- [% ignore %]-->
            [% expression %]
        </html>`;
        const ast = parseHtml(code, {filePath: 'test.html'});
        expect(ast).toMatchSnapshot();
    });
});
