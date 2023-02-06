import legacyPlatform from '../legacy-platform';

const nextStub = () => {
    /* noop */
};

describe('Detect legacy platform', () => {
    it('Should throw error if arguments is invalid', () => {
        expect(() => {
            legacyPlatform();
        }).toThrow();

        expect(() => {
            legacyPlatform({predicate: {}});
        }).toThrow();
    });

    it('Should be detect legacy platform if predicate return true', () => {
        const middleware = legacyPlatform({predicate: () => true});
        const requestStub = {
            isLegacyPlatform: false
        };
        middleware(requestStub, null, nextStub);
        expect(requestStub.isLegacyPlatform).toBeTruthy();
    });

    it('Shouldn\'t be detect legacy platform if predicate return false', () => {
        const middleware = legacyPlatform({predicate: () => false});
        const requestStub = {
            isLegacyPlatform: false
        };
        middleware(requestStub, null, nextStub);
        expect(requestStub.isLegacyPlatform).toBeFalsy();
    });

    it('Should be detect legacy platform if any predicate return true', () => {
        const middleware = legacyPlatform({predicate: [() => false, () => true]});
        const requestStub = {
            isLegacyPlatform: false
        };
        middleware(requestStub, null, nextStub);
        expect(requestStub.isLegacyPlatform).toBeTruthy();
    });

    it('Shouldn\'t be detect legacy platform if every predicate return false', () => {
        const middleware = legacyPlatform({predicate: [() => false, () => false]});
        const requestStub = {
            isLegacyPlatform: false
        };
        middleware(requestStub, null, nextStub);
        expect(requestStub.isLegacyPlatform).toBeFalsy();
    });
});
