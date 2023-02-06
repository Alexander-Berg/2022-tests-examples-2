const DetailsTab = require('../../../page/driverCard/DetailsTab');
const DriverCard = require('../../../page/driverCard/DriverCard');
const ReportsQuality = require('../../../page/ReportsQuality');

describe('Переход в карточку водителя', () => {

    let firstDriverLicense,
        firstDriverName,
        firstDriverNickName,
        firstName,
        firstPhoneNumber,
        firstWorkRule,
        lastName,
        nickName,
        nickNameAndAutoAndStatus;

    it('Открыть страницу Качество', () => {
        ReportsQuality.goTo();
    });

    it('Сохранить данные о водителе', () => {
        firstDriverName = ReportsQuality.resultTable.firstDriver.getText();
        firstDriverNickName = ReportsQuality.resultTable.firstNickName.getText();
        firstPhoneNumber = ReportsQuality.resultTable.firstPhoneNumber.getText();
        firstWorkRule = ReportsQuality.resultTable.firstWorkRule.getText();
        firstDriverLicense = ReportsQuality.resultTable.firstDriverLicense.getText();
    });

    it('Открыть страницу первого водителя', () => {
        ReportsQuality.openFirstDriver();
    });

    it('Информация совпадает с данными из таблицы', () => {
        firstName = DetailsTab.detailsBlock.firstName.getValue();
        lastName = DetailsTab.detailsBlock.lastName.getValue();
        nickNameAndAutoAndStatus = DriverCard.nickNameAndAutoAndStatus.getText();
        [nickName] = nickNameAndAutoAndStatus.split(' :: ');

        expect(`${lastName} ${firstName}`).toEqual(firstDriverName);
        expect(nickName).toEqual(firstDriverNickName);
        expect(DriverCard.phoneNumber).toHaveAttributeEqual('value', firstPhoneNumber);
        expect(DetailsTab.workRulesBlock.workRules).toHaveTextEqual(firstWorkRule);
        expect(DetailsTab.detailsBlock.driverLicense).toHaveAttributeEqual('value', firstDriverLicense);
    });

});
