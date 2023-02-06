import {BasePage} from './base.page';

class MenuPage extends BasePage {
    public async findDomain(domain: string) {
        const element = await $(`//strong[contains(.,\'${domain}\')]`);

        return element.getText();
    }
}

export const menuPage = new MenuPage();
