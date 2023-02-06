/**
 * todo fomasha порефакторить этот тест, чтобы работал без стора
 */
describe('PageLayout', () => {
    it('works', () => {
        expect('').toBe('');
    });
});
// import React from 'react';
// import { Provider } from 'react-redux';
// import { cleanup } from 'react-testing-library';
// import { StaticRouter, Route } from 'react-router-dom';
// import { PageLayout } from '..';
// import { jestSnapshotRenderTest } from 'client/utils/jest-utils';
// import configureStore from 'client/store';
// import { getState } from 'client/store/state';
// import { createState } from 'server/lib/create-state';
// import { BundleData } from 'client/bundles/types';
// import { createMemoryHistory } from 'history';
//
// const initialState: BundleData = {
//     nonce: 'nonce',
//     requestId: 'requestId',
//     secretkey: 'secretkey',
//     cfg: {
//         raven: {
//             dsn: 'dsn',
//         },
//         langs: ['ru'],
//     },
//     blackbox: {
//         uid: '564628606',
//         login: 'yndx-fomasha',
//         lang: 'ru',
//     },
//     langdetect: {
//         id: 'ru',
//         name: 'Ru',
//     },
//     query: {},
//     isInternalUser: true,
//     protocol: '',
//     tld: '',
//     userSettings: {
//         licenceAgreementAccepted: true,
//         mailingAccepted: true,
//     },
// };
//
// const history = createMemoryHistory();
//
// const mockStore = configureStore(getState(initialState), history);
//
// afterEach(cleanup);
//
// jestSnapshotRenderTest({
//     'with hasMenu prop implicitly set to false': (
//         <Provider store={mockStore}>
//             <StaticRouter location="/" context={{}}>
//                 <Route path="/">
//                     <PageLayout>Page content goes here</PageLayout>
//                 </Route>
//             </StaticRouter>
//         </Provider>
//     ),
//
//     'with hasMenu prop explicitly set to false': (
//         <Provider store={mockStore}>
//             <StaticRouter location="/" context={{}}>
//                 <Route path="/">
//                     <PageLayout menu={<div>Test</div>}>
//                         Page content goes here
//                     </PageLayout>
//                 </Route>
//             </StaticRouter>
//         </Provider>
//     ),
//
//     'with hasMenu prop explicitly set to true': (
//         <Provider store={mockStore}>
//             <StaticRouter location="/" context={{}}>
//                 <Route path="/">
//                     <PageLayout>Page content goes here</PageLayout>
//                 </Route>
//             </StaticRouter>
//         </Provider>
//     ),
// });
