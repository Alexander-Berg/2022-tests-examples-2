import {assert} from 'chai'

import {NumericSize, TabsBlock, TabsBlockTouch, TitleBlock, ContainerBlock} from '../../src';

import {SimpleTabs, SimpleTouchTabs} from '../mocks/index';

describe('Div tabs test', () => {
    it('should create simple tabs', () => {
        let title: TitleBlock = new TitleBlock({
            text: "<font color=\"#000000\">Фильмы</font>",
            text_style: 'title_m'
        });
        let tabs: TabsBlock = new TabsBlock({
            items: [{
                title: {text: 'text', action: {log_id: 'id', url: 'ua.ru'}},
                content: new ContainerBlock({
                    width: new NumericSize({value: 1}),
                    height: new NumericSize({value: 1}),
                    children: [title]
                })
            }]
        });

        assert.deepEqual(tabs.div(), SimpleTabs);
    });

    it('should create simple tabs for touch', () => {
        let title: TitleBlock = new TitleBlock({
            text: "<font color=\"#000000\">Фильмы</font>",
            text_style: 'title_m'
        });
        let tabs: TabsBlock = new TabsBlockTouch({
            tabs_position: 'bottom',
            inactive_tab_bg_color: 'red',
            items: [{
                title: {text: 'text', action: {log_id: 'id', url: 'ua.ru'}},
                content: new ContainerBlock({
                    width: new NumericSize({value: 1}),
                    height: new NumericSize({value: 1}),
                    children: [title]
                })
            }]

        });

        assert.deepEqual(tabs.div(), SimpleTouchTabs);
    });
});