import './one-a.styl';
import './nested-imports.client.js';
import './style-in-client.client.js';

import {onlyOne} from './imported.view.js';
import {importedNoClient} from './imported-no-client.view.js';

onlyOne();
importedNoClient();

