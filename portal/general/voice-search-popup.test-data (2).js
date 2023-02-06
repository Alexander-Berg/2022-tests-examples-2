exports.simple = function (execView) {
    return '<style>' +
        'html,body{height:100%;}' +
        'body{margin: 0;}' +
        '.voice-search-popup__letter{animation-name:none;}' +
        '</style>' +
        execView('VoiceSearchPopup', {}, {});
};
