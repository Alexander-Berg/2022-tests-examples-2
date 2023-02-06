import { BlockOther } from '@block/block/__other/block__other.view';

export function BlockInner() {
    return 'inner';
}

export function Block() {
    return (
        <>
            {'Hello '}
            <BlockInner />
            {' '}
            <BlockOther />
        </>
    );
}
