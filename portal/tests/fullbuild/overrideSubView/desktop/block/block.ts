import { execView } from '@lib/views/execView';
import { Block, BlockInner } from '@block/block/block.view';

export function run() {
    return execView(Block);
}

export function runInner() {
    return execView(BlockInner);
}
