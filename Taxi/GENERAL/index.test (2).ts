/**
 * @jest-environment node
 */
import Bunker, {getBunkerUrl} from '.';

const BUNKER_HOST = 'http://bunker-api-dot.yandex.net';
describe('BunkerService', () => {
    const config = {host: BUNKER_HOST};

    describe('getBunkerUrl', () => {
        it('собирает путь к действию cat без параметра', () =>
            expect(getBunkerUrl(config)('cat')).toEqual('http://bunker-api-dot.yandex.net/v1/cat'));
        it('собирает путь к действию cat с параметром', () => {
            expect(getBunkerUrl(config)('cat', {node: '/tanker'})).toEqual(
                `http://bunker-api-dot.yandex.net/v1/cat?node=${encodeURIComponent('/tanker')}`
            );
            expect(getBunkerUrl(config)('cat/', {node: '/taxi-corp-client/tanker'})).toBe(
                'http://bunker-api-dot.yandex.net/v1/cat/?node=%2Ftaxi-corp-client%2Ftanker'
            );
        });
    });

    describe('getKeyContent', () => {
        const service = Bunker({host: BUNKER_HOST});
        it('может нормально получить контент ноды', async () => {
            expect((await service.cat('/taxi-corp-client/tanker')).export_info).not.toBeNull();
        });
    });

    describe('ls', () => {
        const service = Bunker({host: BUNKER_HOST});
        it('может нормально получить контент ноды', async () => {
            /* eslint-disable no-console */
            expect(console.info(await service.ls('/taxi-corp-client'))).not.toBeNull();
            expect(console.info(await service.ls('/taxi-corp-client', 'stable'))).not.toBeNull();
            /* eslint-enable */
        });
    });
});
