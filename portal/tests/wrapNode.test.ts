import wrapNode from '../wrapNode';

describe('wrapNode', () => {
    test('test', () => {
        const node0 = document.createElement('div');
        const node1 = document.createElement('div');
        const parent = document.createElement('div');
        parent.appendChild(node0);
        parent.appendChild(node1);

        expect(wrapNode(node0)).toEqual([node0]);
        expect(wrapNode([node0, node1])).toEqual([node0, node1]);
        expect(wrapNode(parent.querySelectorAll('*'))).toEqual([node0, node1]);
    });
});
