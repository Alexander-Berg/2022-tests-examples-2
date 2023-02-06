export async function clearValue(element: any) {
    const oldValue = await (await element)?.getValue();

    if (oldValue) {
        const backspaces = new Array(oldValue.length).fill('Backspace');

        await element?.setValue(backspaces);
    }
}

export async function setValue(element: any, value: string) {
    await clearValue(element);
    await (await element)?.setValue(value);
}

export async function addValue(element: any, value: string) {
    await (await element)?.setValue(value);
}
