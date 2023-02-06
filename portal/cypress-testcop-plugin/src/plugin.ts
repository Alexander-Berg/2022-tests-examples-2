import {StatsReporter} from './stats-reporter';
import {JsonReporter} from './json-reporter';
import {getSkipsAndMutes} from './testcop';
import {CypressTestcopPluginConfig, CypressTestcopReporterConfig, parseConfig} from './config';

/**
 * Configures hermione-muted-tests plugin to work with cypress.
 * Stability index and auto mutes features are currently missing
 * @param pluginConfig
 * @param reporterConfig
 * @returns {Cypress.PluginConfig}
 */
export function CypressTestcopPlugin(
    pluginConfig: CypressTestcopPluginConfig,
    reporterConfig: CypressTestcopReporterConfig = {},
): Cypress.PluginConfig {
    const testcopConfig = parseConfig(pluginConfig);

    return async (on: Cypress.PluginEvents, config: Cypress.PluginConfigOptions) => {
        if (!testcopConfig.enabled) {
            return config;
        }

        const skipsAndMutes = await getSkipsAndMutes(testcopConfig);
        const statsReporter = new StatsReporter(testcopConfig, reporterConfig, skipsAndMutes);
        const jsonReporter = new JsonReporter(testcopConfig, reporterConfig, skipsAndMutes);

        config.env.skiplist = JSON.stringify(Object.keys(skipsAndMutes.skips ?? {}));
        config.env.mutelist = JSON.stringify(Object.keys(skipsAndMutes.mutes ?? {}));
        config.env.skipbrowser = reporterConfig.browser;

        on('after:run', async results => {
            if (results.status === 'failed') {
                console.error('Cypress Testcop Plugin: Cypress run failed. Report not saved');
                console.error(results.message);
                return;
            }
            await Promise.allSettled([
                statsReporter.report(results),
                jsonReporter.report(results),
            ]).then(result => result.filter(s => s.status === 'rejected').forEach((e) => console.log(e)));
        });
        console.log('Cypress Testcop plugin: Successfully inited');
        return config;
    };
}
