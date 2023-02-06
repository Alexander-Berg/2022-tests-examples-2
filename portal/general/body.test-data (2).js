const servicesAll = require('./mocks/body.json');


exports.all = function (execView) {
    return execView('Style', {
        content: '.services-big__item_icon,.services-all__icon,.services-big__item_icon{' +
                'background: #4eb0da !important;' +
                '}'
    }) +
        execView('BLayout__content', {}, servicesAll);
};
