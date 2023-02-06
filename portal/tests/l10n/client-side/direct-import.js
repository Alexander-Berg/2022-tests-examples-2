import {l10n} from '../../../lib/home.l10n';

export function testDirectImport() {
    return l10n('client.direct');
}

export function evalDirectImport(subkey) {
    return l10n(`client.evalDirect.${subkey}`);
}

export function tryCatch() {
    var res = '';
    try {
        return l10n('client.try');
    } catch (err) {
        // Тут специально такая конструкция, чтобы проверить обработку присвоения
        res = err;
    }
    return 'Not found ' + res;
}
