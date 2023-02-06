exports.simple = (execView) => execView('Style', {
    content: '.metro{box-shadow: none;}'
}) + execView('Metro', {}, {
    Metro: {
        icon: 'msk',
        show: 1,
        url: '//metro.yandex.ru/moscow',
        counter: 'msk'
    }
});
