/* eslint-env es6 */
/* eslint dot-notation: 0 */
/* eslint no-console: 0 */

let tree = {};
let dataList = [];
let defaultState = {
    path: '/',
    mode: 'explore',
    searchString: ''
};
let state = Object.assign({}, defaultState);
let pollingTasks = {};

const POLLING_INTERVAL = 1000;

function initData (data) {
    function appendItem (parts, to) {
        let first = parts.shift();

        if (!(first in to)) {
            to[first] = {
                children: {},
                isTest: parts.length === 0
            };
        }

        if (parts.length) {
            appendItem(parts, to[first].children);
        }
    }

    data.forEach(block => {
        let parts = block.split('/');

        appendItem(parts, tree);
    });

    dataList = data;
}

function initViewer (data) { // eslint-disable-line
    initData(data);
    updateContents(false);
    bindEvents();
    onPopState();
}

function updateContents (animate) {
    pollingTasks = {};
    updatePath();
    drawItems(animate);
}

let prevMode = state.mode;
function updateHash () {
    let obj = {
        mode: state.mode !== 'explore' ? state.mode : '',
        path: state.path !== '/' ? state.path : '',
        searchString: state.searchString
    };
    let replace = prevMode === state.mode && state.mode === 'search';
    prevMode = state.mode;

    let hash = Object.keys(obj)
        .reduce((acc, item) => {
            if (obj[item]) {
                acc.push(`${encodeURIComponent(item)}=${encodeURIComponent(obj[item])}`);
            }

            return acc;
        }, [])
        .join('&');

    let pagePath = window.location.href,
        hashIndex = pagePath.indexOf('#');

    if (hashIndex > -1) {
        pagePath = pagePath.substr(0, hashIndex);
    }
    window.history[replace ? 'replaceState' : 'pushState']({}, document.title, pagePath + (hash ? ('#' + hash) : ''));
}

function onPopState () {
    let obj = Object.assign({}, defaultState);

    window.location.hash.substr(1)
        .split('&')
        .forEach((item) => {
            let pair = item.split('='),
                name = decodeURIComponent(pair[0]),
                val = decodeURIComponent(pair[1]);

            if (name) {
                obj[name] = val;
            }
        });

    let hasDiff = false;
    for (let key in obj) {
        if (obj.hasOwnProperty(key) && obj[key] !== state[key]) {
            hasDiff = true;
        }
    }

    if (hasDiff) {
        state = obj;
        document.querySelector('.search__input').value = state.searchString;

        updateContents();
    }
}

function updatePath () {
    let dom = document.querySelector('.path');

    if (state.mode === 'explore') {
        let items = state.path.slice(1).split('/').filter(Boolean);

        items.unshift('/');

        dom.innerHTML = items.map((item, index) => {
            let itemPath = index === 0 ? '/' : '/' + items.slice(1, index + 1).join('/');

            return `<div class="path__item" title="${itemPath}" data-path="${itemPath}">${item}</div>`;
        }).join('');
    } else if (state.mode === 'search') {
        dom.innerHTML = '<div class="path__clear">Exit search</div>';
    }
}

function findItems (path) {
    let localPath = path.substr(1);

    if (localPath.endsWith('/')) {
        localPath = localPath.substr(0, localPath.length - 1);
    }

    if (!localPath) {
        return tree;
    }

    function find (parts, tree) {
        let first = parts.shift();

        if (first in tree) {
            if (parts.length === 0) {
                return tree[first].children;
            } else {
                return find(parts, tree[first].children);
            }
        } else {
            return {};
        }
    }

    let parts = localPath.split('/');

    return find(parts, tree);
}

function match (str, pattern, offset) {
    let strPos = 0,
        patternPos = 0,
        matches = [];

    while (strPos < str.length && patternPos < pattern.length) {
        if (str[strPos] === pattern[patternPos]) {
            matches.push(strPos + offset);
            ++patternPos;
        }
        ++strPos;
    }

    return patternPos >= pattern.length ? matches : null;
}

function bestMatch (str, pattern) {
    if (!match(str, pattern)) {
        return null;
    }

    let bestScore = Infinity;
    let bestMatch = null;
    for (let i = 0; i < str.length; ++i) {
        let matched = match(str.substr(i), pattern, i);
        let score = calcSearchSortOrder(matched);

        if (!matched) {
            break;
        }

        if (score < bestScore) {
            bestScore = score;
            bestMatch = matched;
        }
    }

    return {
        match: bestMatch,
        order: bestScore
    };
}

function calcSearchSortOrder (match) {
    if (!match) {
        return Infinity;
    }

    let sum = 0;

    for (let i = 1; i < match.length; ++i) {
        let dist = match[i] - match[i - 1] - 1;
        sum += dist * dist;
    }

    return sum;
}

function searchItems (searchString) {
    return dataList
        .map(item => {
            let {match, order} = bestMatch(item, searchString) || {};

            return {
                name: item,
                children: [],
                match: match,
                order: order
            };
        })
        .filter(item => item.match)
        .sort((a, b) => a.order - b.order)
        .reduce((acc, item) => {
            acc[item.name] = item;

            return acc;
        }, {});
}

function findItem (path) {
    let localPath = path.startsWith('/') ? path.substr(1) : path;

    if (localPath.endsWith('/')) {
        localPath = localPath.substr(0, localPath.length - 1);
    }

    if (!localPath) {
        return tree;
    }

    function find (parts, tree) {
        let first = parts.shift();

        if (first in tree) {
            if (parts.length === 0) {
                return tree[first];
            } else {
                return find(parts, tree[first].children);
            }
        } else {
            return null;
        }
    }

    let parts = localPath.split('/');

    return find(parts, tree);
}

function calcBlocks (item) {
    let sum = 0;

    if (item.isTest) {
        ++sum;
    }

    Object.keys(item.children).forEach(child => {
        sum += calcBlocks(item.children[child]);
    });

    return sum;
}

function drawItems (animate) {
    function joinChildren (item, children) {
        let keys = Object.keys(children);

        if (keys.length === 1) {
            item += '/' + keys[0];

            item = joinChildren(item, children[keys[0]].children);
        }

        return item;
    }

    let items;
    if (state.mode === 'explore') {
        items = findItems(state.path);
    } else {
        items = searchItems(state.searchString);
    }
    let dom = document.querySelector('.items');

    let page = document.createElement('div');
    page.className = 'items__page' + (animate !== false ? ' items__page_animated' : '');
    page.innerHTML = Object.keys(items).map(item => {
        let itemRoot = items[item];
        let blocks = calcBlocks(itemRoot);
        let children = itemRoot.children;
        let visibleName;

        let joinedItem = joinChildren(item, children);
        let itemObj;
        if (state.mode === 'explore') {
            itemObj = findItem(joinPath(state.path, joinedItem));
        } else {
            itemObj = findItem(joinedItem);
        }

        if (state.mode === 'explore') {
            visibleName = joinedItem;
            if (visibleName.includes('/')) {
                let index = visibleName.indexOf('/');
                visibleName = visibleName.substr(0, index) + '<span class="item__title_suffix">' + visibleName.substr(index) + '</span>';
            }
        } else {
            visibleName = '';
            let prevIndex = 0;

            for (let i = 0; i < itemRoot.match.length; ++i) {
                visibleName += '<span class="item__title_suffix">';
                visibleName += joinedItem.substring(prevIndex, itemRoot.match[i]);
                visibleName += '</span>';
                visibleName += joinedItem[itemRoot.match[i]];
                prevIndex = itemRoot.match[i] + 1;
            }

            visibleName += '<span class="item__title_suffix">';
            visibleName += joinedItem.substring(itemRoot.match[itemRoot.match.length - 1] + 1);
            visibleName += '</span>';
        }

        if (itemObj.isTest) {
            return `<div class="item item_test" data-name="${joinedItem}" data-test="1">
                        <div class="item__top">
                            <div class="item__title">${visibleName}</div>
                            <div class="item__info">test</div>
                        </div>
                        <div class="item__content"></div>
                        <div class="item__run-content"></div>
                    </div>`;
        } else {
            return `<div class="item" data-name="${joinedItem}">
                        <div class="item__top">
                            <div class="item__title">${visibleName}</div>
                            <div class="item__info">${blocks} ${blocks === 1 ? 'block' : 'blocks'}</div>
                        </div>
                    </div>`;
        }
    }).join('');

    let lastChild = dom.lastChild;
    if (lastChild) {
        lastChild.addEventListener('animationend', () => {
            lastChild.remove();
        });
        lastChild.classList.add('items__page_hidden');
    }
    dom.appendChild(page);
}

function joinPath (path, append) {
    return path + (path.endsWith('/') ? '' : '/') + append;
}

function appendPath (name) {
    let items = findItems(state.path);
    let firstPart = name.split('/')[0];

    if (firstPart in items) {
        state.path = joinPath(state.path, name);
        updateContents();
        updateHash();
    }
}

function buildTestUrl (views, blockPath, dataName, project) {
    return `/?datafile=${blockPath.replace(/^\//, '')}&dataname=${dataName}&project=${project}`;
}

/*function buildGeminiRunCommand (blockPath) {
    let subRoot = blockPath.split('/')[0];

    return `make -C tmpl/${subRoot} GEMINI_BLOCK=${blockPath} gemini`;
}*/

/*function buildGeminiUpdateCommand (blockPath) {
    let subRoot = blockPath.split('/')[0];

    return `make -C tmpl/${subRoot} GEMINI_BLOCK=${blockPath} gemini-update`;
}*/

function loadTest (item) {
    let name = item.dataset.name,
        content = item.querySelector('.item__content'),
        joinedPath = state.mode === 'explore' ? joinPath(state.path, name).slice(1) : name;

    if (item.classList.contains('item_progress') || item.classList.contains('item_loaded')) {
        return;
    }
    item.classList.remove('item_error');
    item.classList.add('item_progress');
    content.innerHTML = '';

    fetch('/tests-api/?method=getBlockInfo&blockPath=' + encodeURIComponent(joinedPath))
        .then(res => res.json())
        .then(json => {
            if (json.levels.length < 1) {
                throw new Error('Cannot find view level');
            }
            let dataList = '';

            const buttonsFor = (level, dataName) => (json.projects || ['']).map(project => {
                return `<a class="item__data-open" href="${buildTestUrl(level, joinedPath, dataName, project)}" target="_blank" rel="noopener">Open ${project}</a>`;
            }).join('');


            if (json.levels.length === 1) {
                dataList = json.data.map(dataName => `
                    <div class="item__data-row">
                        <div class="item__data-name">${dataName}</div>
                            ${buttonsFor(json.levels[0], dataName)}
                        </div>
                    `).join('');
            } else {
                json.levels.forEach(level => {
                    dataList += json.data.map(dataName => `
                        <div class="item__data-row">
                            <div class="item__data-name">${level} : ${dataName}</div>
                                ${buttonsFor(level, dataName)}
                            </div>
                        `).join('');
                });
            }

            content.innerHTML = `
                <div class="item__data">
                    <div class="item__data-title">Data</div>
                    ${dataList}` +
            /* `<div class="item__data-title">Commands</div>
                    <div class="item__data-row">
                        <div class="item__data-name">${buildGeminiRunCommand(joinedPath)}</div>
                        <button class="item__data-open" data-copy>Copy</button>
                        <button class="item__data-open" data-run>Run</button>
                        <button class="item__data-open" data-update>Update</button>
                    </div>` + */
                `</div>
            `;

            item.classList.remove('item_progress');
            item.classList.add('item_loaded');
        })
        .catch(err => {
            console.error(err);
            item.classList.remove('item_progress');
            item.classList.add('item_error');
            content.textContent = String(err);
        });
}

function bindEvents () {
    document.querySelector('.items').addEventListener('click', function (event) {
        let item = event.target.closest('.item'),
            copy = event.target.closest('[data-copy]'),
            run = event.target.closest('[data-run]'),
            update = event.target.closest('[data-update]'),
            outToggle = event.target.closest('[data-out-toggle]');

        if (item) {
            if (copy) {
                onCopyClick(copy);
            } else if (run || update) {
                onRunClick(item, !!update);
            } else if (outToggle) {
                onOutToggleClick(item);
            } else {
                onItemClick(item);
            }
        }
    });
    document.querySelector('.path').addEventListener('click', function (event) {
        let item = event.target.closest('.path__item'),
            clear = event.target.closest('.path__clear');
        if (item) {
            onPathClick(item);
        } else if (clear) {
            onPathClearClick();
        }
    });
    document.querySelector('.search__input').addEventListener('input', function (event) {
        let val = event.target.value;

        state.searchString = val;
        if (val) {
            state.mode = 'search';
        } else {
            state.mode = 'explore';
        }
        updateContents();
        updateHash();
    });

    window.addEventListener('popstate', onPopState);
}

function onItemClick (item) {
    if (item.dataset.test) {
        loadTest(item);
    } else {
        appendPath(item.dataset.name);
    }
}

function onPathClick (item) {
    if (state.path !== item.dataset.path) {
        state.path = item.dataset.path;
        updateContents();
        updateHash();
    }
}

function onCopyClick (copyButton) {
    let text = copyButton.previousElementSibling;
    let range = document.createRange();
    range.selectNodeContents(text);
    let sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);

    document.execCommand('copy');
}

function onPathClearClick () {
    state.mode = 'explore';
    state.searchString = '';
    let input = document.querySelector('.search__input');
    input.value = '';
    updateContents();
    updateHash();
    input.focus();
}

function onRunClick (item, update) {
    let name = item.dataset.name,
        content = item.querySelector('.item__run-content'),
        joinedPath = state.mode === 'explore' ? joinPath(state.path, name).slice(1) : name;

    item.querySelectorAll('[data-run], [data-update]').forEach(button => {
        button.disabled = true;
    });

    item.classList.add('item_progress');
    item.classList.remove('item_error');

    content.innerHTML = '';

    fetch(`/tests-api/?method=runTest&blockPath=${encodeURIComponent(joinedPath)}&update=${update ? 1 : 0}`)
        .then(res => res.json())
        .then(json => {
            if (json.error) {
                throw json.error;
            }

            startPolling(joinedPath, item);
        })
        .catch(err => {
            console.error(err);
            item.classList.remove('item_progress');
            item.classList.add('item_error');
            content.textContent = String(err);

            item.querySelectorAll('[data-run], [data-update]').forEach(button => {
                button.disabled = false;
            });
        });
}

function startPolling (blockPath, item) {
    pollingTasks[blockPath] = {
        start: Date.now(),
        item
    };

    if (Object.keys(pollingTasks).length === 1) {
        setTimeout(runPollingRequests, POLLING_INTERVAL);
    }
}

function showItemResult (item, out, err, reportUrl) {
    item.classList.remove('item_progress');
    item.classList.toggle('item_error', !!err);

    item.querySelectorAll('[data-run], [data-update]').forEach(button => {
        button.disabled = false;
    });

    let content = item.querySelector('.item__run-content');
    content.innerHTML = `
        <div class="item__out">
            <div class="item__out-top">
                <div class="item__out-title">${err ? 'Failed' : 'Ok'}</div>
                <button class="item__data-open" data-out-toggle>Toggle log</button>
                ${reportUrl ? `<a class="item__data-open" href="${reportUrl}?rnd=${Date.now()}" target="_blank" rel="noopener">Open report</a>` : ''}
            </div>
            <div class="item__out-log">${out + err}</div>
        </div>
    `;
}

function runPollingRequests () {
    Object.keys(pollingTasks).forEach(name => {
        let obj = pollingTasks[name],
            item = obj.item;

        if (Date.now() - obj.start > 1000 * 60 * 5) {
            delete pollingTasks[name];
        } else {
            fetch('/tests-api/?method=retrieveTaskInfo&blockPath=' + encodeURIComponent(name))
                .then(res => res.json())
                .then(json => {
                    if (json.error) {
                        throw json.error;
                    }

                    if (json.finished) {
                        showItemResult(item, json.stdout, json.stderr, json.reportUrl);

                        delete pollingTasks[name];
                    }
                })
                .catch(err => {
                    console.error(err);
                    showItemResult(item, '', String(err), null);
                    delete pollingTasks[name];
                });
        }
    });

    if (Object.keys(pollingTasks).length > 0) {
        setTimeout(runPollingRequests, POLLING_INTERVAL);
    }
}

function onOutToggleClick (item) {
    let out = item.querySelector('.item__out-log');

    if (out) {
        out.classList.toggle('item__out-log_visible');
    }
}
