(function() {
    /** @typedef {{frame: HTMLElement, container: HTMLElement}} TWidget */
    /** @typedef {Object.<string, TWidget>} TWidgets */
    /**
     * @typedef TInstance Глобальный объект
     * @type {Object}
     * @property {String} CLASSNAME Classname для поиска контейнеров на странице
     * @property {Boolean} inited Флаг инициализации
     * @property {Boolean} defer Флаг откладывающий автоматический запуск
     * @property {Boolean} started Флаг старта
     * @property {Function} sync Функция синхронизации виджетов на странице
     * @property {Function} start Функция запускает первоначальную инициализацию
     * @property {Function} stop Функция останавливает выполнение логики виджета на странцие
     * @property {Function} getWidgets Функция вернет объект виджетов
     */

    var ERROR_MSG =
        "There's been some kind of mistake. Please contact us using any available method of communication";
    // Ключ глобального объекта на странице
    var ROOT_NAME = 'Ya';
    // Ключ плагина
    var WIDGET_NAME = 'efirWidget';
    // Класс контейнера, необходимый для поиска и инициализации
    var CLASSNAME = 'efir-widget';
    // URL страницы виджета которую встраиваем
    var FRAME_URL = 'https://frontend.vh.yandex.ru/v23/player/';
    // Префикс для событий песочницы
    var SANDBOX_EVENT_PREFIX = 'sandbox-event-prefix-';
    // Параметры песочницы
    var SANDBOX_DEFAULT_PARAMS = [
        'from=partner',
        'recommendations=off',
        'recommendations_permanent_titles_visibility=true',
        'autoplay=0',
        'mute=0',
        'from_block=partner_pretty_player'
    ];

    /** @type {Object} Ссылка на корень глобального объекта */
    var root = (document[ROOT_NAME] = document[ROOT_NAME] || {});

    /** @type {TInstance} Ссылка на глобальный объект */
    var instance = (root[WIDGET_NAME] = root[WIDGET_NAME] || {});

    if (instance.inited) {
        // Если запустили раньше, синхронизируем
        if (instance.started) {
            instance.sync();
        }
        return;
    }

    /** @type {TWidgets} словарь виджетов на странице */
    var widgets = {};

    /** @type {number} счетчик виджетов для создания уникального идентификатора */
    var counter = 0;

    /**
     * Формирует URLParams для передачи во фрейм
     * @param {Object} params словарь название параметра - значение
     * @returns {String}
     */
    var getUrlParams = function(params) {
        var sandboxParams = SANDBOX_DEFAULT_PARAMS.join('&');

        sandboxParams = sandboxParams + '&event_prefix=' + SANDBOX_EVENT_PREFIX + params.wid + ':';

        if (params.partnerId) {
            sandboxParams = sandboxParams + '&partner_id=' + params.partnerId;
        }

        return '?' + sandboxParams;
    };

    /**
     * Вставит фрейм в контейнер предварительно его очистив
     * @param {HTMLElement} container
     * @param {HTMLDivElement} frame
     */
    var embedFrame = function(container, frame) {
        container.innerHTML = '';
        container.appendChild(frame);
    };

    /**
     * Создает блок с фреймом и возвращает его
     * @param params
     * @return {HTMLDivElement}
     */
    var createFrame = function(params) {
        var frameWrapper = document.createElement('div');
        frameWrapper.width = '100%';
        frameWrapper.style.maxWidth = '800px';
        frameWrapper.style.padding = '0';
        frameWrapper.style.margin = '10px auto';
        frameWrapper.style.display = 'none';

        var frameContainer = document.createElement('div');
        frameContainer.height = '0';
        frameContainer.width = '100%';
        frameContainer.style.padding = '0 0 56.3%';
        frameContainer.style.margin = '0';
        frameContainer.style.position = 'relative';

        var frame = document.createElement('iframe');
        frame.src = FRAME_URL + params.id + getUrlParams(params);
        frame.style.position = 'absolute';
        frame.style.backgroundColor = 'transparent';
        frame.style.border = 'none';
        frame.style.overflow = 'hidden';
        frame.style.borderRadius = '8px';
        frame.style.top = '0';
        frame.style.left = '0';
        frame.allow = 'autoplay; encrypted-media';
        frame.allowFullscreen = true;
        frame.allowTransparency = true;
        frame.width = '100%';
        frame.height = '100%';

        frameContainer.appendChild(frame);
        frameWrapper.appendChild(frameContainer);

        return frameWrapper;
    };

    /**
     * Инициализирует виджет и вставляет iframe в контейнер
     * @param {HTMLElement} container
     * @returns {Object}
     */
    var initializeWidget = function(container) {
        var wid = container.dataset.wid || counter++;

        if (widgets[wid]) {
            return widgets[wid];
        }

        container.dataset.wid = wid;
        container.style.textAlign = 'center';
        container.style.fontSize = '0';

        var frame = createFrame(container.dataset);
        embedFrame(container, frame);

        return {
            wid: wid,
            container: container,
            frame: frame
        };
    };

    /**
     * Производит поиск контейнеров и запускает их инициализацию
     * Добавляет новые виджеты, если появились
     */
    var sync = function() {
        var elems = document.getElementsByClassName(instance.CLASSNAME),
            newWidgets = {};

        if (elems.length) {
            var containers = Array.prototype.slice.call(elems);
            var widget;
            for (var index in containers) {
                widget = initializeWidget(containers[index]);
                newWidgets[widget.wid] = widget;
            }
        }

        widgets = newWidgets;
    };

    /**
     * Запускает первоначальную инициализацию
     */
    var start = function() {
        bindEvents();
        sync();
        instance.started = true;
    };

    /**
     * Останавливает выполнение
     */
    var stop = function() {
        unbindEvents();
    };

    /**
     * Подписывается на сообщения
     */
    var bindEvents = function() {
        if (window.addEventListener) {
            window.addEventListener('message', messageListener);
        } else {
            window.attachEvent('onmessage', messageListener);
        }
    };

    /**
     * Отписывается от сообщений
     */
    var unbindEvents = function() {
        if (window.removeEventListener) {
            window.removeEventListener('message', messageListener);
        } else {
            window.detachEvent('onmessage', messageListener);
        }
    };

    /**
     * Управляет показом виджета
     * @param {String} wid - id виджета
     */
    var show = function(wid) {
        var widget = widgets[wid];

        if (widget) {
            widget.frame.style.display = 'block';
        }
    };

    /**
     * Управляет логирование ошибок и скрытием виджета
     * @param {Object} payload данные отправленные виджетом
     */
    var error = function(payload) {
        var wid = payload.wid;

        if (wid && payload.fatal) {
            var widget = widgets[wid];

            if (widget) {
                // TODO Нужен фолбек на виджет без фрейма
                widget.container.parentNode.removeChild(widget.container);
                delete widgets[wid];
            }
        }

        // eslint-disable-next-line no-console
        console.error(ERROR_MSG, payload);
    };

    /**
     * Прослушивает события для управления виджетом
     * @param {Event} event
     */
    var messageListener = function(event) {
        var data = event.data;

        try {
            var eventName = JSON.parse(data).event;
            var sandboxMsg = eventName.match(/sandbox-event-prefix-(\d):(\w+)/);

            if (!sandboxMsg) {
                return;
            }

            var wid = sandboxMsg[1];
            var sandboxEventName = sandboxMsg[2];

            switch (sandboxEventName) {
                case 'error':
                    error({
                        wid: wid,
                        fatal: true,
                        error: eventName
                    });
                    break;
                case 'inited':
                    show(wid);
                    break;
                default:
                    return;
            }
        } catch (e) {
            //
        }
    };

    /**
     * Вернет сохраненные виджеты
     */
    var getWidgets = function() {
        return widgets;
    };

    instance.CLASSNAME = CLASSNAME;
    instance.inited = true;
    instance.sync = sync;
    instance.start = start;
    instance.stop = stop;
    instance.getWidgets = getWidgets;

    if (!instance.defer) {
        instance.start();
    }
})();
