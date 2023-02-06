exports.noTabs = execView => '<div class="outer" style="overflow:hidden"><style>.block{margin:0}}</style>' + execView('Afisha2', {
    Afisha: {
        show: 1,
        events: [{
            href: '//ya.ru',
            full: 'Союз Спасения',
            genre: 'история'
        }, {
            href: '//ya.ru',
            full: 'Звёздные Войны: Скайуокер. Восход',
            genre: 'фантастика',
            premiere_badge: 'премьера в чт'
        }, {
            href: '//ya.ru',
            full: 'Фиксики против кработов',
            genre: 'приключения',
            premiere_badge: 'премьера завтра'
        }]
    }
}) + '</div>';

exports.withTabs = execView => '<div class="outer" style="overflow:hidden"><style>.block{margin:0}}</style>' + execView('Script', {
    content: `
        window.server = sinon.fakeServer.create();

        window.server.respondWith(/portal\\/api\\/data/, JSON.stringify(${JSON.stringify(require('./mocks/concerts.json'))}));
    `
}) + execView('Afisha2', {
    Afisha: {
        show: 1,
        events: [{
            href: '//ya.ru',
            full: 'Союз Спасения',
            genre: 'история'
        }, {
            href: '//ya.ru',
            full: 'Звёздные Войны: Скайуокер. Восход',
            genre: 'фантастика'
        }, {
            href: '//ya.ru',
            full: 'Фиксики против кработов',
            genre: 'приключения'
        }],
        tabs: [{
            'id': 'concerts',
            'title': ''
        }, {
            'id': 'theatres',
            'title': ''
        }, {
            'id': 'sport',
            'title': ''
        }, {
            'id': 'kids',
            'title': 'Детям'
        }]
    }
}) + '</div>';
