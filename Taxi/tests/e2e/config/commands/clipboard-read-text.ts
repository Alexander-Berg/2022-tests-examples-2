export default async function clipboardReadText(this: WebdriverIO.Browser) {
    const elementId = 'clipboard-read-text-textarea';

    await this.execute((elementId) => {
        const textArea = document.createElement('textarea');
        textArea.id = elementId;
        textArea.style.top = '0';
        textArea.style.left = '0';
        textArea.style.position = 'fixed';
        textArea.style.zIndex = '50000';
        document.body.appendChild(textArea);
    }, elementId);

    const input = await this.$(`#${elementId}`);
    await input.click();
    await this.keys(['Control', 'v']);
    const value = await input.getValue();

    await this.execute((input) => {
        if (input instanceof HTMLElement) {
            input.remove();
        }
    }, input);

    return value;
}
