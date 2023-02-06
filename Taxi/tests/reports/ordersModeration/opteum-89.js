const {driverSearchChecks} = require('../../../shared/reportsOrdersModeration');

describe(
    'Фильтрация: по водителю: ВУ',

    () => driverSearchChecks({
        query: '88YE222456',

        nameAtSuggest: 'Васильченко :: Никита Андреевич',
        nameAtTable: 'Васильченко Никита Андреевич',
    }),
);
