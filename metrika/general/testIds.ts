const helpSelectors = {
    passport: {
        loginInput: '[name="login"]',
        passwordInput: '[name="passwd"]',
        submitButton: '[type="submit"]',
        skipButton: '[data-t="phone_skip"] button',
    },

    datePicker: {
        button: '.datepicker-custom-input-button',
        day: '.react-datepicker__day',
        select: '.datepicker-apply-button',
        popup: '.react-datepicker-popper',
    },

    lego: {
        button: '.button2',
    },
};

const testIds = {
    common: {
        spinner: 'common-spinner',
        searchSelect: {
            input: 'common-search-select',
            item: 'common-search-select-item',
            toggler: 'common-search-select-toggler',
            menu: 'common-search-select-menu',
        },
        baseSelect: {
            body: 'common-base-select-body',
            button: 'common-base-select-button',
            confirm: 'common-base-select-confirm',
        },
        modal: {
            confirm: 'common-modal-confirm',
        },
    },
    advertiser: {
        form: {
            nameInput: 'advertiser-form-name',
            postClickInput: 'advertiser-form-postClick',
            postViewInput: 'advertiser-form-postView',
            error: 'advertiser-form-error',
            changeWarning: 'advertiser-form-warning',
            saveButton: 'advertiser-form-save',
            deleteButton: 'advertiser-form-delete',
            confirmDelete: 'advertiser-form-confirm-delete',
        },
        page: {
            name: 'advertiser-page-name',
            headerMenu: 'advertiser-page-header-menu',
            rejectAccess: 'advertiser-page-reject-access',
            deleteAdvertiser: 'advertiser-page-delete-advertiser',
            confirmDelete: 'advertiser-page-confirm-delete',
        },
    },
    campaigns: {
        status: {
            button: 'campaigns-status-btn',
            item: 'campaigns-status-item',
        },
        table: {
            spinner: 'campaigns-table-spinner',
            body: 'campaigns-table',
        },
        item: {
            row: 'campaigns-item-row',
            copy: 'campaings-item-clone',
            menuButton: 'campaings-item-menu',
            name: 'campaigns-item-name',
        },
    },
    landings: {
        page: {
            createButton: 'landings-page-create',
            landingName: 'landings-page-name',
            landingUrl: 'landings-page-url',
            editButton: 'landings-page-edit',
        },
        form: {
            saveButton: 'landings-form-save',
            nameInput: 'landings-form-name',
            urlInput: 'landings-form-url',
            cancelButton: 'landings-form-cancel',
            deleteButton: 'landings-form-delete',
            confirmDeleteButton: 'landings-form-confirm-delete',
        },
    },
    placement: {
        name: 'placement-name',
        landing: 'placement-landing',
        landingNew: 'placement-new-landing',
        site: 'placement-site',
        volume: 'placement-volume',
        cost: 'placement-cost',
        saveButton: 'placement-save',
    },
    campaign: {
        summary: {
            menu: 'campaign-summary-menu',
            statusToggler: 'campaign-status-toggler',
            delete: 'campaign-delete',
            badge: 'campaign-summary-status',
        },
        edit: {
            next: 'campaign-next-page',
            save: 'campaign-save',
            previous: 'campaign-previous-page',
            delete: 'campaign-delete',
            description: {
                name: 'camapign-name',
                calendar: 'campaign-calendar',
                advertiser: 'campaign-advertiser',
                page: 'campaign-description-page',
            },
            goals: {
                goals: 'campaign-goals',
                noGoals: 'campaign-no-goals',
                page: 'campaign-goals-page',
            },
            plan: {
                goalButton: 'campaign-main-goal-button',
                goal: 'campaign-goal',
                conversions: 'campaign-conversions-count',
                conversionCost: 'campaign-conversion-price',
                shows: 'campaign-shows-count',
                clicks: 'campaign-clicks-count',
                ctr: 'campaign-ctr',
                cpm: 'campaign-cpm',
                cpc: 'campaign-cpc',
                page: 'campaign-plan-page',
            },
            placement: {
                create: 'campaign-new-placement',
                page: 'campaign-placement-page',
            },
            pixels: {
                page: 'campaign-pixels-page',
            },
        },
    },
};

const createClass = (id: string) => {
    return `__tst__${id}`;
};

const createClassSelector = (id: string) => {
    return `.__tst__${id}`;
};

const createIdSelector = (id: string) => {
    return `[data-test-id="${id}"]`;
};

const createXPathIdSelector = (id: string) => {
    return `@data-test-id="${id}"`;
};

const createId = (id: string) => {
    return {
        'data-test-id': id,
    } as { [key: string]: any };
};

export {
    helpSelectors,
    testIds,
    createIdSelector,
    createId,
    createClass,
    createClassSelector,
    createXPathIdSelector,
};
