modules.define('page', ['i-bem-dom', 'main'], function(provide, bemDom, Main) {

provide(bemDom.declBlock(this.name, {
    _onChange: function(e, data) {
        this.setMod('error', data.hasIssues);
    }
}, {
    lazyInit: true,
    onInit: function() {
        this._events(Main).on('change', this.prototype._onChange);
    }
}));

});
