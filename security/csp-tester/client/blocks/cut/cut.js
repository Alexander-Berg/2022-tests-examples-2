modules.define('cut', ['i-bem-dom', 'cut__switcher'], function(provide, bemDom, Switcher) {

provide(bemDom.declBlock(this.name, {
    showMore: function() {
        this.toggleMod('visible');
    }
}, {
    lazyInit: true,
    onInit: function() {
        this._events(Switcher).on('click', this.prototype.showMore);
    }
}));

});

modules.define('cut__switcher', ['i-bem-dom', 'button'], function(provide, bemDom, Button) {

provide(bemDom.declElem('cut', 'switcher', {
    _onClick: function() {
        this._emit('click');
    }
}, {
    lazyInit: true,
    onInit: function() {
        this._events(Button).on('click', this.prototype._onClick);
    }
}));

});
