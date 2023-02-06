({
    shouldDeps: [
        'i-platform',
        'i-validate',
        'i-url',
        {block: 'link',  mods: {pseudo: 'yes'}},
        {block: 'select2', mods: {size: 's', theme: 'normal'}},
        {block: 'button', mods: {size: 's', theme: 'action'}},
        {block: 'input', mods: {theme: 'normal', size: 's'}},
        {block: 'popup', elems: ['content'], mods: {type: 'modal', autoclosable: 'no', animate: 'no', adaptive: 'yes', padding: 'no'}}
    ]
})
