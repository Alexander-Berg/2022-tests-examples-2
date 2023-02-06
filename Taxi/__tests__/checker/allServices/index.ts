import {config} from 'dotenv';

(function () {
    config({path: 'arcadia/__tests__/checker/oneService/.env.arcadia.test'});

    require('../../../ci/build_base');
})();
