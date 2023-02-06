import { expect } from 'chai';
import { Tree } from '../lib/tree';

describe('tree', () => {
    it('возвращает params', () => {
        const data = { a: 1, b: 2, path: 'q' };

        expect(new Tree(data).toArray())
            .to.deep.equal([data]);
    });

    it('создаёт узлы дерева', () => {
        const tree = new Tree({ a: 1 });

        tree.leaf('sub', { a: 2 });
        tree.leaf('sub2', { a: 3 }).leaf('subsub', { a: 4, b: 5 });

        expect(tree.toArray())
            .to.deep.equal([
                {
                    path: '\tsub\t',
                    a: 2,
                },
                {
                    path: '\tsub2\tsubsub\t',
                    a: 4,
                    b: 5,
                },
                {
                    path: '\tsub2\t',
                    a: 3,
                },
            ]);
    });
});
