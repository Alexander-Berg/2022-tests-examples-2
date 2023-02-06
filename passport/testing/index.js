module.exports = {
    port: '3000',
    path: '/broker2',
    blackbox: 'pass-test.yandex.ru',
    frontend_url: 'https://social-test.yandex.ru/broker2',
    staticPath: '//yastatic.net/broker/{{VERSION}}',
    st_path: '//yastatic.net/broker/{{VERSION}}',
    url: {
        protocol: 'http',
        host: '127.0.0.1:6000'
    },
    paths: {
        experiments: 'http://uaas.search.yandex.net/passport'
    }
};
