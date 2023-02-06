import {renderServer} from '@components/Layout/server';
import {ResizeTestPush} from '@blocks/pushes/ResizeTestPush';
import configureStore from './configureStore';

export const renderPage = (res) => {
    renderServer(res, {
        title: i18n('Frontend.id.title'),
        App: ResizeTestPush,
        configureStore
    });
};
