import {getRequests} from '../';

const api = {
    request: (path, data) => data
};

const defaultServices = [
    'marketData',
    'musicData',
    'collectionsData',
    'favMarketData',
    'favAfishaData',
    'diskData',
    'videoData',
    'afishaData',
    'videoData',
    'videoData',
    'videoData',
    'videoData'
];

const toLoad = [
    'marketData',
    'musicData',
    'collectionsData',
    'favMarketData',
    'favAfishaData',
    'diskData',
    'videoData',
    'afishaData'
];

describe('Dashboard', () => {
    describe('getRequests', () => {
        test('if client', () => {
            const getData = (service) => ({track_id: 'trackId', service, pageSize: 11, page: 1, lang: 'ru'});
            const publicId = 'publicId';
            const data = getRequests(false, {api, trackId: 'trackId', publicId, lang: 'ru'}, toLoad);
            const requests = [];

            let videoPage = 0;

            for (let i = 0; i < data.services.length; i++) {
                const service = data.services[i];

                requests.push(getData(service));

                if (service === 'videoData') {
                    requests[i].pageSize = 4;
                    requests[i].page = ++videoPage;
                }

                if (service === 'collectionsData') {
                    requests[i].publicId = publicId;
                }
            }

            expect(data).toEqual({
                videoDataCount: 5,
                services: defaultServices,
                requests
            });
        });
        it('should return 0 services', () => {
            expect(getRequests(false, {}).services.length).toEqual(0);
        });
    });
});
