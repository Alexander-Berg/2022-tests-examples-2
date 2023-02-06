import path from 'path';

import {appDirectory, rootResolve, serviceResolve} from '@/src/lib/resolve';

export const PATH_TO_HERMIONE_HTML_REPORT = path.relative(
    appDirectory,
    rootResolve('reports/.dev/reports/pigeon-hermione-reports')
);
export const PATH_TO_HERMIONE_CONFIG = serviceResolve('out/src/tests/e2e/config/hermione.config.js');
