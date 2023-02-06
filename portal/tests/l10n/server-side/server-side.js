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

export function localeArray(data, req) {
    return `<div>
        Здесь должен быть перевод из танкера
        <span class="locale__test">${req.l10n('array').join('-')}</span>
    </div>`;
}