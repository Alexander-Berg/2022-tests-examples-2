import React from 'react';
import {mount} from 'enzyme';
import configureMockStore from 'redux-mock-store';
import {Provider} from 'react-redux';

import createActions from '_common/static/services/help/actions';
import Core from '_common/static/services/help/blocks/core/Core';

import ChatContent from '../ChatContent';
import Form from '../Form';
import CSAT from '../CSAT';

const createStore = configureMockStore();

const THEME = 'yandex';
const ACTIONS = createActions({protocol: {}, internal: {}}, {getAuthFromState: () => ({}), authToOptions: () => ({})});
const I18N = {
    print: () => null
};

describe('common/static/services/help/components/chat/ChatContent', () => {
    it('показывает пустую страницу пока возвращаемся в меню когда пользователь проставил ксат чтоб не успел еще чего тыкнуть', () => {
        const store = createStore({
            chat: {
                csatFinished: true,
                view: {
                    show_message_input: true
                },
                ask_csat: false,
                chat_open: false,
                attachments: []
            },
            config: {}
        });

        const wrapper = mount(
            <Provider store={store}>
                <Core actions={ACTIONS} theme={THEME} i18n={I18N}>
                    <ChatContent/>
                </Core>
            </Provider>
        );

        expect(wrapper.find(ChatContent).text()).toBe('');

        wrapper.unmount();
    });

    it.each`
        chat_open | show_message_input | ask_csat | showForm
        ${true}   | ${true}            | ${true}  | ${false}
        ${true}   | ${true}            | ${false} | ${true}
        ${true}   | ${false}           | ${true}  | ${false}
        ${true}   | ${false}           | ${false} | ${false}
        ${false}  | ${true}            | ${true}  | ${false}
        ${false}  | ${true}            | ${false} | ${false}
        ${false}  | ${false}           | ${true}  | ${false}
        ${false}  | ${false}           | ${false} | ${false}
    `(
    'Форма ввода сообщения должна отображаться: $showForm, если чат открыт - $chat_open, view говорит что надо показать - $show_message_input, запрошен CSAT - $ask_csat',
    ({chat_open, show_message_input, ask_csat, showForm}) => {
        const store = createStore({
            chat: {
                csatFinished: false,
                view: {
                    show_message_input
                },
                ask_csat,
                chat_open,
                attachments: []
            },
            config: {}
        });

        const wrapper = mount(
            <Provider store={store}>
                <Core actions={ACTIONS} theme={THEME} i18n={I18N}>
                    <ChatContent/>
                </Core>
            </Provider>
        );

        expect(wrapper.find(Form).exists()).toBe(showForm);

        wrapper.unmount();
    }
);

    it.each`
        chat_open | ask_csat | showCSAT
        ${true}   | ${true}  | ${true}
        ${true}   | ${false} | ${false}
        ${false}  | ${true}  | ${false}
        ${false}  | ${false} | ${false}
    `(
    'CSAT должен отображаться: $showCSAT, если чат открыт - $chat_open, запрошен CSAT - $ask_csat',
    ({chat_open, ask_csat, showCSAT}) => {
        const store = createStore({
            chat: {
                csatFinished: false,
                view: {
                    show_message_input: false
                },
                ask_csat,
                chat_open,
                attachments: []
            },
            config: {}
        });

        const wrapper = mount(
            <Provider store={store}>
                <Core actions={ACTIONS} theme={THEME} i18n={I18N}>
                    <ChatContent/>
                </Core>
            </Provider>
        );

        expect(wrapper.find(CSAT).exists()).toBe(showCSAT);

        wrapper.unmount();
    }
);
});
