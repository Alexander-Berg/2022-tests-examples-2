const mock = require('./mocks/index');

exports.simple = execView => execView('News', mock);

exports.promo = execView => execView('News', {
    Topnews: {
        ...mock.Topnews,
        'promohref': 'http://news.yandex.ua/east.html',
        'promotext': 'Оранжевое небо, оранжевая новость'
    }
});
