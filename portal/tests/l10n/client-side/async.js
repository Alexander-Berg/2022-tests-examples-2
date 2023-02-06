export function localeAsync(data, req) {
    return `<div>
        Здесь должен быть перевод из танкера
        <span class="locale__test">${req.l10n('async')}</span>
    </div>`;
}
