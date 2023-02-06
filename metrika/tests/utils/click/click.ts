import { Browser } from 'hermione';

// Стандартный метод isEnabled проверяет только наличие disabled аттрибута. Но многие лего компоненты сделаны через aria-disabled
const customClick: Browser['customClick'] = function(
    this: Browser,
    selector?: string,
) {
    return this.click(selector).catch((error) => {
        if (error.message.includes('Other element would receive the click')) {
            if (selector) {
                return this.scroll(selector, 0, 200).click();
            }

            return this.scroll(0, 200).click();
        }

        throw error;
    });
};

const addCustomClick = (browser: Browser) => {
    browser.addCommand('customClick', customClick);
};

export { customClick, addCustomClick };
