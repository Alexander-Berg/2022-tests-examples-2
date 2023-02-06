'use strict';

specs('zen', function () {
    it.skip('Отправляется realshow', async function() {
        await this.browser.yaOpenMorda({getParams: {
            ab_flags: [
                'filter_blocks_big'
            ].join(':')
        }});

        await this.browser.$('.zen-lib_state_loaded').then(elem => elem.waitForDisplayed());

        await this.browser.yaInBrowser(() => {
            // eslint-disable-next-line no-async-promise-executor
            return new Promise(async (resolve, reject) => {
                let row,
                    rowLayoutName;

                document.body.style.overflow = 'initial';

                home.stat.logPath = function (type, counter) {
                    if (type === 'show' && counter === `${rowLayoutName}.realshow`) {
                        resolve();
                    }
                };
                let scroll = window.scrollY;
                do {
                    row = $('.media-grid__row:not([data-blockname=infinity_zen]):last');

                    if (!row.length) {
                        scroll += window.innerHeight * 0.8;
                        window.scrollTo(0, scroll);
                        await new Promise(resolve => setTimeout(resolve, 100));
                    }
                } while (!row.length && scroll < window.innerHeight * 10);

                if (!row.length) {
                    return reject(new Error(`не нашлось ни одной вставки при скролле до ${scroll}`));
                }

                const TIMEOUT = 15000;
                rowLayoutName = row.attr('data-blockname');
                scrollTo(0, row.offset().top);
                setTimeout(() => reject(new Error(`realshow блока ${rowLayoutName} не отправлен за ${TIMEOUT}мс`)), TIMEOUT);
            });
        });
    });
});
