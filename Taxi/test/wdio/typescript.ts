import type {Options} from '@wdio/types';

export const typescriptConfig: Pick<Options.Testrunner, 'autoCompileOpts'> = {
    autoCompileOpts: {
        autoCompile: true,
        // see https://github.com/TypeStrong/ts-node#cli-and-programmatic-options
        tsNodeOpts: {
            transpileOnly: true,
            project: 'test/tsconfig.json',
        },
    },
};
