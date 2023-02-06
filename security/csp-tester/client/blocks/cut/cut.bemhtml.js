block('cut')(
    js()(true),
    content()(function() {
        var switcher = this.ctx.switcher;

        return [
            {
                elem: 'switcher',
                content: typeof switcher === 'string' ? {
                    block: 'button',
                    mods: { theme: 'islands', size: 'm', togglable: 'check' },
                    text: switcher
                } : switcher
            },
            {
                elem: 'content',
                content: applyNext()
            }
        ];
    }),
    elem('switcher').js()(true)
);
