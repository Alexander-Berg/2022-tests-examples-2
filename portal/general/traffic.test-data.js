const mocks = require('./mocks');

exports.forecast_text = function (execView) {
    return execView('Style', {
        content: 'body{width:230px;}'
    }) + execView('Traffic', {}, {
        Traffic: mocks.text
    });
};

exports.forecast_future_end_day = function (execView) {
    return execView('Style', {
        content: 'body{width:230px;}'
    }) + execView('Traffic', {}, {
        Traffic: mocks.forecast_future_end_day
    });
};

exports.forecast_future_last = function (execView) {
    return execView('Style', {
        content: 'body{width:230px;}'
    }) + execView('Traffic', {}, {
        Traffic: mocks.forecast_future_last
    });
};

exports.forecast_icons = function (execView) {
    return execView('Style', {
        content: 'body{width:230px;}'
    }) + execView('Traffic', {}, {
        Traffic: mocks.forecast_icons
    });
};

exports.forecast_icons_end_day = function (execView) {
    return execView('Style', {
        content: 'body{width:230px;}'
    }) + execView('Traffic', {}, {
        Traffic: mocks.forecast_icons_end_day
    });
};

exports.description = function (execView) {
    return execView('Style', {
        content: 'body{width:230px;}'
    }) + execView('Traffic', {}, {
        Traffic: mocks.description
    });
};



