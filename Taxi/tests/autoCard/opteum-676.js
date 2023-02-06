const AutoCard = require('../../page/AutoCard');
const VehiclesPage = require('../../page/VehiclesPage');
const {assert} = require('chai');

const DATA = [
    {
        id: 'длина',
        min: 170,
        max: 601,
        errorHint: 'Допустимое значение длины от 170 до 601 см',
    },
    {
        id: 'ширина',
        min: 96,
        errorHint: 'Допустимое значение ширины от 96 до 250 см',
        max: 250,
    },
    {
        id: 'высота',
        min: 90,
        max: 250,
        errorHint: 'Допустимое значение высоты от 90 до 250 см',
    },
    {
        id: 'грузоподъемность',
        min: 300,
        max: 6000,
        errorHint: 'Допустимое значение грузоподъемности от 300 до 6000 кг',
    },
];

let cargoParamsSection, hint, input;

describe('Грузовой автомобиль: валидация размеров', () => {
    it('Открыть карточку создания автомобиля', () => {
        VehiclesPage.goTo();
        VehiclesPage.addButton.click();
    });

    it('выбрать тариф грузовой', () => {
        AutoCard.categoriesBlock.dropdown.scrollIntoView();
        AutoCard.categoriesBlock.dropdown.waitForClickable();
        AutoCard.categoriesBlock.dropdown.click();
        AutoCard.categoriesBlock.dropdownItems.cargo.click();
        AutoCard.categoriesBlock.dropdown.click();
    });

    for (let i = 0; i < 4; i++) {
        it(`Отображается ошибка при параметрах ${DATA[i].id} превышающие максимальные`, () => {
            // блок с параметрами грузового отсека стоит на 4 месте
            cargoParamsSection = $$('form >div >div')[3].$$('[class*=Row_center]')[i];
            input = cargoParamsSection.$('input');
            hint = cargoParamsSection.$('.Textinput-Hint');
            AutoCard.type(input, DATA[i].max + 1);
            $('main').click();
            assert.equal(hint.getText(), DATA[i].errorHint);

        });

        it('отображаются ошибки об обязательности при очистке поля', () => {
            AutoCard.clearWithBackspace(input);
            assert.equal(hint.getText(), 'Это поле необходимо заполнить');
        });

        it(`Отображается ошибка при вводе параметров ${DATA[i].id} меньше минимальных`, () => {
            AutoCard.type(input, DATA[i].min - 1);
            $('main').click();
            assert.equal(hint.getText(), DATA[i].errorHint);
        });
    }

});
