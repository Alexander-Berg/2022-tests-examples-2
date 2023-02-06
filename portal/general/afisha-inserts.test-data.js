const mocks = require('./mocks');

const ajaxMocks = `<script>
    window.mocks = {
        cinemas: ${JSON.stringify(require('./mocks/ajax-cinemas.json'))},
        sessions: ${JSON.stringify(require('./mocks/ajax-sessions.json'))},
        concerts: ${JSON.stringify(require('./mocks/ajax-concerts.json'))}
    };

    var server = window.server = sinon.fakeServer.create();

    server.respondWith(/nogeoget/, JSON.stringify(window.mocks.cinemas));
    </script>`;

const style = `<style>
    .afisha-event-film__image.afisha-event-film__image_empty-type_0,
    .afisha-event-film__image.afisha-event-film__image_empty-type_1,
    .afisha-event-film__image.afisha-event-film__image_empty-type_2,
    .afisha-event-film__image.afisha-event-film__image_empty-type_3,
    .afisha-event-film__image.afisha-event-film__image_empty-type_4 {
        background-image: none;
        background: #faceff;
    }
    </style>`;

for (const theme of ['white', 'black']) {
    for (const mode of ['noauth', 'concerts']) {
        exports[`${theme}-${mode}`] = (execView, {documentMods}) => {
            documentMods.push('i-ua_browser_desktop');

            if (mode === 'concerts') {
                mocks.AfishaInserts.tabs = [{
                    id: 'concerts',
                    title: 'Концерты'
                }];
            } else {
                mocks.AfishaInserts.tabs = [];
            }


            return ajaxMocks +
                style +
                `<div class="outer" style="padding: 50px;width: 900px; background: ${theme === 'white' ? '#fff' : '#222229'}; font-size: 16px;">` +
                    '<div class="zen-insert-block">' +
                        execView('AfishaInserts__serverSide', {}, Object.assign({}, mocks, {
                            Logged: 0,
                            GeoID: 213,
                            Locale: 'ru',
                            Skin: theme === 'black' ? 'night' : undefined
                        })) +
                    '</div>' +
                '</div>' +
                "<script>$(function(){$('.afisha-inserts').bem('afisha-inserts');});</script>";
        };
    }
}
