block('page')(
    js()(true),
    // replace 'index.min.js' with 'index.{lang}.min.js'
    elem('js').match(function() { return this.ctx.i18n; }).def()(function() {
        var url = this.ctx.url.split('.');
        url.splice(1, 0, this.i18n(this.block, 'lang'));

        return applyNext({ 'ctx.url': url.join('.') });
    })
);
