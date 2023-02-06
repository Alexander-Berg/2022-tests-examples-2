import { toAdblockFormat, fromAdblockFormat } from '..';

const MAP = {
    advertiserId: 'catId',
    ohMyGodThisIsAdId: 'notAdvertiserId',
};
const REVERTED_MAP = Object.entries(MAP).reduce(
    (result, [key, value]) => ({
        ...result,
        [value]: key,
    }),
    {},
);

const canonicalParams =
    'advertiserId=155&someField=value&ohMyGodThisIsAdId=777';
const canonicalParamsObject: { [key: string]: string } = {};
// в тайпингах нет entries
new URLSearchParams(canonicalParams).forEach((value, key) => {
    canonicalParamsObject[key] = value;
});

const adblockParams = 'catId=155&someField=value&notAdvertiserId=777';
const adblockParamsObject: { [key: string]: string } = {};
// в тайпингах нет entries
new URLSearchParams(adblockParams).forEach((value, key) => {
    adblockParamsObject[key] = value;
});

describe('toAdblockFormat', () => {
    it('URLSearchParams', () => {
        const params = new URLSearchParams(canonicalParams);
        const result = toAdblockFormat(params, MAP);
        expect(result.toString()).toMatchSnapshot();
    });

    it('string', () => {
        const result = toAdblockFormat(canonicalParams, MAP);
        expect(result.toString()).toMatchSnapshot();
    });

    it('object', () => {
        const result = toAdblockFormat(canonicalParamsObject, MAP);
        expect(result.toString()).toMatchSnapshot();
    });
});

describe('fromAdblockFormat', () => {
    it('URLSearchParams', () => {
        const params = new URLSearchParams(adblockParams);
        const result = fromAdblockFormat(params, REVERTED_MAP);
        expect(result.toString()).toMatchSnapshot();
    });

    it('string', () => {
        const result = fromAdblockFormat(adblockParams, REVERTED_MAP);
        expect(result.toString()).toMatchSnapshot();
    });

    it('object', () => {
        const result = fromAdblockFormat(adblockParamsObject, REVERTED_MAP);
        expect(result.toString()).toMatchSnapshot();
    });
});
