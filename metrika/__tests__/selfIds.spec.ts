import sinon, { SinonStub } from 'sinon';
import * as utils from '@src/utils/fnv32a';
import * as inject from '@inject';
import { expect } from 'chai';
import * as resourses from '../const';
import { getSelfIds } from '../selfIds';

describe('self id for resource timings', () => {
    const sandbox = sinon.createSandbox();
    const testName = 'test';
    let resourceIdStub: SinonStub<any, any>;
    beforeEach(() => {
        resourceIdStub = sandbox.stub(inject, 'resourceId').value(testName);
        sandbox.stub(resourses, 'RESOURCES').value({
            'mc.yandex.ru/watch.js': 1,
        });
        sandbox.stub(utils, 'fnv32a').callsFake((a: string) => a as any);
    });
    afterEach(() => {
        sandbox.restore();
    });
    it('it skip existing resourse', () => {
        resourceIdStub.value('watch.js');
        const result = getSelfIds({} as any);
        expect(result).to.be.deep.eq({
            'mc.yandex.com/watch.js': 1,
            'cdn.jsdelivr.net/npm/yandex-metrica-watch/watch.js': 1,
        });
    });
    it('returns prefixed bundles', () => {
        const result = getSelfIds({} as any);
        expect(result).to.be.deep.eq({
            'mc.yandex.ru/test': 1,
            'mc.yandex.com/test': 1,
            'cdn.jsdelivr.net/npm/yandex-metrica-watch/test': 1,
        });
    });
});
