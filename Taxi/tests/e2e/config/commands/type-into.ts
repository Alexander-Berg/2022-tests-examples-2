type Options = Partial<{
    clear?: boolean;
    blur?: boolean;
}>;

/**
 * @function
 * @description Находит элемент по data-testid селекторам и печатает в него текст
 */
export async function typeInto(
    this: WebdriverIO.Browser,
    selector: Hermione.GenericSelector,
    textToType: string,
    options?: Options
) {
    const {clear, blur} = options || {};
    const input = await this.assertBySelector(selector);

    if (clear) {
        await input.click();
        await this.keys(['Control', 'a']);
        await this.keys('Delete');
        await input.setValue(textToType);
    } else {
        await input.addValue(textToType);
    }

    if (blur) {
        await this.$('body').click();
    }
}

export type TypeInto = typeof typeInto;
