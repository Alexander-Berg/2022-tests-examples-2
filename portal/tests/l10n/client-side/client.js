import {localeClient} from './b';
import {l10n} from '../../../lib/home.l10n';
import {execView} from './client-side';

export function testClient() {
    return execView(localeClient, {
        client: l10n('client.translation')
    });
}
