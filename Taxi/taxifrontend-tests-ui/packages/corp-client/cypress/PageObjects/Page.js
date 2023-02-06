class Page {
    /**
     * Клик по кнопке с переданным названием
     * @param title
     * @returns {Page}
     */
    clickBtn(title) {
        cy.xpath(`//span[text()='${title}']`).click();
        return this;
    }
}

export default Page;
