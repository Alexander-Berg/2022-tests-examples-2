BEM.DOM.decl('application-settings-test-devices', null, {
    live () {
        this.liveBindTo('instruction-header', 'pointerclick', function (e) {
            var params = this.elemParams(e.data.domElem) || {};

            if (params.name) {
                this.toggleMod(
                    this.elem('instruction', 'name', params.name),
                    'expanded',
                    'yes',
                    ''
                );
            }
        });
    },
});
