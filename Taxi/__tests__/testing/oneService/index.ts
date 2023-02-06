import {config} from 'dotenv';

(function () {
    config({path: 'tools/arcadia/__tests__/testing/oneService/.env.arcadia.test'});

    console.info('build_base start');
    console.time('build_base');
    require('../../../ci/build_base');
    console.timeEnd('build_base');

    console.info('build_stage start');
    console.time('build_stage');
    require('../../../ci/build_stage');
    console.timeEnd('build_stage');

    console.info('build_push start');
    console.time('build_push');
    require('../../../ci/build_push');
    console.timeEnd('build_push');

    console.info('publish_clownductor start');
    console.time('publish_clownductor');
    require('../../../ci/publish_clownductor');
    console.timeEnd('publish_clownductor');
})();
