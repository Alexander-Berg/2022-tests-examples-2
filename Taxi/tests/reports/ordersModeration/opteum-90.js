const {driverSearchChecks} = require('../../../shared/reportsOrdersModeration');

describe(
    'Фильтрация: по водителю: номер телефона',

    () => driverSearchChecks({
        query: '70005181486',

        nameAtSuggest: 'Васильченко :: Никита Андреевич',
        nameAtTable: 'Васильченко Никита Андреевич',
    }),
);
