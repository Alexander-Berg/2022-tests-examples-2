/**
 * @fires#list-update
 *
 * Tells other `test-devices-selector` blocks that list of devices was updated
 * Also subscribes to this `list-update` event and update self
 */
BEM.DOM.decl({name: 'test-devices-selector', modName: 'update-on-event', modVal: 'yes'}, {

    onSetMod: {
        js () {
            this.__base.apply(this, arguments);
            BN(this.__self.getName()).on('list-update', this._onListUpdate, this);
        },
    },

    _onListUpdate (e, data) {
        if (e.block !== this) {
            this._updateList(data.fullList, false);
        }
    },

    /**
     * trigger `list-update` only if user add new device manually
     * @override {test-devices-selector}
     */
    _updateList (fullList, isUser) {
        this.__base.apply(this, arguments);
        if (isUser) {
            this.trigger('list-update', {
                fullList,
            });
        }
    },

});
