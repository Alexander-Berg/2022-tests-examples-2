import React from 'react';

import {applyPlaceholder} from './utils';

describe('applyPlaceholder', () => {
    test('string values key invariant', () => {
        let res = applyPlaceholder('xxx %key1% yyy %key2%', {
            key2: 'aaa',
            key1: 'bbb',
        });

        expect(res).toBe('xxx bbb yyy aaa');

        res = applyPlaceholder('xxx %key1% yyy %key2%', {
            key1: 'bbb',
            key2: 'aaa',
        });

        expect(res).toBe('xxx bbb yyy aaa');
    });

    test('jsx values key invariant', () => {
        let res = applyPlaceholder('xxx %key1% yyy %key2%', {
            key1: <div key="1">bbb</div>,
            key2: <div key="2">aaa</div>,
        }) as React.ReactElement;

        let children = Array.from(res.props.children);
        expect(children.length).toBe(4);
        expect(children[0]).toBe('xxx ');
        expect((children[1] as React.ReactElement).key).toBe('1');
        expect(children[2]).toBe(' yyy ');
        expect((children[3] as React.ReactElement).key).toBe('2');

        res = applyPlaceholder('xxx %key1% yyy %key2%', {
            key2: <div key="2">aaa</div>,
            key1: <div key="1">bbb</div>,
        }) as React.ReactElement;

        children = Array.from(res.props.children);
        expect(children[0]).toBe('xxx ');
        expect((children[1] as React.ReactElement).key).toBe('1');
        expect(children[2]).toBe(' yyy ');
        expect((children[3] as React.ReactElement).key).toBe('2');
    });

    test('mixed values', () => {
        const res = applyPlaceholder('xxx %key3% %key1% yyy %key2% %key4%', {
            key4: 'aaa',
            key2: <div key="2">aaa</div>,
            key1: <div key="1">bbb</div>,
            key3: 'bbb',
        }) as React.ReactElement;

        const children = Array.from(res.props.children);
        expect(children[0]).toBe('xxx bbb ');
        expect((children[1] as React.ReactElement).key).toBe('1');
        expect(children[2]).toBe(' yyy ');
        expect((children[3] as React.ReactElement).key).toBe('2');
        expect(children[4]).toBe(' aaa');
    });
});
