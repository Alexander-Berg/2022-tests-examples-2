[
    {
        mustDeps: [
            'i-bem-dom'
        ],
        shouldDeps: [
            'codemirror',
            'jquery', 'form', 'result', 'cut',
            {
                block: 'textarea',
                mods: { theme: 'islands', size: 'm' }
            },
            {
                block: 'info-modal',
                mods: { theme: 'islands' }
            }
        ]
    },
    {
        tech: 'js',
        shouldDeps: [
            {
                tech: 'bemhtml',
                block: 'cut'
            },
            {
                tech: 'bemhtml',
                block: 'textarea',
                mods: { theme: 'islands', size: 'm' }
            },
            {
                tech: 'bemhtml',
                block: 'heading',
                mods: { level: 1 }
            }
        ]
    }
];
