export function locale(data, req) {
    return `<div>
        Здесь должен быть перевод из танкера
        <span class="locale__test">${req.l10n('test')}</span>
    </div>`;
}

export function localeNested(data, req) {
    return `<div>
        Здесь должен быть перевод из танкера
        <span class="locale__test">${req.l10n('nested.test')}</span>
    </div>`;
}

export function localeEval(data, req) {
    const a = 'test';
    return `<div>
        Здесь должен быть перевод из танкера
        <span class="locale__test">${req.l10n('eval.' + a)}</span>
    </div>`;
}

export function localeArray(data, req) {
    return `<div>
        Здесь должен быть перевод из танкера
        <span class="locale__test">${req.l10n('array').join('-')}</span>
    </div>`;
}

export function localeCondition(data, req) {
    function getTr (val) {
        return req.l10n(`condition.${val ? 'test1' : 'test2'}`);
    }

    return `<div>
        Здесь должен быть перевод из танкера
        <span class="locale__test">${getTr(data.val)}</span>
    </div>`;
}


export function localeNotExist(data, req) {
    return `<div>
        Здесь должен быть перевод из танкера
        <span class="locale__test">${req.l10n('NotExistKey')}</span>
    </div>`;
}

export const localeClient = (data) => {
    return `<div>
        Здесь должен быть перевод из танкера
        <span class="locale__test">${data.client}</span>
    </div>`;
};

export const localeNestedDepth = (data, req) => {
    const one = 'one';
    return `<div>
        Здесь должен быть перевод из танкера
        <span class="locale__test">${req.l10n('nestedDepthTest.' + one) + req.l10n('nestedDepthTest.two')}</span>
    </div>`;
};
