import * as path from 'path';
import * as fs from 'fs';
import * as vm from 'vm';
import mod from 'module';
// eslint-disable-next-line import/no-extraneous-dependencies
import webpack from 'webpack';
import { getConfig } from '../../getServerWebpackConfig';

function runFileInContext(filePath: string, context: vm.Context) {
    const contents = fs.readFileSync(filePath, 'utf-8');
    vm.runInContext(mod.wrap(contents), context, {
        filename: filePath
    })(null, require, null, filePath, path.dirname(filePath));
}

export async function buildServerBundle(rootDir: string) {
    let serverConfig = getConfig({
        rootDir,
        outputDir: path.resolve(rootDir, 'dist'),
        isProd: true
    });
    serverConfig.entry = { server: '?project=all' };
    const compiler = webpack(serverConfig);

    return new Promise<void>((resolve, reject) => {
        compiler.run((err: Error | undefined, stats) => {
            try {
                if (err) {
                    reject(err);
                    return;
                } else if (stats && stats.hasErrors()) {
                    const json = stats.toJson();
                    if (json.errors) {
                        reject(new Error(json.errors.length > 1 ? json.errors.join() : String(json.errors[0])));
                    } else {
                        reject(new Error('Unknown'));
                    }
                    return;
                }

                resolve();
            } catch (err2) {
                reject(err2);
            }
        });
    });
}

export function getServerExecView(rootDir: string, levelName: string) {
    const fileContent = fs.readFileSync(path.resolve(rootDir, 'dist', 'server.js'), 'utf-8');

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let contextBase: { [key: string]: any } = {};
    contextBase.global = contextBase;
    contextBase.require = require;
    let context = vm.createContext(contextBase);
    runFileInContext(path.resolve(__dirname, '../../../common/test/viewEnv.js'), context);
    runFileInContext(path.resolve(__dirname, '../../../js_libs/core.js'), context);
    runFileInContext(path.resolve(__dirname, '../../../common/test/viewEnv2.js'), context);
    vm.runInContext(fileContent, context);

    return context.home[levelName].execView;
}
