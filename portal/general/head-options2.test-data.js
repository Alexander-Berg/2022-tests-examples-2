/* eslint-env es6 */

exports.simple = (execView) => '<div style="padding: 100px;">' + execView('HeadOptions2', {}, {
    HomePageNoArgs: 'https://yandex.ru',
    MordaZone: 'ru',
    JSON: {
        common: {}
    },
    blocks_layout: ['infinity_zen'],
    Zen: {
        is_lib: true,
        show: true
    }
}) + '</div>';

exports.noBlocks = (execView) => '<div style="padding: 100px;">' + execView('HeadOptions2', {}, {
    HomePageNoArgs: 'https://yandex.ru',
    MordaZone: 'ru',
    JSON: {
        common: {}
    },
    blocks_layout: []
}) + '</div>';

exports.skins = (execView) => '<div style="padding: 100px;">' + execView('HeadOptions2', {}, {
    HomePageNoArgs: 'https://yandex.ru',
    MordaZone: 'ru',
    JSON: {
        common: {}
    },
    sk: '123456',
    blocks_layout: ['infinity_zen'],
    Zen: {
        is_lib: true,
        show: true
    }
}) + '</div>';
