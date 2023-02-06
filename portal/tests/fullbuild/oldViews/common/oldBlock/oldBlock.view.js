views('oldBlock', function (data, req, execView) {
    return execView('oldBlock__layout', {
        content: execView('block')
    });
});

views('oldBlock__layout', function (data) {
    return '<div class="oldBlock">' + (data.content || '') + '</div>';
});
