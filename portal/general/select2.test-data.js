exports.simple = (execView) => execView('Select2', {
    mods: {
        type: 'radio',
        view: 'default',
        tone: 'default',
        text: 'vary',
        theme: 'normal',
        size: 'n'
    },
    items: [
        {val: 'red', text: 'Каждый', icon: {mods: {glyph: 'carets-v'}}},
        {val: 'orange', text: 'Охотник', icon: {mods: {glyph: 'carets-v'}}},
        {val: 'yellow', text: 'Желает'},
        {val: 'green', text: 'Знать'},
        {val: 'lightblue', text: 'Где'},
        {val: 'blue', elemMods: {disabled: 'yes'}, text: 'Сидит'},
        {val: 'violet', text: 'Фазан'}
    ]
});
