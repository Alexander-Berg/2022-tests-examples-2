import { mount, shallow } from 'enzyme';

import App from '~p/index';
import { Hero } from '~c/Hero/Hero';
import { MobileAppScreen } from '~c/MobileAppScreen/MobileAppScreen';
import { Profit } from '~c/Profit/Profit';
import { WhatCanOffer } from '~c/WhatCanOffer/WhatCanOffer';
import { Conditions } from '~c/Conditions/Conditions';
import { Faq, faqList } from '~c/Faq/Faq';

describe('Базовые тесты', () => {
  const app = shallow(<App />);

  describe('Компонент Hero', () => {
    describe('Имеет один заголовок', () => {
      const hero = app.find(Hero);
      const heroTitle = hero.dive().find('Title');
      const titlesH1 = heroTitle.filterWhere((wrap) => {
        return wrap.prop('level') === 'h1';
      });

      it('На странице есть только один h1', () => {
        expect(titlesH1.length).toEqual(1);
      });

      it('Содержит правильный текст', () => {
        expect(titlesH1.dive().find('h1').text()).toEqual('Получайте новые заказы с сервисом Яндекс.Еда');
      });
    });
  });

  describe('Компонент Profit', () => {
    const profit = mount(<Profit />);
    const title = profit.find('Title');

    describe('Заголовок', () => {
      it('Только один в компоненте', () => {
        expect(title.length).toEqual(1);
      });

      it('Содержит правильный текст', () => {
        expect(title.text()).toEqual('Что вы получаете');
      });
    });
  });

  describe('Компонент MobileAppScreen', () => {
    const mobileAppScreen = mount(<MobileAppScreen />);
    const title = mobileAppScreen.find('Title');

    describe('Заголовок', () => {
      it('Только один в компоненте', () => {
        expect(title.length).toEqual(1);
      });

      it('Содержит правильный текст', () => {
        expect(title.text()).toEqual('Управляйте рестораном через приложение');
      });
    });
  });

  describe('Компонент Conditions', () => {
    const component = mount(<Conditions />);
    const title = component.find('Title');

    describe('Заголовок', () => {
      it('Только один в компоненте', () => {
        expect(title.length).toEqual(1);
      });

      it('Содержит правильный текст', () => {
        expect(title.text()).toEqual('Условия сотрудничества');
      });
    });
  });

  describe('Компонент WhatCanOffer', () => {
    const component = mount(<WhatCanOffer />);
    const title = component.find('Title');

    describe('Заголовок', () => {
      it('Только один в компоненте', () => {
        expect(title.length).toEqual(1);
      });

      it('Содержит правильный текст', () => {
        expect(title.text()).toEqual('Что еще можем предложить');
      });
    });
  });

  describe('Компонент FAQ', () => {
    const faq = mount(<Faq />);
    const faqTitle = faq.find('Title');

    describe('Заголовок', () => {
      it('Только один в компоненте', () => {
        expect(faqTitle.length).toEqual(1);
      });

      it('Содержит правильный текст', () => {
        expect(faqTitle.text()).toEqual('Частые вопросы (FAQ)');
      });
    });

    describe('Список', () => {
      it('Содержит правильное количество пар вопрос-ответ', () => {
        expect(faq.find('FaqItem').length).toEqual(faqList.length);
      });
    });

    // FIXME
    //  Не работает симуляция клика с изменением стейта
    // describe('Элемент списка', () => {
    //   const faqFirstItem = faq.find('FaqItem').first();
    //   const firstItemTrigger = faqFirstItem.find('button');
    //   const setState = jest.fn();
    //   const useStateSpy = jest.spyOn(React, 'useState');
    //   // @ts-ignore
    //   useStateSpy.mockImplementation((init) => [init, setState]);
    //
    //   it('При нажатии на вопрос раскрывает ответ', () => {
    //     firstItemTrigger.simulate('click', { currentTarget: firstItemTrigger.getDOMNode() });
    //     expect(setState).toHaveBeenCalledTimes(1);
    //   });
    //
    //   it('При повторном нажатии на вопрос скрывает ответ', () => {});
    // });
  });
});
