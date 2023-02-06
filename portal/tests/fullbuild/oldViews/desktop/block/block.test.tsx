import { execView } from '@lib/views/execView';
import { Block } from '@block/block/block.view';
import { mockView, restoreViews } from '@lib/views/mock';

describe('block', () => {
    beforeEach(() => {
        restoreViews();
    });

    test('simple', () => {
        expect(execView(Block)).toEqual('Hello inner desktop');
        expect(execView('oldBlock')).toEqual('oldBlock overriden <div class="oldBlock_desktop">Hello inner desktop</div>');
    });

    test('mocked', () => {
        mockView('block', () => 'HelloMocked');
        expect(execView('oldBlock')).toEqual('oldBlock overriden <div class="oldBlock_desktop">HelloMocked</div>');
        restoreViews();
        expect(execView('oldBlock')).toEqual('oldBlock overriden <div class="oldBlock_desktop">Hello inner desktop</div>');
        mockView('oldBlock__layout', (data: {content: string}) => 'mocked ' + data.content);
        expect(execView('oldBlock')).toEqual('oldBlock overriden mocked Hello inner desktop');
    });
});
