import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { Home__getStaticUrlWww } from './home__get-static-url.view';

describe('common getStaticUrl', function() {
    beforeEach(function() {
        // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
        if (!home.env) {
            home.env = {
                devInstance: true,
                prodInstance: false,
                debug: true,
                inlineCss: false,
                useCache: false,
                externalStatic: false,
                inlineSuggest: false
            };
        }

        home.staticVersion = '1.2345';
    });

    home.GetStaticURL.addFreezedFiles('white', {
        'pages/comtr/_comtr.css': '//yastatic.net/s3/home-static/_/p/q/NV-RyolHyvzx5WR9e-22AEE14.css'
    });

    describe('dev', function() {
        it('default usage', function() {
            let req = mockReq({}, {
                devStaticHost: 'https://st-v1d1.wdevx.yandex.net'
            });
            let getStaticURL = execView(Home__getStaticUrlWww, req);

            expect(getStaticURL.getHost()).toEqual('//yastatic.net');

            expect(getStaticURL.getAbsolute('pages/comtr/_comtr.tr.js', 'white'))
                .toEqual('https://st-v1d1.wdevx.yandex.net/tmpl/white/pages/comtr/_comtr.tr.js');
            expect(getStaticURL.getAbsolute('pages/comtr/_comtr.css', 'white'))
                .toEqual('//yastatic.net/s3/home-static/_/p/q/NV-RyolHyvzx5WR9e-22AEE14.css');

            expect(getStaticURL.getHash('pages/comtr/_comtr.tr.js', 'white'))
                .toBeUndefined();
            expect(getStaticURL.getHash('pages/comtr/_comtr.css', 'white'))
                .toEqual('s3home-static_pqNV-RyolHyvzx5WR9e-22AEE14');
        });
    });

    describe('prod', function() {
        beforeEach(function() {
            home.env.externalStatic = true;
            home.env.devInstance = false;
        });

        it('default usage', function() {
            let req = mockReq();
            let getStaticURL = execView(Home__getStaticUrlWww, req);

            expect(getStaticURL.getHost()).toEqual('//yastatic.net');

            expect(getStaticURL.getAbsolute('pages/comtr/_comtr.tr.js', 'white'))
                .toEqual('//yastatic.net/s3/home-static/1.2345/white/pages/comtr/_comtr.tr.js');
            expect(getStaticURL.getAbsolute('pages/comtr/_comtr.css', 'white'))
                .toEqual('//yastatic.net/s3/home-static/_/p/q/NV-RyolHyvzx5WR9e-22AEE14.css');

            expect(getStaticURL.getHash('pages/comtr/_comtr.tr.js', 'white'))
                .toBeUndefined();
            expect(getStaticURL.getHash('pages/comtr/_comtr.css', 'white'))
                .toEqual('s3home-static_pqNV-RyolHyvzx5WR9e-22AEE14');
        });

        it('ua static', function() {
            let req = mockReq({}, {
                uafr_static_yandex_sx: 1
            });
            let getStaticURL = execView(Home__getStaticUrlWww, req);

            expect(getStaticURL.getHost()).toEqual('//static.yandex.sx');

            expect(getStaticURL.getAbsolute('pages/comtr/_comtr.tr.js', 'white'))
                .toEqual('//static.yandex.sx/s3/home-static/1.2345/white/pages/comtr/_comtr.tr.js');
            expect(getStaticURL.getAbsolute('pages/comtr/_comtr.css', 'white'))
                .toEqual('//static.yandex.sx/s3/home-static/_/p/q/NV-RyolHyvzx5WR9e-22AEE14.css');
        });

        it('custom root', function() {
            let req = mockReq({}, {
                options: {
                    s3root: 's3/custom'
                }
            });
            let getStaticURL = execView(Home__getStaticUrlWww, req);

            expect(getStaticURL.getHost()).toEqual('//yastatic.net');

            expect(getStaticURL.getAbsolute('pages/comtr/_comtr.tr.js', 'white'))
                .toEqual('//yastatic.net/s3/custom/1.2345/white/pages/comtr/_comtr.tr.js');

            // s3/custom не перезаписывается в рантайме для фриза
            expect(getStaticURL.getAbsolute('pages/comtr/_comtr.css', 'white'))
                .toEqual('//yastatic.net/s3/home-static/_/p/q/NV-RyolHyvzx5WR9e-22AEE14.css');
        });

        it('custom root + ua', function() {
            let req = mockReq({}, {
                options: {
                    s3root: 's3/custom'
                },
                uafr_static_yandex_sx: 1
            });
            let getStaticURL = execView(Home__getStaticUrlWww, req);

            expect(getStaticURL.getHost()).toEqual('//static.yandex.sx');

            expect(getStaticURL.getAbsolute('pages/comtr/_comtr.tr.js', 'white'))
                .toEqual('//static.yandex.sx/s3/custom/1.2345/white/pages/comtr/_comtr.tr.js');

            // s3/custom не перезаписывается в рантайме для фриза
            expect(getStaticURL.getAbsolute('pages/comtr/_comtr.css', 'white'))
                .toEqual('//static.yandex.sx/s3/home-static/_/p/q/NV-RyolHyvzx5WR9e-22AEE14.css');
        });

        it('custom host + ua', function() {
            let req = mockReq({}, {
                exp: {
                    msk_cdn_static: {
                        on: 1
                    }
                },
                uafr_static_yandex_sx: 1
            });
            let getStaticURL = execView(Home__getStaticUrlWww, req);
            expect(getStaticURL.getHost()).toEqual('//static.yandex.sx');

            expect(getStaticURL.getAbsolute('pages/comtr/_comtr.tr.js', 'white'))
                .toEqual('//static.yandex.sx/s3/home-static/1.2345/white/pages/comtr/_comtr.tr.js');
            expect(getStaticURL.getAbsolute('pages/comtr/_comtr.css', 'white'))
                .toEqual('//static.yandex.sx/s3/home-static/_/p/q/NV-RyolHyvzx5WR9e-22AEE14.css');
        });

        it('ua', function() {
            let req = mockReq({}, {
                uafr_static_yandex_sx: 1
            });
            let getStaticURL = execView(Home__getStaticUrlWww, req);

            expect(getStaticURL.getHost()).toEqual('//static.yandex.sx');

            expect(getStaticURL.getAbsolute('pages/comtr/_comtr.tr.js', 'white'))
                .toEqual('//static.yandex.sx/s3/home-static/1.2345/white/pages/comtr/_comtr.tr.js');
            expect(getStaticURL.getAbsolute('pages/comtr/_comtr.css', 'white'))
                .toEqual('//static.yandex.sx/s3/home-static/_/p/q/NV-RyolHyvzx5WR9e-22AEE14.css');
            expect(getStaticURL.getAbsolute('https://yastatic.net/jquery/2.1.4/jquery.min.js'))
                .toEqual('https://yastatic.net/jquery/2.1.4/jquery.min.js');
        });
    });
});
