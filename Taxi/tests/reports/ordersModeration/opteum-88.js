const {driverSearchChecks} = require('../../../shared/reportsOrdersModeration');

describe(
    'Фильтрация: по водителю: ФИО',

    () => driverSearchChecks({
        query: 'Васильченко Никита Андреевич',

        nameAtSuggest: 'Васильченко :: Никита Андреевич',
        nameAtTable: 'Васильченко Никита Андреевич',
    }),
);
