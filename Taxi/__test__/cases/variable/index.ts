import {extendNavigation} from '../../extendNavigation';

const ROUTE = '/test-url';

extendNavigation('group', {
    url: ROUTE,
    title: 'title'
});
