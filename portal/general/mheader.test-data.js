const noAuth = {
    BigCityName: 'МоскваМоскваМоскваМоскваМоскваМоскваМосква',
    Logged: 0,
    Mail: {
        show: 1
    },
    Passport: {
        host: 'passport.yandex.ru'
    },
    MordaZone: 'ru'
};

const logged = {
    MordaZone: 'ru',
    Requestid: '1.1.1.1',
    BigCityName: 'МоскваМоскваМоскваМоскваМоскваМоскваМоскваМосква',
    Logged: 1,
    AuthInfo: {
        avatar_id: '0/0-0'
    },
    Bell: {
        show: 1
    },
    Passport: {
        host: 'passport.yandex.ru'
    }
};

const plus = {
    Plus: {
        show: 1,
        is_active: 1
    }
};

exports.logout = execView => execView('Mheader', noAuth);

exports.logged = execView => execView('Mheader', logged);

exports.loggedPlus = execView => execView('Mheader', {...logged, ...plus});
