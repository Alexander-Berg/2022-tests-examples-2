import {traverse, RootNode} from '../src/tree-traverse';
import chai from 'chai';

const expect = chai.expect;

describe('tree-traverse', function () {
    const tree: RootNode = {
        elements: [
            {
                type: 'element',
                name: 'a',
                elements: [
                    {
                        type: 'text',
                        text: 'b'
                    },
                    {
                        type: 'element',
                        name: 'c',
                        attributes: {
                            foo: 'bar',
                            elements: '123'
                        },
                        elements: [
                            {
                                type: 'text',
                                text: 'deep'
                            }
                        ]
                    }
                ]
            },
            {
                type: 'text',
                text: 'd'
            }
        ]
    };


    it('обходит элементы', () => {
        const str = [];
        traverse(tree, node => {
            const type = 'type' in node ? node.type : 'root',
                val = 'name' in node ? node.name : 'text' in node ? node.text : 'noval';
            str.push(`${type}:${val}`);
        }, {});
        expect(str).to.deep.equal([
            'root:noval',
            'element:a',
            'text:b',
            'element:c',
            'text:deep',
            'text:d'
        ]);
    });

    it('обходит не больше maxdepthв глубину 1', () => {
        const str = [];
        traverse(tree, node => {
            const type = 'type' in node ? node.type : 'root',
                val = 'name' in node ? node.name : 'text' in node ? node.text : 'noval';
            str.push(`${type}:${val}`);
        }, {maxdepth: 1});
        expect(str).to.deep.equal([
            'root:noval',
            'element:a',
            'text:d'
        ]);
    });
    it('обходит не больше maxdepthв глубину 2', () => {
        const str = [];
        traverse(tree, node => {
            const type = 'type' in node ? node.type : 'root',
                val = 'name' in node ? node.name : 'text' in node ? node.text : 'noval';
            str.push(`${type}:${val}`);
        }, {maxdepth: 2});
        expect(str).to.deep.equal([
            'root:noval',
            'element:a',
            'text:b',
            'element:c',
            'text:d'
        ]);
    });

    it('не обходит потомков узла с непустым ответом', () => {
        const str = [];
        traverse(tree, node => {
            const type = 'type' in node ? node.type : 'root',
                val = 'name' in node ? node.name : 'text' in node ? node.text : 'noval';
            str.push(`${type}:${val}`);

            if ('name' in node && node.name === 'c') {
                return true;
            }
        }, {});
        expect(str).to.deep.equal([
            'root:noval',
            'element:a',
            'text:b',
            'element:c',
            'text:d'
        ]);
    });
});