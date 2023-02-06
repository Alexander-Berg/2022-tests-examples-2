/* eslint-disable @typescript-eslint/ban-ts-comment */

import { execView } from '@lib/views/execView';
// @ts-ignore
import { BlockOuter } from '@block/block/block.view';

export function run() {
    return execView(BlockOuter);
}
