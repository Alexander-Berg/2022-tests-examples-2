const alone = require('./mocks/alone.json');
const multiple = require('./mocks/multiple.json');

exports.alone = (execView) => {
    return '<div class="media-grid">' +
            '<div class="media-grid__row">' +
                execView('MediaEvent__serverSide', {}, Object.assign({}, JSON.parse(JSON.stringify(alone)), {
                    pageMods: {},
                    skin: {}
                })) +
            '</div>' +
        '</div>' +
        "<script>$(function(){$('.media-event').bem('media-event');});</script>";
};

exports.multiple = (execView) => {
    return '<div class="media-grid">' +
        '<div class="media-grid__row">' +
            execView('MediaEvent__serverSide', {}, Object.assign({}, JSON.parse(JSON.stringify(multiple)), {
                pageMods: {},
                skin: {}
            })) +
        '</div>' +
    '</div>' +
    "<script>$(function(){$('.media-event').bem('media-event');});</script>";
};
