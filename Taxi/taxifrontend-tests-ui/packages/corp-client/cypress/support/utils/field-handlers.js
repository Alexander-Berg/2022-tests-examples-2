class FieldsHandlers {
    constructor() {
        this.getFieldHandler = this.getFieldHandler.bind(this);
        this.addFieldHandler = this.addFieldHandler.bind(this);
    }

    _list = {
        input: {
            fill: 'fillTextInput',
            clear: 'clearTextInput',
        },
    };

    getFieldHandler(fieldType, handlerType) {
        return this._list[fieldType][handlerType];
    }

    addFieldHandler(fieldType, handlerType, handler) {
        this._list[fieldType][handlerType] = handler;
    }
}

export default new FieldsHandlers();
