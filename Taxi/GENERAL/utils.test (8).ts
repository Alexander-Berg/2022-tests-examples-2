import {Render} from '@constructor/compiler-common';
import {componentDescriptionToNode} from './utils';

describe('componentDescriptionToNode', () => {
    test('full description', () => {
        const description: Render.ComponentDescription = {
            a: 1,
            '#b': '2',
            onC: () => null,
            'url.query.a': () => null,
            'url.query': () => null,
            $d: {},
        };

        const [node, children] = componentDescriptionToNode('$xxx', description);

        expect(node).toEqual({
            id: 'xxx',
            data: {
                a: 1,
                '#b': '2',
            },
            events: {
                'on-c': description.onC,
                'url.query.a': description['url.query.a'],
                'url.query': description['url.query'],
            },
        });

        expect(children).toEqual([['$d', description.$d]]);
    });

    test('custom component name', () => {
        const description: Render.ComponentDescription = {
            $$b: {},
            $c: {},
        };

        const [node, children] = componentDescriptionToNode('$$a', description);

        expect(node).toEqual({
            id: 'a',
            data: {},
        });

        expect(children).toEqual([
            ['$$b', description.$$b],
            ['$c', description.$c],
        ]);
    });
});
