import {TestcopAPI, TestSkipsResult} from '@yandex-int/testcop-api';
import {CypressTestcopPluginConfig} from './config';

const getReleaseBranch = () => {
    const branch = process.env.BUILD_BRANCH || process.env.TRENDBOX_BRANCH || '';

    return /(^|\/)release(s|)\//.test(branch) ? branch : null;
};

export const getSkipsAndMutes = async (config: CypressTestcopPluginConfig): Promise<TestSkipsResult> => {
    const api = TestcopAPI.create('');
    const skipsBranch = getReleaseBranch() || config.branch;

    return await api.getTestSkips({
        project: config.project,
        tool: config.tool,
        skipsBranch,
        flakyStatsBranch: config.branch,
        isFlakyTestsStatsRequired: true,
    });
};
