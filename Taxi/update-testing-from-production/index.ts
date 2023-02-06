import {startWorker} from '@/src/utils/start-worker';
import {dumpFromProductionReadOnly} from 'cli/db/roll-production-dump-command';

void startWorker(async () => {
    await dumpFromProductionReadOnly();
});
