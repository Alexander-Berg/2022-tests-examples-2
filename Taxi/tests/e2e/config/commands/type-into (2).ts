type Options = Partial<{
    clear?: boolean;
    blur?: boolean;
}>;

/**
 * @function
 * @description Находит элемент по data-testid селекторам и печатает в него текст
 */
export default async function typeInto(
    this: WebdriverIO.Browser,
    selector: Hermione.Selector,
    textToType: string,
    options?: Options
) {
    const {clear, blur} = options || {};
    const input = await this.findByTestId(selector);

    if (clear) {
        await input.click();
        await this.keys(['Control', 'a']);
        await this.keys('Delete');
        await input.setValue(textToType);
    } else {
        await input.addValue(textToType);
    }

    if (blur) {
        await this.executeScript('arguments[0].blur()', [input]);
    }
}

export type TypeInto = typeof typeInto;
