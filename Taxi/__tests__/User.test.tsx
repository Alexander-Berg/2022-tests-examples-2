import React from 'react';
import {render} from 'enzyme';
import User from '../User';

const login = 'test-user';
const avatarId = '0/0-0';
const avatarHost = 'https://test-avatar.yandex.ru';

describe('Components/user', () => {
    it('Передача логина пользователя', () => {
        const wrapper = render(<User avatarId={avatarId} login={login}/>);
        expect(wrapper.find('.amber-user-name__login').text()).toEqual(login);
    });

    it('Передача id аватара', () => {
        const wrapper = render(<User avatarId={avatarId} login={login}/>);
        expect(wrapper.find('.amber-user-avatar__img').prop('src')).toContain(avatarId);
    });

    it('Передача avatarHost', () => {
        const wrapper = render(<User avatarHost={avatarHost} avatarId={avatarId} login={login}/>);
        expect(wrapper.find('.amber-user-avatar__img').prop('src')).toContain(avatarHost);
    });
});
