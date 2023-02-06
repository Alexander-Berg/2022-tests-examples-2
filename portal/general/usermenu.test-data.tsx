import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
/* eslint-disable @typescript-eslint/ban-ts-comment */
// @ts-ignore
import { Usermenu__resources } from './usermenu.view';

export function simple() {
    const settingsJs = home.settingsJs([]);
    const req = mockReq({}, {
        settingsJs,
        Mail: {
            show: 1,
            Logged: 1,
            count: 123,
            auth_host: 'passport.yandex.ru',
            visible: 1,
            users: [{
                default: 1,
                uid: '1',
                UserName: {
                    f: 'V',
                    l: 'asya',
                    str: 'Vasya'
                },
                email: 'vasya@yandex.ru',
                avatar_id: '0/0-0'
            }]
        },
        AuthInfo: {
            allow_more_users: '1'
        },
        Passport: {
            host: 'passport.yandex.com.tr',
            path: 'passport.yandex.com.tr/passport',
            register_url: 'https://passport.yandex.com.tr/registration?mode=register&retpath=https%3A%2F%2Fmail.yandex.com.tr&origin=passport_auth2reg&mda=0',
            social_host: 'social.yandex.com.tr',
            url: 'https://passport.yandex.com.tr/passport?mda=0'
        },
        HomePageNoArgs: 'https://yandex.com.tr',
        MordaZone: 'com.tr',
        MordaContent: 'spok',
        Yandexuid: '1234',
        JSON: {
            common: {
                pageName: 'spok'
            }
        }
    });

    execView(Usermenu__resources, {}, req);

    return `<style>body{
        background:#000;
        font: 16px sans-serif;
    }

    :link {
        text-decoration: none;
    }
    </style>
<div class="dialog__list"></div>
<script>
${settingsJs.getRawScript(req)}

$(function() {
    setTimeout(function() {
        MBEM.blocks.usermenu.show();
    }, 100);
});
</script>`;
}
