async function clearValue(element: ReturnType<typeof $>) {
    const oldValue = await element.getValue();

    if (oldValue) {
        const backspaces = new Array(oldValue.length).fill('Backspace');

        await element.setValue(backspaces);
    }
}

export async function setValue(element: ReturnType<typeof $>, value: string) {
    await clearValue(element);
    await element.setValue(value);
}
