BEM.DOM.decl({name: 'application-settings-lists', modName: 'type', modVal: 'test-devices'}, {
    /**
     * Gets data from row
     * @param {jQuery} row
     * @return {Object} field_name: field_value
     * @private
     * @override
     */
    _getDataFromRow (row) {
        const selectBlocks = this.findBlocksInside(row, 'select2');

        return selectBlocks.reduce((result, selectBlock) => {
            result[selectBlock.getName()] = selectBlock.getVal();
            return result;
        }, this.__base(...arguments));
    },

    /**
     * Handler for creating a new test device
     * @param {jQuery} row
     * @private
     */
    _create (row) {
        var params = this._getDataFromRow(row),
            appId;

        if (!params.name || !params.device_id) {
            this._markEmptyFields(row);
            return;
        }

        appId = BN('i-params').get('item').appId;
        BN('i-attribution').create(appId, params)
            .then((result) => {
                this._replaceRow(row, result.device);
            })
            .fail((error) => {
                const errorMessage = (_.get(error, 'status') === 409) ?
                    _.get(error, ['body', 'message'], this.i18n('error-device-exists')) :
                    error;

                this._failHandler(errorMessage);
            })
            .done();
    },

    /**
     * Handler for updating test device information
     * @param {jQuery} row
     * @returns {Promise}
     */
    _update (row) {
        var params = this.elemParams(row),
            newParams,
            appId;

        if (!params.id) {
            return Vow.fulfill();
        }

        newParams = this._getDataFromRow(row);

        if (!newParams.name || !newParams.device_id) {
            return Vow.fulfill();
        }

        appId = BN('i-params').get('item').appId;
        return BN('i-attribution').update(appId, params.id, newParams)
            .fail((error) => {
                const errorMessage = (_.get(error, 'status') === 409) ?
                    this.i18n('error-device-exists') :
                    error;

                this._failHandler(errorMessage);
            });
    },

    /**
     * Handler for deleting a test device
     * @param {jQuery} row
     * @private
     */
    _delete (row, button) {
        var params = this.elemParams(row);

        if (!params.id) {
            return;
        }

        BN('i-attribution').remove(BN('i-params').get('item').appId, params.id)
            .then(() => {
                BEM.DOM.destruct(row);
            })
            .fail((err) => {
                this._failHandler(err);
                button.delMod('disabled');
            })
            .done();
    },
});
