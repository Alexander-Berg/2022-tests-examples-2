export interface CypressTestcopPluginConfig {
    enabled?: boolean;
    project: string;
    branch: string;
    tool?: string;
}

export interface CypressTestcopReporterConfig {
    reportFile?: string;
    browser?: string;

    jsonEnabled?: boolean;

    statsEnabled?: boolean;
    ytPath?: string;
    ytProxy?: string;
}

export const parseConfig = (config: CypressTestcopPluginConfig) => {
    if (!config.project) {
        throw new Error('Cypress Testcop Plugin: config.project is empty');
    }

    return {
        ...config,
        enabled: process.env.DISABLE_CYPRESS_TESTCOP ? false : (config.enabled ?? true),
        tool: config.tool || 'cypress',
    };
};
