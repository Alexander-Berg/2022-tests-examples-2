import { Block2 } from '@block/block2/block2.view';
import { Block3 } from '@block/block3/block3.view';

export function Block(data: UnusedData, req: Req3) {
    if (req.isClient) {
        return <Block2 />;
    }
    return <Block3 />;
}

export function Block__inner(data: UnusedData, req: Req3, execView: ExecViewCompat): string {
    return 'Unused code' + execView(Block__inner2);
}
Block__inner.isCached = true;

export function Block__inner2(data: UnusedData, req: Req3, execView: ExecViewCompat): string {
    return 'Unused code2' + execView(Block__inner);
}
Block__inner2.isCached = true;
