const mock = require('./mocks/general');

const logged = {
    Logged: 1,
    AuthInfo: {
        avatar_id: '0/0-0'
    },
    UserName: {
        str: 'vasya'
    }
};

module.exports.logout = execView => '<div class="body__wrapper"><div class="content"></div></div>' + execView('Menu2', Object.assign({},
    mock
));

module.exports.logged = execView => '<div class="body__wrapper"><div class="content"></div></div>' + execView('Menu2', Object.assign({},
    mock,
    logged
));
