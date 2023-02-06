import { execView } from '@lib/views/execView';
import { Block } from '@block/block/block.view';

export function run() {
    return execView(Block);
}
