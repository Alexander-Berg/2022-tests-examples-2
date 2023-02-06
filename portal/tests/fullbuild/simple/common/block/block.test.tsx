import { execView } from '@lib/views/execView';
import { Block } from '@block/block/block.view';
import { mockView, restoreViews } from '@lib/views/mock';

describe('block', () => {
    beforeEach(() => {
        restoreViews();
    });

    test('simple', () => {
        expect(execView(Block)).toEqual('Hello');
    });

    test('mocked', () => {
        mockView(Block, () => 'HelloMocked');
        expect(execView(Block)).toEqual('HelloMocked');
        restoreViews();
        expect(execView(Block)).toEqual('Hello');
    });
});
