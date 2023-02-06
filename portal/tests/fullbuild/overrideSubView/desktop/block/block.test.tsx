import { execView } from '@lib/views/execView';
import { Block, BlockInner } from '@block/block/block.view';
import { mockView, restoreViews } from '@lib/views/mock';

describe('block', () => {
    beforeEach(() => {
        restoreViews();
    });

    test('simple', () => {
        expect(execView(Block)).toEqual('Hello inner desktop other+other2_desktop');
    });

    test('mocked', () => {
        mockView(BlockInner, () => 'hello mocked');
        expect(execView(Block)).toEqual('Hello hello mocked other+other2_desktop');
        restoreViews();
        expect(execView(Block)).toEqual('Hello inner desktop other+other2_desktop');
    });
});
