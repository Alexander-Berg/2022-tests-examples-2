import {makeDataTestIdSelector} from 'tests/e2e/utils/make-data-test-id-selector';

type RestoreCSS = {value: null | string; priority: string | undefined};

/**
 * @function
 * @description Копирует файл в контейнер с chromium, находит элемент, и загружает в него этот файл
 * @param selector
 * @param pathToFile
 */
export async function uploadFileInto(
    this: WebdriverIO.Browser,
    selector: Hermione.GenericSelector,
    pathToFile: string
) {
    const input = await this.assertBySelector(selector);

    const restoreCss = await this.execute((input) => {
        const restore: RestoreCSS = {value: null, priority: undefined};

        if (input instanceof HTMLElement) {
            restore.value = input.style.getPropertyValue('display');
            restore.priority = input.style.getPropertyPriority('display');
            input.style.setProperty('display', 'block', 'important');
        }

        return restore;
    }, input);

    await input.waitForDisplayed();

    const remotePath = await this.uploadFile(pathToFile);
    await input.setValue(remotePath);

    await this.execute(
        (selector: string, restoreCss: RestoreCSS) => {
            const input = document.querySelector(selector);

            if (input instanceof HTMLElement) {
                input.style.setProperty('display', restoreCss.value, restoreCss.priority);
            }
        },
        makeDataTestIdSelector(selector),
        restoreCss
    );
}

export type UploadFileInto = typeof uploadFileInto;
