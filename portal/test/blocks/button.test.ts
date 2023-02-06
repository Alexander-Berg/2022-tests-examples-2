import {assert} from 'chai'

import {ButtonElement, ContainerBlock, MenuItem, NumericSize} from '../../src';

import {SimpleButtonElement, ButtonElementWithImage, ButtonElementWithAllProperties} from '../mocks';

describe('Div button test', () => {
    it('should create simple button', () => {
        let button: ButtonElement = new ButtonElement({
            action: {
                url: "ya.ru",
                log_id: 'id'
            }
        });

        assert.deepEqual(button.div(), SimpleButtonElement);
    });
});