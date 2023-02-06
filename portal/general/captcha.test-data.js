exports.simple = function (execView) {
    return '<style>.captcha{display:inline-block;}</style>' + execView('Captcha', {});
};
