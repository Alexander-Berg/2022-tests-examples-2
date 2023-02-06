import React from 'react';
import {shallow} from 'enzyme';
import Logo from '../Logo';

const urlYandex = 'http://ya.ru';
const serviceUrl = 'http://taxi.yandex.ru';
const BLOCK_NAME = 'amber-logo';
const serviceName = 'Такси';
const service = 'go-taxi';

describe('Components/logo', () => {
    it('Использование параметра lang', () => {
        const lang = 'ru';
        const wrapper = shallow(<Logo lang={lang}/>);
        expect(wrapper.find(`.${BLOCK_NAME}__yandex`).prop('className')).toContain(lang);
    });

    it('Ссылка на Яндекс', () => {
        const wrapper = shallow(<Logo url={urlYandex}/>);
        expect(wrapper.find(`.${BLOCK_NAME}__yandex`).prop('href')).toEqual(urlYandex);
    });

    it('Ссылка на сервис', () => {
        const wrapper = shallow(<Logo url={urlYandex} serviceUrl={serviceUrl}/>);
        expect(wrapper.find(`.${BLOCK_NAME}__service-name`).prop('href')).toEqual(serviceUrl);
    });

    it('Название сервиса', () => {
        const wrapper = shallow(<Logo url={urlYandex} serviceName={serviceName}/>);
        expect(wrapper.find(`.${BLOCK_NAME}__service-name`).prop('title')).toEqual(serviceName);
    });

    it('Сервис в className', () => {
        const wrapper = shallow(<Logo url={urlYandex} service={service}/>);
        expect(wrapper.find(`.${BLOCK_NAME}__service-name`).prop('className')).toContain(service);
    });
});
