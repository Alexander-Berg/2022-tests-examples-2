module.exports = {
    block: 'page',
    title: 'CSP tester',
    favicon: '/favicon.ico',
    head: [
        { elem: 'meta', attrs: { name: 'description', content: 'Test your CSP for errors online' } },
        { elem: 'meta', attrs: { name: 'viewport', content: 'width=device-width, initial-scale=1' } },
        { elem: 'css', url: 'index.min.css' }
    ],
    scripts: [{ elem: 'js', url: 'index.min.js', i18n: true }],
    mods: { theme: 'islands' },
    content: [
        {
            block: 'ng-head',
            service: {
                id: 'csp',
                name: 'CSP tester'
            },
            left: {
                block: 'ng-headmenu',
                content: [
                    {
                        elem: 'item',
                        url: 'https://wiki.yandex-team.ru/product-security/csp/',
                        text: 'Узнать больше о внедрении CSP и рекомендациях по составлению политики'
                    }
                ]
            },
            right: [
                // {
                //     block: 'ng-head-user',
                //     uid: 1,
                //     login: 'tadatuta',
                //     avatar: '//center.yandex-team.ru/api/v1/user/tadatuta/avatar/50.jpg'
                // }
            ]
        },
        {
            block: 'main',
            content: [
                {
                    block: 'form',
                    method: 'post',
                    mix: { block: 'test-form', js: true },
                    content: [
                        {
                            elem: 'control',
                            content: [
                                {
                                    block: 'textarea',
                                    mods: { theme: 'islands', size: 'm', width: 'available' },
                                    name: 'policy',
                                    placeholder: 'Введите сюда вашу CSP политику или URL для её получения через заголовок'
                                }
                            ]
                        },
                        {
                            block: 'button',
                            mods: { theme: 'islands', size: 'm', type: 'submit', view: 'action', disabled: true },
                            text: 'Проверить'
                        }
                    ]
                },
                {
                    block: 'result',
                    content: [
                        {
                            elem: 'valid',
                            content: {
                                block: 'heading',
                                mods: { level: 1 },
                                content: 'Ошибок не обнаружено'
                            }
                        },
                        {
                            elem: 'invalid'
                        },
                        {
                            elem: 'content'
                        }
                    ]
                }
            ]
        },
        {
            block: 'ng-foot',
            content: [
                {
                    block: 'link',
                    mods: { theme: 'islands' },
                    mix: { block: 'ng-foot', elem: 'nda' },
                    url: 'https://wiki.yandex-team.ru/product-security/csp/tester/#feedback',
                    content: 'Обратная связь'
                },
                {
                    block: 'link',
                    mods: { theme: 'islands' },
                    mix: { block: 'ng-foot', elem: 'nda' },
                    url: 'https://wiki.yandex-team.ru/hr/nda/',
                    content: 'Конфиденциально'
                },
                {
                    elem: 'copyright',
                    content: '© ' + new Date().getFullYear() + ' ООО «Яндекс»'
                }
            ]
        }
    ]
};
