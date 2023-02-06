import { execView } from '@lib/views/execView';
import { Block, BlockInner } from '@block/block/block.view';
import { mockView, restoreViews } from '@lib/views/mock';

describe('block', () => {
    beforeEach(() => {
        restoreViews();
    });

    test('simple', () => {
        expect(execView(Block)).toEqual('Hello inner');
        expect(execView('oldBlock')).toEqual('<div class="oldBlock">Hello inner</div>');
    });

    test('mocked', () => {
        mockView(BlockInner, () => 'Mocked');
        expect(execView(Block)).toEqual('Hello Mocked');
        expect(execView('oldBlock')).toEqual('<div class="oldBlock">Hello Mocked</div>');
        restoreViews();
        expect(execView('oldBlock')).toEqual('<div class="oldBlock">Hello inner</div>');
        mockView('oldBlock__layout', (data: {content: string}) => 'mocked ' + data.content);
        expect(execView('oldBlock')).toEqual('mocked Hello inner');
    });
});
