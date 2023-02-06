function Viewer() {
    this.env = 'dev'; // rc, prod
    this.urls = {
        dev: '/portal/api/search/2/',
        rc: 'https://www-rc.yandex.ru/portal/api/search/2/',
        prod: 'https://www.yandex.ru/portal/api/search/2/'
    };

    this.requiredParams = {
        'app_version_name': '',
        'app_version': '',
        'app_platform': '',
        'dp': '2',
        'did': '22222222222222222222222222222222',
        'model': '',
        'app_id': 'ru.yandex.searchplugin.dev',
        'uuid': '11111111111111111111111111111111',
        'size': '',
        'os_version': '',
        'lang': 'ru-RU',
        'app_build_number': '1',
        'afisha_version': '3',
        'manufacturer': '',
        'poiy': '',
        '_cacheResourcesFlag': 1
    };

    this.device = 'androidNew';
    
    this.userDevices = {
        androidNew: {
            'app_version_name': '6.20',
            'app_version': '6020000',
            'app_platform': 'android',
            'dp': '3.0',
            'did': '22222222222222222222222222222222',
            'model': 'MI 5',
            'app_id': 'ru.yandex.searchplugin.dev',
            'uuid': '11111111111111111111111111111111',
            'size': '1080,1920',
            'os_version': '6.0',
            'lang': 'ru-RU',
            'app_build_number': '1',
            'afisha_version': '3',
            'manufacturer': 'Xiaomi',
            'poiy': '1350',
            '_cacheResourcesFlag': 1
        },
        androidOld: {
            'app_version_name': '5.70',
            'app_version': '5070000',
            'app_platform': 'android',
            'dp': '1.5',
            'did': '22222222222222222222222222222222',
            'model': 'GT-I9100',
            'app_id': 'ru.yandex.searchplugin.dev',
            'uuid': '11111111111111111111111111111111',
            'size': '480,800',
            'os_version': '4.0.4',
            'lang': 'ru-RU',
            'app_build_number': '1',
            'afisha_version': '3',
            'manufacturer': 'samsung',
            'poiy': '600',
            '_cacheResourcesFlag': 1
        },
        apadNew: {
            'app_version_name': '5.70',
            'app_version': '5070000',
            'app_platform': 'apad',
            'dp': '2.0',
            'did': '22222222222222222222222222222222',
            'model': 'SM-T719',
            'app_id': 'ru.yandex.searchplugin.dev',
            'uuid': '11111111111111111111111111111111',
            'size': '960,2000',
            'os_version': '6.0.1',
            'lang': 'ru-RU',
            'app_build_number': '28342',
            'afisha_version': '3',
            'manufacturer': 'samsung',
            'poiy': '1200',
            '_cacheResourcesFlag': 1
        },
        ios: {
            'app_version_name': '3.10',
            'app_version': '3010000',
            'app_platform': 'iphone',
            'dp': '2.0',
            'did': '22222222-2222-2222-2222-222222222222',
            'model': 'iPhone9%2C3',
            'app_id': 'ru.yandex.mobile',
            'uuid': '11111111111111111111111111111111',
            'size': '750.0%2C1334.0',
            'os_version': '10.1.1',
            'lang': 'ru-RU',
            'app_build_number': '1',
            'afisha_version': '3',
            'manufacturer': 'Apple',
            'poiy': '937.5',
            '_cacheResourcesFlag': 1
        },
        mock: {
            'webcard': 2,
            'assist': 'traffic',
            'usemock': '58d9132b60b2bfa9fcdc077e',
            '_cacheResourcesFlag': 1
        },
        custom: {
        }
    };

    this.paramsVisible = false;

    // с какими параметрами отправлять POST запрос
    this.params = '';
    this.resources = [];
    this.blocks = [];
}

Viewer.prototype.loadEnv = function() {
    this.env = localStorage.appsEnv || this.env;

    localStorage.removeItem('home:appAPI_hidden');

    var options = [];

    for (var envName in this.urls) {
        if (this.urls.hasOwnProperty(envName)) {
            options.push('<option value="' + envName + '">' + envName + '</option>');
        }
    }

    $('.select-env').append(options.join(''));

    var self = this;

    $('.select-env option').each(function() {
        this.selected = (this.value === self.env);
    });

    $('.select-env').on('change', function() {
        self.env = this.value;

        self.saveEnv();

        self.get();
    });

    $('.settings-go').click(function() {
        self.get();
    });

    $('.settings-reload').click(function() {
        self.get(true);
    });

    $('.settings-vi').click(function() {
        self.paramsVisible = !self.paramsVisible;
        self.updateParamsField();
    });
};

Viewer.prototype.saveEnv = function() {
    localStorage.appsEnv = this.env;
};

Viewer.prototype.loadDevice = function() {
    this.device = localStorage.appsDevice || this.device;
    this.loadParams(true);

    var options = [];

    for (var deviceName in this.userDevices) {
        if (this.userDevices.hasOwnProperty(deviceName)) {
            options.push('<option value="' + deviceName + '">' + deviceName + '</option>');
        }
    }

    $('.select-device').append(options.join(''));

    var self = this;

    $('.select-device option').each(function() {
        this.selected = (this.value === self.device);
    });

    $('.select-device').on('change', function() {
        self.device = this.value;

        self.loadParams();
        self.saveDevice();

        self.get();
    });
};

Viewer.prototype.saveDevice = function() {
    localStorage.appsDevice = this.device;
};

Viewer.prototype.loadParams = function(firstTime) {
    if (this.device !== 'custom' && this.userDevices[this.device]) {
        this.params = JSON.parse(JSON.stringify(this.userDevices[this.device]));
    } else {
        // если что-то переименуюется
        if (firstTime && this.device !== 'custom') {
            this.fixDevice();
        }

        if (firstTime) {
            this.params = localStorage.appsParams ? JSON.parse(localStorage.appsParams) : '';
        }

        // нет значения в ls или апдейт значения из селектора
        if (!this.params || !firstTime) {
            this.params = JSON.parse(JSON.stringify(this.requiredParams));
        }
    }

    this.saveParams();

    this.checkParamsField(firstTime);
    this.updateParamsField();
};

Viewer.prototype.fixDevice = function() {
    this.device = 'custom';
    this.saveDevice();

    $('.select-device').val('custom');
};

// надо ли держать поле с переметрами открытым
Viewer.prototype.checkParamsField = function(firstTime) {
    if (firstTime) {
        this.paramsVisible = false;

        return;
    }

    if (this.device === 'custom') {
        this.paramsVisible = true;

        return;
    }
};

Viewer.prototype.updateParamsField = function() {
    $('.settings__area')
        .val(this.paramsToText());

    if (this.paramsVisible) {
        $('.settings__area').removeClass('hidden');
    } else {
        $('.settings__area').addClass('hidden');
    }

    if (this.paramsVisible) {
        $('.settings__area').focus();
    }
};

Viewer.prototype.paramsToText = function() {
    return this.concatParams().replace(/&/g, '\n');
};

Viewer.prototype.textToParams = function() {
    return this.parseParams($('.settings__area').val().split('\n'));
};

Viewer.prototype.saveParams = function() {
    localStorage.appsParams = JSON.stringify(this.params);
};

Viewer.prototype.listenEvents = function() {
    var self = this;

    window.addEventListener('message', function(event) {
        var type = event.data.type,
            name = event.data.id,
            params = event.data.params;

        if (type === 'setHeight') {
            self.setIframeHeight(name, params);
        }
    }, false);
};

Viewer.prototype.setIframeHeight = function(name, params) {
    $('#' + name + ' iframe').css({height: params[0]});
};

Viewer.prototype.getUrl = function() {
    return this.urls[this.env] + '?' + this.concatParams();
};

Viewer.prototype.concatParams = function(customParams) {
    var res = [],
        params = customParams || this.params;

    for (var name in params) {
        if (params.hasOwnProperty(name)) {
            res.push(name + '=' + params[name]);
        }
    }

    return res.join('&');
};

Viewer.prototype.parseParams = function(arr) {
    var params = {},
        str;

    for (var i = 0, l = arr.length; i < l; i++) {
        str = arr[i].split('=');

        if (str.length === 2) {
            params[str[0]] = str[1];
        }
    }

    return params;
};

Viewer.prototype.checkParams = function() {
    var params = this.textToParams();

    if (this.concatParams(this.params) !== this.concatParams(params)) {
        this.fixDevice();

        this.params = params;
        this.saveParams();

        this.updateParamsField();
    }
};

Viewer.prototype.get = function(useData) {
    var self = this;

    this.checkParams();

    $.ajax(this.getUrl(), {
        method: 'POST',
        data: 'cached_resources=' + encodeURIComponent(JSON.stringify({
            'resources': useData ? this.resources : [],
            'webcards': this.blocks
        })) + (useData ? '&hidden=' + encodeURIComponent(this.getHiddenBlocks()) : ''),
        processData: false,
        dataType: 'json'
    }).done(function(response) {
        self.draw(response.block.filter(function(el) {
            return el.type === 'webcard';
        }), useData);
    });
};

Viewer.prototype.getHiddenBlocks = function() {
    return (localStorage.getItem('home:appAPI_hidden') || '');
};

Viewer.prototype.draw = function(webcards, useData) {
    if (!useData) {
        this.resources = [];
        this.blocks = [];
    }

    for (var i = 0, l = webcards.length; i < l; i++) {
        this.drawCard(webcards[i].id, webcards[i].data, useData);
    }
};

Viewer.prototype.drawCard = function(webcardId, webcard, useData) {
    if (!useData) {
        this.blocks.push({
            id: webcardId,
            url: webcard.html.url
        });
    }

    var preResources = [];

    for (var i = 0, l = webcard.resources.length; i < l; i++) {
        if (!useData) {
            this.resources.push(webcard.resources[i].url);
        }
        preResources.push('<div class="card__resource">' + '[' + webcard.resources[i].content.length + ']' + ' ' + webcard.resources[i].url + '</div>');
    }

    var href = this.urls[this.env] + webcardId + '?webcard=1&' + this.concatParams() + (useData ? '&hidden=' + encodeURIComponent(this.getHiddenBlocks()) : ''),
        card =  $('<div class="card" id=' + webcardId + '>' +
                    '<div class="card__link b-inline"><a href="' + href + '" class="link">Open</a></div>' +
                    '<div class="card__link b-inline"><a href="' + href + '&cleanvars=1" class="link">Cleanvars</a></div>' +
                    '<iframe class="card__iframe" src="' + href + '"></iframe>' +
                    '<div class="card__info"><pre></pre></div>' +
                    '<div class="card__resources"></div>' +
                '</div>'),
        dataPass = false;

    if ($('#' + webcardId).length) {
        if (webcard.html && webcard.html.content) {
            $('#' + webcardId).replaceWith(card);
        } else {
            // data pass
            card = $('#' + webcardId);

            dataPass = true;
        }
    } else {
        $('.cards').append(card);
    }

    var iframe = $('.card__iframe', card);

    if (webcard.height) {
        iframe.css({height: webcard.height});
    }

    if (dataPass && webcard.data) {
        if (iframe[0].contentWindow.window.onData) {
            iframe[0].contentWindow.window.onData(webcard.data);
        }
    }

    $('.card__resources', card).html(preResources.join(''));

    var info = JSON.parse(JSON.stringify(webcard));
    delete info.html;
    delete info.resources;

    $('.card__info pre', card).html(JSON.stringify(info, null, 4));
};

Viewer.prototype.init = function() {
    this.loadEnv();
    this.loadDevice();

    this.listenEvents();

    this.get();
};
