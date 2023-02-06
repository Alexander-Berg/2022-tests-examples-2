/* eslint-disable max-len */

const index = require('./mocks/index'),
    more = require('./mocks/more'),
    promo = require('./mocks/promo'),
    dark = require('./mocks/dark'),
    noSort = require('./mocks/noSort'),
    stripe = require('./mocks/stripe'),
    noSortStripe = require('./mocks/noSortStripe'),
    business = require('./mocks/business');

function wrap(content) {
    return `
        <script>window.localStorage['home:servicesNewPromoShowed.travel'] = 1</script>
        <style>
            [class][class].services-new__icon,
            [class][class].services-new-more__icon {
                background-image: url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KIDxnPgogIDxlbGxpcHNlIHN0cm9rZT0ibnVsbCIgcnk9IjQzLjMzMzMzNCIgcng9IjQzLjMzMzMzNCIgaWQ9InN2Z185IiBjeT0iNTAiIGN4PSI1MCIgZmlsbC1vcGFjaXR5PSJudWxsIiBzdHJva2Utb3BhY2l0eT0ibnVsbCIgc3Ryb2tlLXdpZHRoPSJudWxsIiBmaWxsPSIjRjAwIi8+CiAgPHBhdGggc3Ryb2tlPSJudWxsIiBpZD0ic3ZnXzYiIGZpbGw9IiNmZmZmZmYiIGQ9Im01NS4zNjE4MzksNTYuNzgwNTM2bDAsMjAuNTc5OTk0bDUuOTg2MTc0LDBsMCwtNTQuNzIxMDY0bC04Ljk0MDM3MSwwYy04Ljc4MzM3MSwwIC0xNi4xNjgxNDQsNS45MzI4ODEgLTE2LjE2ODE0NCwxNy40OTMyODNjMCw4LjI0NzU1NCAzLjI2NTMxNywxMi43MTg0NiA4LjE2MjU3MiwxNS4xODQzNzJsLTEwLjQxNjc1LDIyLjA0MzQwOWw2LjkxODA5MywwbDkuNDgzMzksLTIwLjU3OTk5NGw0Ljk3NTAzNSwwem0tMC4wMTg3MjUsLTQuODAwNzVsLTMuMTg2MDk3LDBjLTUuMjA4Mzc1LDAgLTkuNDg0ODMxLC0yLjg1MTkzMSAtOS40ODQ4MzEsLTExLjcxNTk2M2MwLC05LjE3MDgzIDQuNjYzOTE1LC0xMi40NDQ3ODkgOS40ODQ4MzEsLTEyLjQ0NDc4OWwzLjE4NjA5NywwbDAsMjQuMTYwNzUyeiIvPgogPC9nPgo8L3N2Zz4=") !important;
            }

            .services-new__icon,
            .services-new-more__icons {
                transition: none !important;
            }

            .document_dark_yes body {
                background-color: #222229;
            }
        </style>
        <div class="wrap" style="padding: 50px 150px; margin: 0 auto;">${content}</div>`;
}

// more может изменяться в ходе тестирования, поэтому лучше его копировать
const copy = x => JSON.parse(JSON.stringify(x));

const addPromo = (obj) => {
    obj.Services_new = Object.assign({}, obj.Services_new, promo);

    return obj;
};

exports.main = execView => {
    return wrap(execView('ServicesNew', Object.assign({}, index)));
};
exports.mainPromo = execView => {
    return wrap(execView('ServicesNew', addPromo(Object.assign({}, index))));
};
exports.mainDark = (execView) => {
    return wrap(execView('ServicesNew', addPromo(Object.assign({}, index, dark))));
};

exports.more = execView => {
    return wrap(execView('ServicesNew', Object.assign({}, copy(more))));
};
exports.morePromo = execView => {
    return wrap(execView('ServicesNew', addPromo(Object.assign({}, copy(more)))));
};
exports.moreDark = (execView) => {
    return wrap(execView('ServicesNew', addPromo(Object.assign({}, copy(more), dark))));
};
exports.searchButton = execView => {
    return wrap(execView('ServicesNew', Object.assign({
        ab_flags: {
            services_new_search_button: {
                value: 1
            }
        },
        MordaZone: 'ru'
    }, index, copy(more))));
};
exports.searchButtonUa = execView => {
    return wrap(execView('ServicesNew', Object.assign({
        ab_flags: {
            services_new_search_button: {
                value: 1
            }
        },
        MordaZone: 'ua'
    }, index, copy(more))));
};
exports.moreNoSort = (execView) => {
    return wrap(execView('ServicesNew', Object.assign({}, copy(more), dark, noSort)));
};
exports.moreNoSortStripe = (execView) => {
    return wrap(execView('ServicesNew', Object.assign({}, copy(more), dark, noSortStripe)));
};
exports.moreStripe = (execView) => {
    return wrap(execView('ServicesNew', Object.assign({}, copy(more), dark, stripe)));
};
exports.business = (execView) => {
    return wrap(execView('ServicesNew', Object.assign({}, copy(business))));
};
exports.businessDark = (execView) => {
    return wrap(execView('ServicesNew', Object.assign({}, copy(business), dark)));
};
