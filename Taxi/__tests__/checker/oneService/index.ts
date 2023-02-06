import {config} from 'dotenv';

(function () {
    config({path: 'tools/arcadia/__tests__/checker/oneService/.env.arcadia.test'});

    console.time('build_base');
    require('../../../ci/build_base');
    console.timeEnd('build_base');
})();
