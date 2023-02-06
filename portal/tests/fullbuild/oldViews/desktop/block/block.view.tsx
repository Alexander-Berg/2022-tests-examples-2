import { BlockSecond as BlockSecondBase, BlockInner as BlockInnerBase, BlockSecondInner as BlockSecondInnerBase } from '@blockBase/block/block.view';

export function BlockInner() {
    return (
        <>
            <BlockInnerBase />
            {' desktop'}
        </>
    );
}

export function BlockSecond(data: UnusedData, req: Req3, execView: ExecViewCompat) {
    return execView(BlockSecondBase) + ' ' + execView(BlockSecondInnerBase);
}

export * from '@blockBase/block/block.view';
