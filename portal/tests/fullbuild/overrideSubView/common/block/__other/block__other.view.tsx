export function BlockOther2() {
    return 'other2';
}

export function BlockOther() {
    return (
        <>
            {'other+'}
            <BlockOther2 />
        </>
    );
}
