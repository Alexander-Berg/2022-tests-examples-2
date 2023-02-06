exports.noTabs = execView => '<div class="outer" style="overflow:hidden"><style>.block{margin:0}}</style>' + execView('Afisha', {
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
