const variants = [{
    mods: {
        theme: 'normal',
        size: 'n',
        tone: 'grey',
        view: 'default'
    }
}, {
    mods: {
        theme: 'normal',
        size: 'n',
        tone: 'grey',
        view: 'default'
    },
    content: [{
        side: 'right',
        content: 'right'
    }]
}, {
    mods: {
        theme: 'normal',
        size: 'n',
        tone: 'grey',
        view: 'default'
    },
    content: [{
        side: 'left',
        content: 'left'
    }]
}, {
    mods: {
        theme: 'normal',
        size: 'n',
        tone: 'grey',
        view: 'default'
    },
    content: [{
        side: 'left',
        content: 'left'
    }, {
        side: 'right',
        content: 'right'
    }]
}, {
    mods: {
        theme: 'normal',
        size: 'm',
        view: 'classic'
    }
}];

exports.simple = (execView) => {
    let rows = variants.map(obj => {
        let tumbler = execView('Tumbler', obj);
        obj.mods.checked = 'yes';
        let tumbler2 = execView('Tumbler', obj);

        return `<tr><td>${tumbler}</td><td>${tumbler2}</td></tr>`;
    });

    return `<table>${rows.join('')}</table>`;
};
