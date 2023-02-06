export function BlockInner() {
    return 'inner';
}

export function Block() {
    return (
        <>
            {'Hello '}
            <BlockInner />
        </>
    );
}

export function BlockSecond() {
    return 'second';
}

export function BlockSecondInner() {
    return 'inner2';
}

export { Block as block };
