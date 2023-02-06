import {extendNavigation} from '../../extendNavigation';

const CONSTANTS = {
    TABS: ['A', 'B'],
    URLS: {
        TEST: '/test-url'
    }
};

extendNavigation('group', {
    url: CONSTANTS.URLS.TEST,
    title: 'title'
});
