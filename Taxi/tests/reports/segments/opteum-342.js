const DriverCard = require('../../../page/driverCard/DriverCard');
const ReportsSegments = require('../../../page/ReportsSegments');

describe('Открытие карточки водителя из сегментов водителей', () => {

    const removeFloatRe = /(,00|0)$|\s+/g;

    let data;

    it('Открыть страницу сегментов водителей', () => {
        ReportsSegments.goTo();
    });

    it('Сохранить данные первого водителя из списка', () => {
        const [lastName, firstName, middleName] = ReportsSegments
            .getCells({tr: 1, td: 3})
            .getText()
            .split(' ');

        data = {
            firstName,
            lastName,
            middleName,
            sign: ReportsSegments.getCells({tr: 1, td: 2}).getText(),
            phone: ReportsSegments.getCells({tr: 1, td: 7}).getText(),
            balance: ReportsSegments.getCells({tr: 1, td: 9}).getText(),
            limit: ReportsSegments.getCells({tr: 1, td: 10}).getText(),
        };
    });

    it('Открыть первого водителя из списка', () => {
        ReportsSegments.getCells({tr: 1, td: 1}).click();
    });

    it('Переключиться на открывшийся таб водителя', () => {
        ReportsSegments.switchTab();
    });

    it('В карточке водителя отображается корректное фио', () => {
        expect(DriverCard.lastName).toHaveAttributeEqual('value', data.lastName);
        expect(DriverCard.firstName).toHaveAttributeEqual('value', data.firstName);

        // отчества может не быть
        if (data.middleName) {
            expect(DriverCard.middleName).toHaveAttributeIncludes('value', data.middleName);
        }
    });

    it('В карточке водителя отображается корректный позывной', () => {
        expect(DriverCard.vehicleLink).toHaveTextIncludes(data.sign);
    });

    it('В карточке водителя отображается корректный телефон', () => {
        expect(DriverCard.phoneNumber).toHaveAttributeEqual('value', data.phone);
    });

    it('В карточке водителя отображается корректный баланс', () => {
        const balanceRub = `${data.balance.replace(removeFloatRe, '')} ₽`;
        expect(DriverCard.currentBalance).toHaveTextEqual(balanceRub);
    });

    it('В карточке водителя отображается корректный лимит', () => {
        const limitRub = data.limit.replace(removeFloatRe, '');
        expect(DriverCard.balanceLimit).toHaveAttributeEqual('value', limitRub);
    });

});
