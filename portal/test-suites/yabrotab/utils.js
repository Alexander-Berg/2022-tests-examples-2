'use strict';

function setWidth (width, cols, ratio) {
    var page = document.querySelector('.b-page'),
        pageStyle = page.style,
        GAP = 8;

    const oneItem = (width - (cols - 1) * GAP) / cols,
        wide = cols > 4;

    page.classList.toggle('b-page_width_wide', wide);
    page.classList.toggle('b-page_width_normal', !wide);
    pageStyle.setProperty('--page-width', `${width}px`);
    pageStyle.setProperty('--item-ratio', ratio);
    pageStyle.setProperty('--item-width', `${oneItem}px`);
    pageStyle.setProperty('--cols-count', cols);
    if (window.broZen) {
        window.broZen.setWidth(+width);
    }
}

async function waitForPageReady() {
    await this.browser.yaInBrowser(async () => {
        await new Promise(resolve => {
            if (document.readyState === 'complete') {
                return resolve();
            }
            window.addEventListener('load', resolve);
        });

        await new Promise(resolve => {
            if (window.pageStatus.visible) {
                return resolve();
            }
            window.pageStatus.addEventListener('page-visible-changed', resolve);
        });
    });

    await this.browser.$("[class*='b-page_scrollable']").then(elem => elem.waitForExist({
        timeout: 5000
    }));
}

async function isBlocksRefreshedAfter(commands) {
    const TIMEOUT = 5000;
    const startTs = await this.browser.yaInBrowser(function getStartTs() {
        return document.querySelector('.main').dataset.ts;
    });

    try {
        await commands.call(this);
    } catch (e) {
        e.message = `isBlocksRefreshedAfter: ошибка при выполнении комманд: ${e.message}`;
    }
    await this.browser
        .yaInBrowser(function checkEndTs(startTs, TIMEOUT) {
            const ts = document.querySelector('.main').dataset.ts;

            if (ts === startTs) {
                return;
            }

            return new Promise((resolve, reject) => {
                const observer = new MutationObserver(list => list.map(onMutationItem));

                function onMutationItem(item) {
                    if (item.addedNodes && Array.prototype.some.call(item.addedNodes, node => node.closest('.main'))) {
                        const endTs = document.querySelector('.main').dataset.ts;

                        if (endTs !== startTs) {
                            observer.disconnect();
                            resolve();
                        }
                    }
                }

                setTimeout(() => {
                    observer.disconnect();
                    reject(new Error(`Блоки не обновлись за ${TIMEOUT}мс`));
                }, TIMEOUT);

                observer.observe(document.querySelector('.main').parentNode, {childList: true});
            });
        }, startTs, TIMEOUT);

}

async function isBlocksNotRefreshed() {
    const TIMEOUT = 5000;
    const {error} = await this.browser
        .executeAsync(function getTimestaps(TIMEOUT, done) {
            const observer = new MutationObserver(list => list.map(onMutationItem));

            function onMutationItem(item) {
                if (item.addedNodes && Array.prototype.some.call(item.addedNodes, node => node.closest('.main'))) {
                    observer.disconnect();
                    done({
                        error: 'Начался рефреш'
                    });
                }
            }
            setTimeout(() => {
                observer.disconnect();
                done({});
            }, TIMEOUT);

            observer.observe(document.querySelector('.main').parentNode, {childList: true});
        }, TIMEOUT);

    if (error) {
        throw new Error(error);
    }
}

module.exports = {
    setWidth,
    waitForPageReady,
    isBlocksRefreshedAfter,
    isBlocksNotRefreshed,
    ignore: [
        '.news',
        '.weather2',
        '.traffic',
        '.feed'
    ],
    hide: [
        '.dev-panel',
        '.panel-item',
        '.zen-app__logo',
        '.banner',
        // Новости могут быть двустрочными, растягивая контент
        '.list__item'
    ]
};
