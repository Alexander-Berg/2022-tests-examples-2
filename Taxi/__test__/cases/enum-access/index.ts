import {extendNavigation} from '../../extendNavigation';

const enum Urls {
    Test = '/test-url'
}

extendNavigation('group', {
    url: Urls.Test,
    title: 'title'
});
