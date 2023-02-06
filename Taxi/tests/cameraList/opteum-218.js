const CameraList = require('../../page/signalq/CameraList');
const {assert} = require('chai');

describe('Смоук: добавление/удаление камеры', () => {
    it('открыт раздел "Все камеры"', () => {
        CameraList.goTo();
    });

    it('удалить все активные камеры', () => {
        CameraList.statusCell
            .filter(el => el.getText().includes('Не работает'))
            .map(el => el.index)
            .forEach(el => {
                CameraList.statusCell[el].click();
                CameraList.deleteCamera();
            });
    });

    it('добавить камеру', () => {
        CameraList.addCamera();
        browser.pause(1000);
    });

    it('камера добавлена', () => {
        assert.isTrue(CameraList.statusCell[0].getText().includes('Не работает'));
    });
});
