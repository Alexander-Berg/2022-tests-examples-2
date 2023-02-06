const mockApi = mock => `<script>
    var server = sinon.fakeServer.create();

    server.respondWith(/\\/empty\\?api/, [200, {'Content-Type': 'application/json'}, JSON.stringify(${JSON.stringify(require(`./mocks/${mock}`))})]);
</script>`;

exports.withoutTabs = execView => mockApi('withoutTabs') + execView('Divjson2Block', {
    api: '/empty?api',
    title: 'Тестовый блок',
    cardWidth: 116,
    layoutName: 'test'
});

exports.withTabs = execView => mockApi('withTabs') + execView('Divjson2Block', {
    api: '/empty?api',
    title: 'Тестовый блок',
    cardWidth: 116,
    tabs: true,
    layoutName: 'test'
});

exports.tabsBottom = execView => mockApi('tabsBottom') + execView('Divjson2Block', {
    api: '/empty?api',
    title: 'Тестовый блок',
    cardWidth: 116,
    tabs: true,
    layoutName: 'test'
});

exports.coloredTabs = execView => mockApi('coloredTabs') + execView('Divjson2Block', {
    api: '/empty?api',
    title: 'Тестовый блок',
    cardWidth: 116,
    tabs: true,
    layoutName: 'test'
});

exports.dark = execView => mockApi('withTabs') + execView('Divjson2Block', {
    api: '/empty?api',
    title: 'Тестовый блок',
    cardWidth: 116,
    tabs: true,
    layoutName: 'test'
}, {
    Skin: 'night'
});
