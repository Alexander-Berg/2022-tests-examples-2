(function () {
    var views = home.desktopViews;
/* begin: transforms-multiple/blocks/test.view.html */
// wait: done
views('viewName', '<div class="home-layout">[% l10n:title %]</div>');
/* end: transforms-multiple/blocks/test.view.html */
/* begin: transforms-multiple/blocks/test2.view.js */
// wait: done
views('news',
    '<div class="news"></div>'
);
/* end: transforms-multiple/blocks/test2.view.js */
})();
