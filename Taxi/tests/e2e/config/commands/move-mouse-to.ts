type MoveToOptions = Exclude<Parameters<WebdriverIO.Element['moveTo']>[0], undefined>;

export type MoveMouseToOptions = Partial<MoveToOptions>;

/**
 * @function
 * @description Находит элемент по data-testid селектору и наводит курсор на него
 */
export async function moveMouseTo(
    this: WebdriverIO.Browser,
    selector: Hermione.GenericSelector,
    options?: MoveMouseToOptions
) {
    const element = await this.assertBySelector(selector);

    await element.moveTo(options);
}

export type MoveMouseTo = typeof moveMouseTo;
