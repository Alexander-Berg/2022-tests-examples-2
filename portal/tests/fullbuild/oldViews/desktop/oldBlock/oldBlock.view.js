views('oldBlock', function oldBlock (data, req, execView) {
    return 'oldBlock overriden ' + execView(oldBlock.base, data);
});

views('oldBlock__layout', function (data) {
    return '<div class="oldBlock_desktop">' + (data.content || '') + '</div>';
});
