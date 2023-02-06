import { Page } from '../Page';
import { helpSelectors } from 'shared/testIds';

class DatePicker extends Page {
    get button() {
        return this.browser.$(helpSelectors.datePicker.button);
    }

    get popup() {
        return this.browser.$(helpSelectors.datePicker.popup);
    }

    get confirmButton() {
        return this.browser.$(helpSelectors.datePicker.select);
    }

    clickDay(day: number) {
        return this.browser
            .$(`${helpSelectors.datePicker.day}[aria-label="day-${day}"]`)
            .click();
    }

    async selectPeriod(from: number, to: number) {
        await this.open();
        await this.clickDay(from);
        await this.clickDay(to);

        return this.confirmSelect();
    }

    async confirmSelect() {
        await this.confirmButton.click();
        return this.popup.customWaitForExist({ reverse: true });
    }

    async open() {
        await this.button.click();
        await this.popup.customWaitForExist();
        return this.browser.pause(200);
    }
}

export { DatePicker };
