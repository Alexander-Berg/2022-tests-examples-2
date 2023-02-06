import React from 'react';
import {mount, shallow} from 'enzyme';

import Button from '../../button/Button';
import File from '../File';

describe('Components/file', () => {
    it('рендерит стандартный button', () => {
        const file = shallow(<File controlComponent={<Button>Кнопка</Button>} />);
        expect(file.find(Button).exists()).toBeTruthy();
        expect(file.find('input').exists()).toBeTruthy();
    });

    it('onChange возвращает event', () => {
        const spy = jest.fn();
        const file = shallow(<File controlComponent={<Button>Кнопка</Button>} onChange={spy} />);
        const path = '/fake/file.txt';
        file.find('input').simulate('change', {
            target: {
                value: path
            }
        });

        expect(spy).toHaveBeenCalled();
        expect(spy.mock.calls[0][0].target.value).toEqual(path);
    });

    it('onFilesChange возвращает FileList', () => {
        const spy = jest.fn();
        const file = mount(<File controlComponent={<Button>Кнопка</Button>} onFilesChange={spy} />);
        file.find('input').simulate('change');

        expect(spy).toHaveBeenCalled();
        expect(spy.mock.calls[0][0]).toBeInstanceOf(FileList);
    });
});
