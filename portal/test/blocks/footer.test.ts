import {assert} from 'chai'

import {FooterBlock,ImageElement} from '../../src/index';

import {SimpleFooter, FooterWithImage, FooterWithAction, FooterWithPadding} from '../mocks/index';

describe('Div footer test', () => {
    it('should create simple footer', () => {
        let footer: FooterBlock = new FooterBlock({
            text: "<font color=\"#000000\">Новости</font>",
            text_style: 'text_m'
        });

        assert.deepEqual(footer.div(), SimpleFooter);
    });

     it('should create footer with padding modifier', () => {
         let footer:FooterBlock = new FooterBlock({
             text: '<font color="#000000">Новости</font>',
             text_style: 'text_m',
             padding_modifier: {
                 size: 'xs',
                 position: 'left'
             }
         });

         assert.deepEqual(footer.div(), FooterWithPadding);
     });

     it('should create footer with image', () => {
         let image: ImageElement= new ImageElement({
             image_url:'ya.ru',
             ratio:0.67
         });

         let footer: FooterBlock = new FooterBlock({
             text: '<font color="#000000">Новости</font>',
             text_style: 'text_m',
             image: image
         });

         assert.deepEqual(footer.div(), FooterWithImage);
     });

     it('should create footer with action', () => {
         let footer: FooterBlock = new FooterBlock({
             text: '<font color="#000000">Новости</font>',
             text_style: 'text_m',
             action: {
                 url: 'url',
                 log_id: 'footer'
             }
         });

         assert.deepEqual(footer.div(), FooterWithAction);
     });

});