/* eslint no-console:1 */
(function () {
    const container = document.querySelector('.container'),
        libContainer = document.querySelector('#morda-lib'),
        form = document.querySelector('form'),
        resetButton = document.querySelector('.reset-button'),
        cookieChanger = document.querySelector('.cookie-changer'),
        isHermione = /\bHermione\//.test(navigator.userAgent);
    if (isHermione) {
        document.body.classList.add('hermione');
    }

    const getFormFields = (form) => {
        return Array.from(form.querySelectorAll('select,input,map-element'))
            .filter(({type, name}) => type !== 'submit' && name);
    };

    const inputs = getFormFields(document.querySelector('form'));
    let params = {},
        events = new EventTarget();

    function setParamValue(name, value) {
        if (params[name] === value) {
            return;
        }
        params[name] = value;

        if (name === 'tablo2021') {
            tablo2021Change(value);
        }

        localStorage.setItem('lastCreatingFormValues', JSON.stringify(params));
        let query = new URLSearchParams();
        for (let key in params) {
            if (params.hasOwnProperty(key)) {
                let value = params[key];
                if (value || value === 0) {
                    if (typeof value === 'object') {
                        value = JSON.stringify(value);
                    }
                    query.set(key, value);
                }
            }
        }
        history.replaceState(null, null, location.origin + location.pathname + '?' + query.toString());

        events.dispatchEvent(new CustomEvent(name, {detail: value}));
        console.debug(`Изменен параметр ${name}`, value, params);
    }

    function getParamValue(name) {
        return params[name];
    }

    // Для гермионных тестов
    window.setParamValue = setParamValue;
    window.getParamValue = getParamValue;

    function getInputValue(input) {
        switch (input.type) {
            case 'checkbox': return !!input.checked;
            case 'number': return parseInt(input.value, 10);
            default: return input.value;
        }
    }

    events.addEventListener('tabloItems', ({detail}) => {
        setTabloItemCount(detail);
    });

    function setContainerClassnames() {
        container.className = `container container_page_${params.pageMode} container_width_${params.tabloSize}`;
    }

    let oldOffset = null;
    function updateOffset() {
        let newValue = (window.Morda.lib && window.Morda.lib.getScrollOffset() || 0) +
            libContainer.offsetTop;
        if (newValue !== oldOffset) {
            oldOffset = newValue;
        }
    }

    function onScroll() {
        updateOffset();
        if (window.scrollY > oldOffset) {
            setParamValue('pageMode', 'tab');
        } else {
            setParamValue('pageMode', 'custo');
        }
    }

    function toggleAutoPageMode() {
        const value = params.autoPageMode,
            select = document.querySelector('select[name=pageMode]');

        if (!value) {
            select.removeAttribute('disabled');
            window.removeEventListener('resize', updateOffset);
            window.removeEventListener('scroll', onScroll);
            return;
        }

        select.setAttribute('disabled', 'disabled');

        window.addEventListener('resize', updateOffset);
        window.addEventListener('scroll', onScroll);
        updateOffset();
    }

    events.addEventListener('autoPageMode', toggleAutoPageMode);
    events.addEventListener('tabloSize', setContainerClassnames);
    events.addEventListener('pageMode', setContainerClassnames);
    events.addEventListener('theme', ({detail}) => {
        document.body.classList.toggle('dark-theme', detail === 'dark');
    });

    // Все подписки на события выше
    inputs.forEach(input => {
        input.addEventListener('change', () => {
            let value = getInputValue(input);

            setParamValue(input.name, value);
        });

        events.addEventListener(input.name, ({detail: value}) => {
            let inputValue = getInputValue(input);
            if (value !== inputValue) {
                if (input.type === 'checkbox') {
                    input.checked = value;
                } else {
                    input.value = value;
                }
            }
        });
    });

    function tablo2021Change(value) {
        document.querySelector('.morda-enabled').style.display = value ? 'none' : '';
        document.querySelector('.zen-view-mode').style.display = value ? '' : 'none';
        document.querySelector('.topnews-enabled').style.display = value ? '' : 'none';
    }

    function onRedrawOneFrameNeeded() {
        console.debug('onRedrawOneFrameNeeded');
    }

    function onScrollNeeded() {
        console.debug('onScrollNeeded');
        document.scrollingElement.scrollTop = 0;
    }

    function initByQueryParams() {
        let search = location.search;

        if (!search) {
            return;
        }

        let query = new URLSearchParams(search);

        for (let [key, value] of query.entries()) {
            try {
                setParamValue(key, JSON.parse(decodeURIComponent(value)));
            } catch (e) {
                setParamValue(key, value);
            }
        }
        return true;
    }

    function initByLocalStorage() {
        let savedParams = localStorage.getItem('lastCreatingFormValues');
        if (savedParams) {
            savedParams = JSON.parse(savedParams);
            for (let key in savedParams) {
                if (savedParams.hasOwnProperty(key)) {
                    setParamValue(key, savedParams[key]);
                }
            }
            return true;
        }
    }

    function fillDefaultParams() {
        const defs = {
            mordaUrlBase: `https://${location.hostname}`,
            history: '',
            mordaEnabled: true,
            zenEnabled: true,
            pageVisible: true,
            pageMode: 'custo',
            zenViewMode: 'full',
            topnewsEnabled: true,
            theme: 'light',
            tabloSize: 'auto',
            tabloItems: 3,
            zenLibEnv: 'stable',
            tablo2021: false,
            zenParams: {},
            browserExperiments: {},
            hideNtpFeed: false,
            bannerEnabled: true
        };
        for (let key in defs) {
            if (!(key in params)) {
                setParamValue(key, defs[key]);
            }
        }
    }

    function tryCreateMordaLib() {
        const required = [
                'mordaUrlBase',
                'mordaEnabled',
                'zenEnabled',
                'pageVisible',
                'pageMode',
                'theme',
                'browserExperiments',
                'history',
                'zenParams',
                'zenLibEnv',
                'tablo2021',
                'zenViewMode',
                'topnewsEnabled',
                'hideNtpFeed',
                'bannerEnabled'
            ],
            libParams = {};

        for (let key of required) {
            if (key in params) {
                libParams[key] = params[key];
            } else {
                return false;
            }
        }

        libParams.browserExperiments = new Map(Object.entries(libParams.browserExperiments));

        window.Morda.create({
            ...libParams,
            container: libContainer,
            onRedrawOneFrameNeeded,
            onScrollNeeded
        }).then(mordaLib => {
            toggleEditMode(true);
            document.body.classList.add('test-page_lib_loaded');
            [
                'mordaEnabled',
                'zenEnabled',
                'pageVisible',
                'pageMode',
                'theme',
                'history',
                'zenParans',
                'zenViewMode',
                'topnewsEnabled'
            ].forEach(name => {
                events.addEventListener(name, ({detail}) => {
                    let methodName = 'set' + name[0].toUpperCase() + name.slice(1);
                    if (!(methodName in mordaLib)) {
                        throw new Error(`no method ${methodName} in mordalib`);
                    }
                    mordaLib[methodName](detail);
                });
            });
        });
    }

    function init() {
        if (initByQueryParams() || initByLocalStorage()) {
            fillDefaultParams();
            tryCreateMordaLib();
        } else {
            fillDefaultParams();
        }
    }

    function reset() {
        localStorage.removeItem('lastCreatingFormValues');
        const {origin, pathname} = window.location;
        const url = `${origin}${pathname}`;
        window.open(url, '_self');
    }

    init();

    toggleEditMode();

    function toggleEditMode(inEditMode = false) {
        const creation = document.querySelectorAll('.creation-param'),
            edit = document.querySelectorAll('.edit-param');

        (inEditMode ? creation : edit).forEach(elem => elem.setAttribute('disabled', 'disabled'));
        (inEditMode ? edit : creation).forEach(elem => elem.removeAttribute('disabled'));
    }


    function getTabloItemCount() {
        return document.querySelectorAll('.tablo-item:not(.tablo-item-add)').length;
    }
    function setTabloItemCount(count) {
        const existing = document.querySelectorAll('.tablo-item:not(.tablo-item-add)');

        if (existing.length === count) {
            return;
        }
        let parent = document.querySelector('.tablo');
        if (existing.length > count) {
            for (let i = count; i < existing.length; i++) {
                parent.removeChild(existing[i]);
            }
        } else {
            for (let i = existing.length; i < count; i++) {
                const newNode = document.createElement('div');
                newNode.className = 'tablo-item';
                parent.prepend(newNode);
            }
        }
        setParamValue('tabloItems', count);
    }

    function onTabloElemClick(e) {
        if (!e.target.classList.contains('tablo-item')) {
            return;
        }
        const isAddition = e.target.classList.contains('tablo-item-add');
        let count = getTabloItemCount() + (isAddition ? 1 : -1);
        setTabloItemCount(count);
    }

    document.querySelector('.tablo')
        .addEventListener('click', onTabloElemClick);

    cookieChanger.addEventListener('click', () => {
        window.Morda.lib.setCookie();
    });

    resetButton.addEventListener('click', reset);
    form.addEventListener('submit', e => {
        e.preventDefault();
        if (window.Morda.lib) {
            location.reload();
        } else {
            tryCreateMordaLib();
        }
    });
})();
