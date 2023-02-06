exports.simple = execView => execView('SimpleButton', {
    mods: {
        size: 'm',
        theme: 'action'
    },
    content: 'Text'
}) + execView('SimpleButton', {
    mods: {
        size: 'm',
        theme: 'action',
        wide: 'yes'
    },
    content: 'Text'
});
