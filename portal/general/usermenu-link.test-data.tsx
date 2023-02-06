import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';

import singleMock from './mocks/single.json';
import multipleMock from './mocks/multiple.json';
import manyMock from './mocks/many.json';
import messengerMock from './mocks/messenger.json';

const messengerFullMock = {
    ...singleMock,
    ...messengerMock
};

function unreadMock(unread?: number) {
    if (!unread) {
        return '';
    }

    return `<script>
        var server = window.server = sinon.fakeServer.create();

        server.respondImmediately = true;

        server.respondWith(/unread/, JSON.stringify({
            UnreadCount: ${unread}
        }));
    </script>`;
}

function handle(mock: Partial<Req3Server>, opts: {
    unread?: number;
} = {}) {
    let settingsJs = home.settingsJs([]);

    let req = mockReq({}, {
        ...mock,
        settingsJs
    });

    settingsJs.add('req.MordaZone', 'ru', 'common');
    if (opts.unread) {
        settingsJs.add('data', { unreadUrl: '/unread' }, 'i-messenger-unread');
    }

    return {
        htmlMix: 'i-ua_browser_desktop',
        html: execView('usermenu-link__data', {}, req) + '<div class="usermenu-link i-bem usermenu-link__control"' +
            'data-bem="{&quot;usermenu-link&quot;:{&quot;popup&quot;: { &quot;mainOffset&quot;: -35, &quot;secondaryOffset&quot;: 25}}}" ' +
            'style="display: inline-block; margin-top: 40px; padding: 20px; width: 300px;">Link</div>' +
            '<style>' +
            '.usermenu__user-icon_type_default .avatar__image{background: rgba(0,0,0,0.15) !important;}' +
            '.usermenu__user-icon_type_custom .avatar__image{background: #4eb0da !important;}' +
            '</style>' +
            `<script>${settingsJs.getRawScript(req)}</script>` +
            unreadMock(opts.unread)
    };
}

export function single() {
    return handle(singleMock);
}

export function multiple() {
    return handle(multipleMock);
}

export function many() {
    return handle(manyMock);
}

export function messenger() {
    return handle(messengerFullMock);
}

export function messengerUnreadOne() {
    return handle(messengerFullMock, {
        unread: 1
    });
}

export function messengerUnreadMany() {
    return handle(messengerFullMock, {
        unread: 999
    });
}
