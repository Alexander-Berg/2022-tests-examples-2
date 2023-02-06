import { execView } from '@lib/views/execView';
import { Block, BlockInner } from '@block/block/block.view';
import { mockView, restoreViews } from '@lib/views/mock';

describe('block', () => {
    beforeEach(() => {
        restoreViews();
    });

    test('simple', () => {
        expect(execView(Block)).toEqual('Hello inner other+other2');
    });

    test('mocked', () => {
        mockView(Block, () => 'HelloMocked');
        expect(execView(Block)).toEqual('HelloMocked');
        restoreViews();
        expect(execView(Block)).toEqual('Hello inner other+other2');
        mockView(BlockInner, () => 'inner mocked');
        expect(execView(Block)).toEqual('Hello inner mocked other+other2');
    });
});
