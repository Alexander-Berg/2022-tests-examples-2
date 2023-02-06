const mockApi = (mock) => `<script>
    var server = sinon.fakeServer.create();

    server.respondWith(/\\/empty\\?api/, [200, {'Content-Type': 'application/json'}, JSON.stringify(${JSON.stringify(require(`./mocks/${mock}`))})]);
</script>`;

exports.withoutTabs = execView => mockApi('withoutTabs') +
    '<div class="media-grid" style="width:900px;padding:40px" data-bem="{&quot;media-grid&quot;:{&quot;layout&quot;:[]}}">' +
    execView('Divjson2Block', {
        layoutName: 'test',
        api: '/empty?api',
        title: 'Тестовый блок',
        cardWidth: 116
    }) +
    '</div>';

exports.withTabs = execView => mockApi('withTabs') +
    '<div class="media-grid" style="width:900px;padding:40px" data-bem="{&quot;media-grid&quot;:{&quot;layout&quot;:[]}}">' +
    execView('Divjson2Block', {
        layoutName: 'test',
        api: '/empty?api',
        title: 'Тестовый блок',
        cardWidth: 116,
        tabs: true
    }) +
    '</div>';

exports.dark = (execView) => {
    return mockApi('dark') + '<div class="media-grid" style="width:900px;padding:40px" data-bem="{&quot;media-grid&quot;:{&quot;layout&quot;:[]}}">' +
        '<div class="media-grid__row">' + execView('Divjson2Block', {
        layoutName: 'test',
        api: '/empty?api',
        title: 'Тестовый блок',
        cardWidth: 116,
        tabs: true
    }, {
        Skin: 'night'
    }) +
        '</div>' +
        '</div>';
};
