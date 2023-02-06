BEM.DOM.decl('test-devices-selector', {

    PURPOSE: 'push_notifications',

    onSetMod: {
        js () {
            this._select = this.findBlockInside(this.elem('body'), 'select2');
            this._select.on('change', this._onSelectChange, this);
            this._val = this._select.getVal();
        },
    },

    destruct () {
        if (this._inited) {
            this._cancelButton.un('click', this._onCancelClick, this);
            this._saveButton.un('click', this._onSaveClick, this);
            this._name.un('change', this._checkValidity, this);
            this._id.un('change', this._checkValidity, this);
            this._attribution.un('change', this._checkValidity, this);
            this._popup.un('hide', this._onPopupHide, this);
            this._popup.destruct();
        }
        this._select.un('change', this._onSelectChange, this);
        this.__base.apply(this, arguments);
    },

    val () {
        return this._val;
    },

    _onSelectChange (e) {
        this._emitChanges({
            val: e.block.getVal(),
        });
    },

    _emitChanges (data) {
        this.trigger('change', data);
    },

    _getPopup () {
        if (!this._popupPromise) {
            this._popupPromise = BN('i-content').append(this.domElem, {
                block: this.__self.getName(),
                elem: 'popup',
                appId: this.params.appId,
                platform: this.params.platform,
            })
            .then(() => {
                this._inited = true;
                this._popup = this.findBlockInside('popup');
                this._popupElem = this.elem('popup');

                this._popup.on('hide', this._onPopupHide, this);
                this._initSettings();
                return this._popup;
            });
        }

        return this._popupPromise;
    },

    _initSettings () {
        this._cancelButton = this.findBlockOn('cancel', 'button')
            .on('click', this._onCancelClick, this);
        this._saveButton = this.findBlockOn('save', 'button')
            .on('click', this._onSaveClick, this);

        this._name = this.findBlockOn('name-input', 'input')
            .on('change', this._checkValidity, this);
        this._id = this.findBlockOn('id-input', 'input')
            .on('change', this._checkValidity, this);
        this._attribution = this.findBlockOn('attribution-select', 'select')
            .on('change', this._checkValidity, this);

        this._validator = BEM.create('i-validate', {
            validators: this.__self.validators,
            context: this,
        });
        this._validator.on('validity-set', this._onValiditySet, this);
        this._validator.validate(this._getFieldsVal());
    },

    _onValiditySet (e, validity) {
        this._saveButton.setMod('disabled', validity.valid ? '' : 'yes');
    },

    _onSaveClick () {
        var val = this._getFieldsVal(),
            that = this,
            params = {
                app_id: this.params.appId,
                device_id: val.deviceId,
                name: val.name,
                type: val.type,
                purpose: this.PURPOSE,
            };

        BN('i-attribution').create(params.app_id, params)
            .then(function (result) {
                return BN('i-attribution').list(params.app_id, params.purpose)
                    .then(function (res) {
                        return {
                            newId: result.device.id,
                            list: res.devices || [],
                        };
                    });
            })
            .then(function (result) {
                that.setMod('empty', result.list.length ? '' : 'yes');
                that._updateList(result.list, true, result.newId);
                that._popup.hide();
            })
            .done();
    },

    _onCancelClick () {
        this._popup.hide();
    },

    _onPopupHide () {
        this._id.val('');
        this._name.val('');
    },

    _onAddClick () {
        this._getPopup().then(function (popup) {
            popup.show();
        }).done();
    },

    _checkValidity () {
        this._validator.validate(this._getFieldsVal());
    },

    _getFieldsVal () {
        return {
            deviceId: this._id.val(),
            name: this._name.val(),
            type: this._attribution.val(),
        };
    },

    _updateList (fullList, isUser, newId) {
        const newList = this.__self.filterList(fullList, this.params.platform);

        return this.replaceHtml(
            this.findElem('body'),
            {
                block: this.__self.getName(),
                elem: 'body',
                list: newList,
            }
        )
        .then(() => {
            this._select.setVal(String(newId));
        })
        .done();
    },

}, {
    live () {
        this.liveBindTo('add-link', 'pointerclick', function (e) {
            this._onAddClick(e);
        });

        this.liveInitOnBlockInsideEvent('change', 'select2', function (event) {
            this._val = event.target.getVal();
        });

        return false;
    },

    validators: {
        deviceId: {
            required (val) {
                val = val.trim();
                return Boolean(val && val.length > 0);
            },
        },
        name: {
            required (val) {
                val = val.trim();
                return Boolean(val && val.length > 0);
            },
        },
    },
});
