import {renderClient} from '@components/Layout/client';
import configureStore from './configureStore';
import {ResizeTestPush} from '@blocks/pushes/ResizeTestPush';

document.addEventListener('DOMContentLoaded', () => {
    renderClient({
        App: ResizeTestPush,
        configureStore
    });
});
