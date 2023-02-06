import path from 'path';
import { spawn } from 'child_process';

export function runSubTest(testPath: string): Promise<void> {
    const jestPath = path.resolve(__dirname, '../../../../node_modules/.bin/jest');
    const configPath = path.resolve(__dirname, '../../jest.config.js');

    return new Promise((resolve, reject) => {
        const jest = spawn(jestPath, ['--config', configPath, '--runTestsByPath', testPath, '--testPathIgnorePatterns']);

        let stderr = '';

        jest.stderr.on('data', data => {
            stderr += data;
        });

        jest.on('close', code => {
            if (code) {
                reject(stderr);
            } else {
                resolve();
            }
        });
    });
}
