import React, {ReactNode} from 'react';

import {jsxStringReplace, replaceToJSXByTags} from '../replaceToJSX';

describe('jsxStringReplace tests', () => {
    test('jsxStringReplace do nothing with empty', () => {
        expect(jsxStringReplace('', '', () => null))
            .toStrictEqual([]);
    });

    test('jsxStringReplace have exception when give some trash', () => {
        const correctError = 'First argument must be a string';

        try {
            jsxStringReplace(123 as unknown as string, '', () => null);
        } catch (e) {
            expect(e.message).toBe(correctError);
        }

        try {
            jsxStringReplace({a: 123} as unknown as string, '', () => null);
        } catch (e) {
            expect(e.message).toBe(correctError);
        }

        try {
            jsxStringReplace(null as unknown as string, '', () => null);
        } catch (e) {
            expect(e.message).toBe(correctError);
        }

        try {
            jsxStringReplace(undefined as unknown as string, '', () => null);
        } catch (e) {
            expect(e.message).toBe(correctError);
        }

        try {
            // eslint-disable-next-line symbol-description
            jsxStringReplace(Symbol() as unknown as string, '', () => null);
        } catch (e) {
            expect(e.message).toBe(correctError);
        }
    });

    test('jsxStringReplace do nothing with string', () => {
        expect(jsxStringReplace('string', '_', () => null))
            .toStrictEqual(['string']);
    });

    test('jsxStringReplace handle source array', () => {
        expect(jsxStringReplace(['string', 'bla'], '_', () => null))
            .toStrictEqual(['string', 'bla']);
    });

    test('jsxStringReplace replace (string match) single jsx', () => {
        const result = jsxStringReplace(
            'string %delim% string2',
            '%delim%',
            _match => {
                return <span>hello</span>;
            },
        );

        expect(result).toStrictEqual([
            'string ',
            // eslint-disable-next-line react/jsx-key
            <span>hello</span>,
            ' string2',
        ]);

        expect(result[0]).toBe('string ');

        expect((result[1] as any).type).toBe('span');
        expect((result[1] as any).props.children)
            .toBe('hello');

        expect(result[2]).toBe(' string2');
    });

    test('jsxStringReplace replace (regexp match) multiple jsx', () => {
        const result = jsxStringReplace(
            'string %delim1% string2 %delim2% string3',
            /(%delim1%|%delim2%)/gim,
            match => {
                if (match === '%delim1%') {
                    return <span>:</span>;
                }

                if (match === '%delim2%') {
                    return <span>|</span>;
                }

                return null;
            },
        );

        expect(result).toStrictEqual([
            'string ',
            // eslint-disable-next-line react/jsx-key
            <span>:</span>,
            ' string2 ',
            // eslint-disable-next-line react/jsx-key
            <span>|</span>,
            ' string3',
        ]);
    });
});

describe('replaceToJSXByTags tests', () => {
    test('replaceToJSXByTags replace all in config', () => {
        const config: Record<string, ReactNode> = {
            '%br%': <p/>,
            '%hr%': <hr/>,
            '%div%': <div/>,
        };

        expect(replaceToJSXByTags('hello %br% %hr% %div%', config))
            .toStrictEqual(['hello ', config['%br%'], ' ', config['%hr%'], ' ', config['%div%'], '']);
    });

    test('replaceToJSXByTags replace all with default value', () => {
        const config: Record<string, ReactNode> = {
            '%hr%': <hr/>,
            '%div%': <div/>,
        };

        expect(replaceToJSXByTags('hello %br% %hr% %div%', config))
            // eslint-disable-next-line react/jsx-key
            .toStrictEqual(['hello ', <br/>, ' ', config['%hr%'], ' ', config['%div%'], '']);
    });

    test('replaceToJSXByTags replace all with just default value', () => {
        expect(replaceToJSXByTags('hello %br% %hr% %div%'))
            // eslint-disable-next-line react/jsx-key
            .toStrictEqual(['hello ', <br/>, ' %hr% %div%']);
    });
});
