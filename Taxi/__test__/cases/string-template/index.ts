import {extendNavigation} from '../../extendNavigation';
import {TAB_ROUTE, Tabs} from './consts';

const ROUTE = '/test-url';

extendNavigation('group', {
    url: `${ROUTE}${TAB_ROUTE}/${Tabs.Users}/2`,
    title: 'title'
});
