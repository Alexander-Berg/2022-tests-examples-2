const {driverSearchChecks} = require('../../../shared/reportsOrdersModeration');

describe(
    'Фильтрация: по водителю: позывной',

    () => driverSearchChecks({
        query: 'nvxden',

        nameAtSuggest: 'Новиков :: Денис Игоревич',
        nameAtTable: 'Новиков Денис Игоревич',
    }),
);
