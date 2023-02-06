import React from 'react';
import {shallow} from 'enzyme';
import {ORDER_STATUS} from '_common/isomorphic/order/consts';
import {useComponents} from '_common/static/utils/components-provider';
import {AppDumb} from './App';

jest.mock('_common/static/utils/components-provider');

const components = {
    Logo: () => null
};

describe('App', () => {
    useComponents.mockImplementation(() => components);
    const allStatuses = Object.values(ORDER_STATUS);

    it('Должна показываться карта, если поездка найдена', () => {
        for (let status of allStatuses) {
            const props = {
                status,
                isNotFound: false
            };

            const wrapper = shallow(<AppDumb {...props}/>);
            expect(wrapper.find('Connect(RouteInfo)')).toHaveLength(1);
            expect(wrapper.find('NotFound')).toHaveLength(0);
        }
    });

    it('Должна показываться 404 страница, если пришел isNotFound', () => {
        for (let status of Object.values(ORDER_STATUS)) {
            const props = {
                status,
                isNotFound: true
            };

            const wrapper = shallow(<AppDumb {...props}/>);
            expect(wrapper.find('NotFound')).toHaveLength(1);
            expect(wrapper.find('Connect(RouteInfo)')).toHaveLength(0);
        }
    });
});
