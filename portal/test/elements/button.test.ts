import {assert} from 'chai'

import {ButtonElement} from '../../src';

import {SimpleButtonElement,ButtonElementWithImage,ButtonElementWithAllProperties} from '../mocks/index';

describe('Div button element test', () => {
    it('should create simple button', () => {
        let button: ButtonElement = new ButtonElement({
            action: {
                url: 'ya.ru',
                log_id: 'id'
            }
        });

        assert.deepEqual(button.div(), SimpleButtonElement);
    });

    it('should create button with image', () => {
        let button: ButtonElement = new ButtonElement({
            image: {
                image_url: 'ya.ru',
                ratio: 0.5
            },
            action: {
                url: 'ya.ru',
                log_id: 'id'
            }
        });

        assert.deepEqual(button.div(), ButtonElementWithImage);
    });

    it('should create button with all properties', () => {
        let button: ButtonElement = new ButtonElement({
            text:'Да',
            background_color: '#000',
            image: {
                image_url: 'ya.ru',
                ratio: 0.5
            },
            action: {
                url: 'ya.ru',
                log_id: 'id'
            }
        });

        assert.deepEqual(button.div(), ButtonElementWithAllProperties);
    });
});