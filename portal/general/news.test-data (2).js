const mock = require('./mocks/index');
const toggleAndMoreMock = require('./mocks/toggle');
const officialCommentsMock = require('./mocks/officialComments');
const summaryMock = require('./mocks/summary');
const degradationMock = require('./mocks/degradation');


const news = (req, params) =>
    execView =>
        ((params && params.before) || '') + execView.withReq('News', {}, req);

const disclaimer = {
    promo: {
        close_url: 'https://yabs.yandex.ru/count/1111111/1111111',
        show_url: 'https://yabs.yandex.ru/count/11111111/1111111',
        text: 'Жёлтой точкой отмечены источники, которые вы добавили в избранное',
        url: 'https://yandex.ru/news#setting'
    }
};

const promo = {
    promohref: 'http://news.yandex.ua/east.html',
    promotext: 'Оранжевое небо, оранжевая новость'
};

exports.toggleAndMore = news({
    ...toggleAndMoreMock
});

exports.officialComments = news({
    ...officialCommentsMock
});

exports.summary = news({
    ...summaryMock
});

exports.promo = news({
    ...mock,
    Topnews: {
        ...mock.Topnews,
        ...mock.blocks_layout_ext,
        ...promo
    }
});

exports.promoDark = news({
    ...mock,
    Skin: 'night',
    blocks_layout_ext: mock.blocks_layout_ext,
    Topnews: {
        ...mock.Topnews,
        ...promo
    }
});

exports.disclaimer = news({
    blocks_layout_ext: mock.blocks_layout_ext,
    Topnews: {
        ...mock.Topnews,
        ...disclaimer
    }
});

exports.disclaimerCustomIcon = news({
    blocks_layout_ext: mock.blocks_layout_ext,
    Topnews: {
        ...mock.Topnews,
        promo: {
            ...disclaimer.promo,
            icon: 'https://yastatic.net/s3/home/icons/news/dot.svg'
        }
    }
});

exports.disclaimerDark = news({
    Skin: 'night',
    blocks_layout_ext: mock.blocks_layout_ext,
    Topnews: {
        ...mock.Topnews,
        ...disclaimer
    }
});

exports.personal = news(mock, {
    before: `<script>
        var server = window.server = sinon.fakeServer.create();

        server.respondImmediately = true;

        server.respondWith(
            /https:\\/\\/news.yandex.ru\\/api\\/v2\\/rubric/,
            [200, {'Content-Type': 'application/json'}, JSON.stringify(${JSON.stringify(require('./mocks/personal.json'))})]
        );
    </script>`
});

exports.personalFallback = news(mock, {
    before: `<script>
        var server = window.server = sinon.fakeServer.create();

        server.respondImmediately = true;

        server.respondWith(/https:\\/\\/news.yandex.ru\\/api\\/v2\\/rubric/, [404, {}, '']);
    </script>`
});

exports.degradation = news({
    ...degradationMock
});
