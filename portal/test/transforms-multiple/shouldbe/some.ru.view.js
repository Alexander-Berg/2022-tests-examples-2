(function () {
    var views = home.desktopViews.ru;
/* begin: transforms-multiple/blocks/test.view.html */
// wait: done
views('viewName', '<div class="home-layout">abc</div>');
/* end: transforms-multiple/blocks/test.view.html */
/* begin: transforms-multiple/blocks/test2.view.js */
// wait: done
views('news',
    '<div class="news"></div>'
);
/* end: transforms-multiple/blocks/test2.view.js */
})();
