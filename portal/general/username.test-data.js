exports.simple = function (execView) {
    return '<div class="root" style="display: inline-block">' +
        '<div>' +
        execView('Username', {}, {
            UserName: {f: 'a', l: 'bcde'}
        }) +
        '</div>' +
        '<div>' +
        execView('Username', {}, {
            UserName: {f: '1', l: '23456789012345678901234567890'}
        }) +
        '</div>' +
        '<div>' +
        execView('Username_sliced', {}, {
            UserName: {f: 'a', l: 'bcde'}
        }) +
        '</div>' +
        '<div>' +
        execView('Username_sliced', {}, {
            UserName: {f: '1', l: '23456789012345678901234567890'}
        }) +
        '</div>' +
        '</div>';
};
