// На самом деле API вот тут
let quasarApp = {
    /**
     * Метод для сообщения нативному коду, что можно присылать команды (звать window.quasar._update)
     */
    notifyPageReady: function(){
        console.log('Натив понял, что webview готова');

        window.quasar.fakeCommandsFromServer([
            {
                name: 'updateInitialState',
                args: {
                    initialState: {}
                }
            },
            {
                name: 'navigation',
                args: {
                    direction: 'down'
                }
            }
        ]);
        // <native code>
    },

    notifyPageLoaded: function () {
        // <native code>
    },

    /**
     * Нативный метод
     * @param {String} name - имя команды
     * @param {String} payloadAsJson - JSON, внутри объект (формат разный, в зависимости от команды)
     * @returns {string}
     */
    // webview -> app
    runCommand: function(name, payloadAsJson) {
        // распарсить команду
        // если имя команды поддерживается, выполнить с аргументами
        // если имя команды не поддерживается, вернуть ошибку

        // Как-то обрабатываем payload

        return JSON.stringify({
            command: name,
            // Тут любой объект
            result: {
                forExample: 'тут что угодно ' + payloadAsJson,
            }
        });
        // <native code>
    },
    runCommandAsync: function (name, payloadAsJson) {
        let asyncCommands = ['showOnboarding', 'scenario'];

        // Как-то обрабатываем payload

        if (asyncCommands.includes(name)) {
            // Уникальный ключ текущего вызова команды
            let asyncKey = 'async.' + name + '.' + Math.random();

            if (window.ASYNCERROR) {
                // Пример ошибки выполнения асинхронной команды
                setTimeout(function () {
                    window.quasar.fakeCommandFromServer( name, {
                        __token__: asyncKey,
                        error: {
                            message: 'Все плохо, онбординг не запустился'
                        }
                    });

                }, 500);
            } else {
                // Пример успешного выполнения асинхронной команды
                setTimeout(function () {
                    window.quasar.fakeCommandFromServer( name, {
                        __token__: asyncKey,
                        result: {
                            message: 'Теперь вы все умеете ' + payloadAsJson
                        }
                    });
                }, 3000);
            }

            return JSON.stringify({
                token: asyncKey
            });

        } else {
             return JSON.stringify({
                error: {
                    message: 'Позвали не асинхронную команду в runCommandAsync'
                }
            });
        }
    }
};

// Вот уже над ними Коля сделает удобное API, например
class QuasarApi {
    constructor () {
        if (QuasarApi._instance) {
            return QuasarApi._instance;
        }

        this.data = {};
        this.data.state = {};
        QuasarApi._instance = this;

    }

    /**
     * Метод, который зовет native для вызовов из app. Зовется после ready
     * @param {String} commandAsString  - JSON вида {name: String, agrs: Object)
     * @private
     */
    _command (commandAsString) {
        let command;

        try {
            command = JSON.parse(commandAsString);
        } catch (e) {
            return;
        }

        QuasarApi._processNativeCommand(command);

    }

    /**
     * Метод, который зовет native для вызовов из app пачкой (накопленные команды от натива) Зовется после ready
     * @param {String} commandAsStringArr - JSON вида [{name: String, agrs: Object)]
     * @private
     */
    _commands (commandAsStringArr) {
        let nativeCommands;

        try {
            nativeCommands = JSON.parse(commandAsStringArr);
        } catch (e) {
            return;
        }

        for (var i = 0; i < nativeCommands.length; ++i) {
            QuasarApi._processNativeCommand(nativeCommands[i]);
        }

    }

    /**
     * Метод для обработки комманды, зовет все подписанные на комманду обработчики
     * @param {Object} command
     * @param {String} command.name - название команды (например navigation)
     * @param {Object} command.args - payload команды (любые данные в объекте, которые нужны для обработки комманды)
     * @private
     */
    static _processNativeCommand (command) {
        let commandName = command.name,
            commandPayload = command.args;

        console.log('Нативная комманда с сервера', command);
        // Обработка асинхронных команд. _runCommandAsync добавляет колбеки при вызове
        if (commandPayload.__token__) {
            return this._processNativeCommandAsync(commandPayload.__token__, commandPayload);
        }

        this._eventTarget.dispatchEvent(new CustomEvent(commandName, {
            detail: commandPayload
        }));

    }

    /**
     * Обработка асинхронной команды от натива
     * @param {String} token - id вызова асинхронной команды, уникальная строка
     * @param {{__token__: String, [result]: Object, [error]: Object}} commandPayload - результат команды (ошибка или )
     * @private
     */
    static _processNativeCommandAsync (token, commandPayload) {
        let error = commandPayload.error,
            payload = commandPayload.result;

        if (error) {
            this._asyncCallbacks[token]['error'](error);
        }

        this._asyncCallbacks[token]['success'](payload);

        delete this._asyncCallbacks[token];

    }

    /**
     * Метод для вызова нативной команды из клиентского кода
     * @param {String} name - имя комманды
     * @param {Object} payload - payload комманды, который прокидывается в app
     * @returns {Object} - результат выполнения команды
     * @private
     */
    static _runCommand (name, payload) {
        let payloadAsString = JSON.stringify(payload),
            commandResultAsString = quasarApp.runCommand(name, payloadAsString),
            commandResult;

        try {
            commandResult = JSON.parse(commandResultAsString)
        } catch (e) {
            return;
        }

        console.log('Ответ нативной комманды', commandResult);

        if (commandResult.error) {
            throw Error(commandResult.error.message);
        }

        return commandResult.result;
    }

    /**
     *
     * @param name
     * @param payload
     * @returns {Promise<any>}
     * @private
     */
    static _runCommandAsync (name, payload) {
        let payloadAsString = JSON.stringify(payload),
            commandResultAsString = quasarApp.runCommandAsync(name, payloadAsString),
            commandResult,
            pendingKey;

        try {
            commandResult = JSON.parse(commandResultAsString);
        } catch (e) {
            return Promise.reject(e);
        }

        pendingKey = commandResult.__token__;

        return new Promise(function (resolve, reject) {
            if (commandResult.error) {
                return reject(commandResult.error);
            }

            QuasarApi._asyncCallbacks[pendingKey] = {
                success: resolve,
                error: reject
            };

        });
    }

    static _asyncCallbacks = {};

    static _eventTarget = new EventTarget();

    /**
     * Метод, который нужно вызвать, когда клиент готов получать сообщения от приложения
     */
    ready () {
        // TODO: возможно асинхронный и нужно ждать ответ для вызовов команд
        quasarApp.notifyPageReady();

    }

    /**
     * Метод, который нужно вызвать, когда страница отобразилась (чтобы заменить заглушку)
     */
    pageLoaded () {
        quasarApp.notifyPageLoaded && quasarApp.notifyPageLoaded();

    }

    /**
     * Сообщает приложению, что клиент собирается пользоваться функциональностью
     * @param feature
     * @private
     */
    _enableFeature (feature) {
        if (!this._featuresEnbaled) {
            QuasarApi._runCommand('enable_feature', {
                feature: feature
            })
        }

    }

    /**
     * Подписка на команду из натива
     * @param {String} command
     * @param {Function} callback
     */
    onCommand (command, callback) {
        QuasarApi._eventTarget.addEventListener(command, callback);

    }

    /**
     * Отписка от команды из натива
     * @param {String} command
     * @param {Function} callback
     */
    offCommand (command, callback) {
        QuasarApi._eventTarget.removeEventListener(command, callback);

    }

    /**
     * Подписка на события навигации
     * @param {Function} callback - function({direction: String})
     */
    onNavigation(callback) {
        this.onCommand('navigation', callback);

    }

    /**
     * Отписка от события навигации
     * @param {Function} callback - function({direction: String})
     */
    offNavigation(callback) {
        this.offCommand('navigation', callback);

    }

    /**
     * Сообщаем, какие направления доступны для навигации
     * @param {{left: Boolean, right: Boolean, up: Boolean, down: Boolean}} directionsObject - объект с доступными направлениями
     */
    setAvailableNavDirections (directionsObject) {
        QuasarApi._runCommand('set_available_nav_directions', directionsObject);

    }

    /**
     * Получить текущий state из натива
     * @returns {args|{initialState}|{direction}|Object|*|"new"}
     */
    getState () {
        let commandResult = QuasarApi._runCommand({name:'get_state'});
        return commandResult.args && commandResult.args.state;

    }

    /**
     * Установить текущий стейт
     * @param {Object} newState
     */
    setState (newState) {
        this.data.state = newState;
        return QuasarApi._runCommand('set_state', {
            state: newState
        });

    }

    /**
     * Обновляет список элементов в саджесте
     * @param {{text: String}[]} suggestItems - массив объектов (каждый - одна подсказка в саджесте)
     */
    updateSuggest (suggestItems) {
        this.data.suggest = suggestItems;
        QuasarApi._runCommand('update_suggest', {
            suggestItems: suggestItems
        });
        console.log('Обновляем саджест:', suggestItems.map(item => item.text).join(', '));

    }

    /**
     * Обновляет список элементов в саджесте
     * @param {{text: String}[]} asrItems - массив объектов с текстами asr
     */
    updateAsr (asrItems) {
        QuasarApi._runCommand('update_asr', {
            asr: asrItems
        });

    }

    /**
     * Обновляет текс заголовка страницы в нативной панели сверху
     * Пустая строка - скрывает текст
     * @param {String} text - строка
     */
    setPageTitle (text) {
        QuasarApi._runCommand('set_page_title', {
            text: text || ''
        });
        console.log('Обновляем заголовок:', text);

    }

    /**
     * Обновляет текущий url страницы для восстановления
     * @param {String} url - url текущей страницы
     */
    setPageUrl (url) {
        QuasarApi._runCommand('set_page_url', {
            url: url
        });
        console.log('Обновляем текущий url страницы:', url);

    }

    /**
     * Показать информеры (актуально для 1-го экрана)
     */
    showInformers () {
        QuasarApi._runCommand('show_informers', {});

    }

    /**
     *
     * @param {String} name - имя сценария
     * @param {Object} payload - payload сценария
     * @returns {Promise<any>}
     */
    callScenario (name, payload) {
        return QuasarApi._runCommandAsync('scenario', {
            name: name,
            payload: payload
        });

    }

    // Тут тестовые функции. Асинхронная команда с ошибкой и без + синхронная команда с ошибкой

    /**
     * Пример асинхронной команды в натив
     * @returns {Promise<any>}
     */
    showOnboarding (shoulThrowError) {
        window.ASYNCERROR = !!shoulThrowError;

        return QuasarApi._runCommandAsync('showOnboarding', {}).then(function (payload) {
            alert(payload.message);
        }, function (error) {
            console.error(error.message)
        });

    }

    /**
     * Временный метод, притворяется вызовом нативной команды
     * @param {string} command
     * @param {Object} payload
     */
    fakeCommandFromServer (command, payload) {
        let fakeNativeCommandAsString = JSON.stringify({
            name: command,
            args: payload
        });

        this._command(fakeNativeCommandAsString);

    }
    /**
     * Временный метод, притворяется вызовом нескольких нативных команды
     * @param {{name: String, args: Object}[]} commands
     */
    fakeCommandsFromServer (commands) {
        let fakeNativeCommandsArrAsString = JSON.stringify(commands);

        this._commands(fakeNativeCommandsArrAsString);

    }

}

window.quasar = new QuasarApi();
