const mocks = require('./mocks.js');

const bodyStyles = (execView) => {
    return execView('Style', {
        content: `body {
        width:300px;
        position:relative;
        margin-top:5px;
        padding: 8px 4px 4px 15px;
    }`
    });
};

exports.region = function (execView) {

    return (
        bodyStyles(execView) + execView('Region', {}, {
            Geo: mocks.Geo,
            MordaZone: 'ru'
        })
    );
};

exports.regionNoHeading = function (execView) {

    return (
        bodyStyles(execView) + execView('Region', {}, {
            Geo: mocks.notitleGeo,
            MordaZone: 'ru'
        })
    );
};

exports.regionNoName = function (execView) {

    return (
        bodyStyles(execView) + execView('Region', {}, {
            Geo: mocks.nonameGeo,
            MordaZone: 'ru'
        })
    );
};

exports.regionNoList = function (execView) {

    return (
        bodyStyles(execView) + execView('Region', {}, {
            Geo: mocks.nolistGeo,
            MordaZone: 'ru'
        })
    );
};
