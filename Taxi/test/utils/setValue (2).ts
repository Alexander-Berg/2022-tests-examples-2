
async function clearValue(element: any) {
    const oldValue = await element?.getValue();

    if (oldValue) {
        const backspaces = new Array(oldValue.length).fill('Backspace');

        await element?.setValue(backspaces);
    }
}

export async function setValue(element: any, value: string) {
    await clearValue(element);
    await element?.setValue(value);
}
