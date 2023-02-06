block('form')(
    tag()('form'),
    js()(true),
    attrs()(function() {
        return {
            method: this.ctx.method,
            action: this.ctx.action
        };
    }),
    elem('label')(
        tag()('label'),
        attrs()(function() {
            return {
                for: this.ctx.for
            };
        })
    )
);
