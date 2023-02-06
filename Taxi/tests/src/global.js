import React from 'react';
import Enzyme from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

Enzyme.configure({adapter: new Adapter()});

global.window.config = Object.freeze({
    env: 'unstable',
    userInfo: {
        filters: {
            '/payments/order_info': {
                last_orders: 25
            },
            '/orders/': {
                last_orders: 15
            }
        }
    }
});

global.window.__adminConfig = Object.freeze({
    getCurrentApi: () => 'api-u'
});

global.React = React;
