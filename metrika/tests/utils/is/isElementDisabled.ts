import { Browser } from 'hermione';

// Стандартный метод isEnabled проверяет только наличие disabled аттрибута. Но многие лего компоненты сделаны через aria-disabled
const customIsElementDisabled: Browser['customIsElementDisabled'] = function(
    this: Browser,
    selector?: string,
) {
    return this.element(selector!)
        .then((res) => {
            const elementId = res.value.ELEMENT;
            return this.elementIdAttribute(elementId, 'aria-disabled');
        })
        .then((res) => {
            const isDisabled = res.value === 'true';

            if (isDisabled) {
                return true;
            }

            return false;
        });
};

export { customIsElementDisabled };
