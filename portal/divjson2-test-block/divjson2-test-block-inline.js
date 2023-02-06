document.addEventListener('DOMContentLoaded', function () {
    home.loadManager.subscribe('js', function() {
        /**
         * @class DivJson2BlockTest
         * @extends DivJson2Block
         */
        BEM.DOM.decl({block: 'divjson2-block', modName: 'test', modVal: 'yes'}, {
            /**
             * Доопределяем класс после инициализации блока
             * @private
             */
            _attach: function () {
                if (!this.params.api) {
                    this._initTextArea('');
                }
            },
            /**
             * Ищет инпут, который находится за пределами блока
             * @returns {BEM.DOM}
             * @private
             */
            _findTextArea: function () {
                return this.findBlockOn($('.divjson2-block__test-input'), 'input');
            },
            /**
             * Проставляет значение в поле ввода и подписывается на изменения
             * @param {string} initialVal
             * @private
             */
            _initTextArea: function (initialVal) {
                this._findTextArea()
                    .val(initialVal)
                    .on('change', function (event) {
                        try {
                            var newVal = event.block.val();
                            if (newVal !== initialVal) {
                                this._drawBlock(JSON.parse(newVal));
                                initialVal = null;
                            }
                        } catch (err) {
                            // eslint-disable-next-line no-console
                            console.error(err);
                        }
                    }.bind(this));
            },
            /**
             * Обрабатывает загрузку
             * @param {object} data
             * @private
             */
            _onLoad: function (data) {
                var initialVal = JSON.stringify(data, 0, 4);

                this._initTextArea(initialVal);

                this.__base.apply(this, arguments);
            }
        });

        $('.divjson2-block_test_yes').bem('divjson2-block')._attach();
    });
});
