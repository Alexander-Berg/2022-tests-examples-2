import { Hermione } from 'hermione';
import { getConfig } from 'server/lib/bishop';

const configsPlugin = (hermione: Hermione) => {
    hermione.on(hermione.events.INIT, () => {
        return getConfig();
    });
};

module.exports = configsPlugin;
