import getRoutes from '../routes';

jest.mock('../pages/ListPage/ListPage.jsx');
jest.mock('../pages/AddAccountPage/AddAccountPage.jsx');
jest.mock('../pages/WelcomePage/WelcomePage.jsx');
jest.mock('../pages/AuthWithLetterPage/AuthWithLetterPage.jsx');

import MagicPromoPage from '../pages/MagicPromoPage/MagicPromoPage.jsx';

describe('Auth routes', () => {
    it('should return routes array', () => {
        const resultRoutes = getRoutes({});

        expect(Array.isArray(resultRoutes)).toBe(true);

        resultRoutes.forEach((route) => {
            expect(typeof route).toBe('object');
            expect(Object.hasOwnProperty.call(route, 'path')).toBe(true);
            expect(Object.hasOwnProperty.call(route, 'component')).toBe(true);
        });
    });

    it('should return condition routes', () => {
        const routeConditions = {isQRPromoEnabled: true};

        let resultRoutes = getRoutes(routeConditions);

        let authPhoneRoute = resultRoutes.find((route) => route.path === '/auth/phone');

        expect(authPhoneRoute).toMatchObject({
            path: '/auth/phone',
            exact: true,
            component: {}
        });

        let authEmailRoute = resultRoutes.find((route) => route.path === '/auth/email');

        expect(authEmailRoute).toMatchObject({
            path: '/auth/email',
            exact: true,
            component: {}
        });

        let authMagicRoute = resultRoutes.find((route) => route.path === '/auth/magic');

        expect(authMagicRoute).toEqual({
            path: '/auth/magic',
            exact: true,
            component: MagicPromoPage
        });

        resultRoutes = getRoutes(routeConditions);

        authPhoneRoute = resultRoutes.find((route) => route.path === '/auth/phone');
        expect(authPhoneRoute).toMatchObject({
            path: '/auth/phone',
            exact: true,
            component: {}
        });

        authEmailRoute = resultRoutes.find((route) => route.path === '/auth/email');
        expect(authEmailRoute).toMatchObject({
            path: '/auth/email',
            exact: true,
            component: {}
        });

        authMagicRoute = resultRoutes.find((route) => route.path === '/auth/magic');
        expect(authMagicRoute).toEqual({
            path: '/auth/magic',
            exact: true,
            component: MagicPromoPage
        });
    });
});
