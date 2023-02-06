import { execView } from '@lib/views/execView';
import { Block } from '@block/block/block.view';
import { Block2 } from '@block/block2/block2.view';
import { mockView, restoreViews } from '@lib/views/mock';

describe('block2', () => {
    beforeEach(() => {
        restoreViews();
    });

    test('simple', () => {
        expect(execView(Block2)).toEqual('Hello');
    });

    test('mocked', () => {
        mockView(Block2, () => 'HelloMocked');
        expect(execView(Block2)).toEqual('HelloMocked');
        restoreViews();
        expect(execView(Block2)).toEqual('Hello');
        mockView(Block, () => 'HelloMocked');
        expect(execView(Block2)).toEqual('HelloMocked');
    });
});
