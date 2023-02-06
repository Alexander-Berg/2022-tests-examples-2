import {serviceResolve} from '@/src/lib/resolve';

// eslint-disable-next-line @typescript-eslint/no-var-requires
require('dotenv').config({path: serviceResolve('.env')});
