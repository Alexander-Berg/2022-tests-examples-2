import assert from 'assert';
import {promises as fs} from 'fs';
import {resolve} from 'path';

import {bash, kill, storage} from './utils';

enum OutputFile {
    DETACHED = 'detached',
    ASYNC_EXIT_HANDLER = 'async-exit-handler',
    KILL_DETACHED = 'kill-detached'
}

describe('package "commands"', () => {
    const testOutputDir = resolve(__dirname, '.tst');
    const getTestOutputFile = (key: string) => resolve(testOutputDir, key + '.log');

    beforeAll(async () => {
        await fs.mkdir(testOutputDir, {recursive: true});
    });

    it('should get and set storage', async () => {
        await storage.set('test', {foo: 'bar'});
        const value = await storage.get('test');
        expect(value).toEqual({foo: 'bar'});
    });

    it('should delete storage key', async () => {
        await storage.set('test', 42);
        expect(await storage.get('test')).toEqual(42);
        await storage.del('test');
        expect(await storage.get('test')).toBeUndefined();
    });

    it('should drain storage key', async () => {
        await storage.set('test', 'foo');
        expect(await storage.get('test')).toEqual('foo');
        expect(await storage.drain('test')).toEqual('foo');
        expect(await storage.get('test')).toBeUndefined();
    });

    it('should bash detached', async () => {
        const outFile = getTestOutputFile(OutputFile.DETACHED);
        const child = bash(`echo OK > ${outFile}`, {detached: true, silent: true});

        expect(child.pid === process.pid).toBeFalsy();

        await waitMs(100);

        const content = await fs.readFile(outFile, {encoding: 'utf8'});
        expect(content.trim()).toBe('OK');
    });

    it('should bind async exit handler', async () => {
        const outFile = getTestOutputFile(OutputFile.ASYNC_EXIT_HANDLER);

        const script = `
const {onExit, asyncToSync} = require('.');

const asyncExitHandler = () => new Promise((resolve) => {
    console.log('INIT asyncExitHandler');
    setTimeout(() => {
        console.log('DONE asyncExitHandler');
        resolve();
    }, 300);
});

const syncExitHandler = asyncToSync(async () => {
    await asyncExitHandler();
});

onExit(() => syncExitHandler());
`;
        await bash(`node -e "${script}" > ${outFile}`, {silent: true});
        await waitMs(500);

        const content = await fs.readFile(outFile, {encoding: 'utf8'});
        expect(content.trim()).toBe(`INIT asyncExitHandler
DONE asyncExitHandler`);
    });

    it('should kill detached process', async () => {
        const outFile = getTestOutputFile(OutputFile.KILL_DETACHED);

        const script = `
const {onExit} = require('.');

onExit(() => console.log('BYE'));

setTimeout(() => {}, 600000);
`;
        const {pid} = bash(`node -e "${script}" > ${outFile}`, {silent: true, detached: true});
        assert(pid, 'runtime error');

        await waitMs(500);
        await kill(pid, 'SIGINT');
        await waitMs(500);

        const content = await fs.readFile(outFile, {encoding: 'utf8'});
        expect(content.trim()).toBe('BYE');
    });
});

function waitMs(ms: number) {
    return new Promise<void>((resolve) => setTimeout(() => resolve(), ms));
}
