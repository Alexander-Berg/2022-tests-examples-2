import './client-side.l10n.js';

export const getlocaleByKey = (key) => (data, req) => {
    return `<div>
        Здесь должен быть перевод из танкера
        <span class="locale__test">${req.l10n(key)}</span>
    </div>`;
};

export const localeExportArray = (data, req) => {
    const key = 'exportArray';
    return `<div>
        Здесь должен быть перевод из танкера
        <span class="locale__test">${req.l10n(key)[0] + ', ' + req.l10n(key)[1] + ', ' +req.l10n(key)[2]}</span>
    </div>`;
};
