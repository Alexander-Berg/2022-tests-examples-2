import {extendNavigation} from '../../extendNavigation';
import {ORDERS_URL, ROUTE, URLS} from './consts';
import {Tabs} from './types';

const URL = `/test-url/${Tabs.Users}`;

const PROMOCODES_URL = URLS.TABS.PROMOCODES;

extendNavigation('group', [{
    url: ROUTE,
    title: 'title'
}, {
    url: '/test-url/2',
    title: 'title2'
}, {
    url: `${URL}/3`,
    title: 'title3'
}, {
    url: `${ORDERS_URL}/4`,
    title: 'title4'
}, {
    url: `${URLS.TABS.PROMOCODES}/5`,
    title: 'title5'
}, {
    url: `${PROMOCODES_URL}/6`,
    title: 'title6'
}]);
