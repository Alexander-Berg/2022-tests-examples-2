import {lex} from './lexer';

describe('lexer', () => {
    it('should lex', () => {
        const code = `<html>
        <!-- [% ignore %]-->
            [% expression %]
        </html>`;
        const tokens = [...lex(code, 'test.html')];
        expect(tokens.length).toBe(1);
        expect(tokens).toMatchSnapshot();
    });

    it('should lex', () => {
        const code = `<html>
            <[% expression %]>
        </html>`;
        const tokens = [...lex(code, 'test.html')];
        expect(tokens.length).toBe(1);
        expect(tokens).toMatchSnapshot();
    });
});
