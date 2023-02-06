import { advertisers as reducer } from '../advertisers';
import * as actions from '../../actions/advertiser';

describe('advertiser reducer', () => {
    it('should append advertiser to state', () => {
        expect(
            reducer(
                {},
                actions.getAdvertiser.success({
                    advertiserId: 1,
                    name: 'Advertiser',
                    postClickDays: 1,
                    postViewDays: 7,
                    grants: [],
                    permission: 'own',
                    owner: 'test',
                    createTime: '2019-07-17 16:42:12',
                    features: [],
                    counters: [],
                }),
            ),
        ).toEqual({
            1: {
                advertiserId: 1,
                name: 'Advertiser',
                postClickDays: 1,
                postViewDays: 7,
                grants: [],
                permission: 'own',
                owner: 'test',
                createTime: '2019-07-17 16:42:12',
                features: [],
                counters: [],
            },
        });
    });

    it('should append advertisers to state', () => {
        expect(
            reducer(
                {},
                actions.setAdvertisersDict([
                    {
                        advertiserId: 1,
                        name: 'Advertiser 1',
                        activeCampaignsCnt: 1,
                        archivedCampaignsCnt: 7,
                        goalsCnt: 5,
                        landingsCnt: 2,
                        permission: 'own',
                        owner: 'self',
                        grants: [],
                        createTime: '2019-07-17 16:42:12',
                        features: [],
                        counters: [],
                    },
                    {
                        advertiserId: 2,
                        name: 'Advertiser 2',
                        activeCampaignsCnt: 1,
                        archivedCampaignsCnt: 7,
                        goalsCnt: 6,
                        landingsCnt: 2,
                        permission: 'edit',
                        owner: 'self',
                        grants: [],
                        createTime: '2019-07-17 16:42:12',
                        features: [],
                        counters: [],
                    },
                ]),
            ),
        ).toEqual({
            1: {
                advertiserId: 1,
                name: 'Advertiser 1',
                activeCampaignsCnt: 1,
                archivedCampaignsCnt: 7,
                goalsCnt: 5,
                landingsCnt: 2,
                permission: 'own',
                owner: 'self',
                grants: [],
                createTime: '2019-07-17 16:42:12',
                features: [],
                counters: [],
            },
            2: {
                advertiserId: 2,
                name: 'Advertiser 2',
                activeCampaignsCnt: 1,
                archivedCampaignsCnt: 7,
                goalsCnt: 6,
                landingsCnt: 2,
                permission: 'edit',
                owner: 'self',
                grants: [],
                createTime: '2019-07-17 16:42:12',
                features: [],
                counters: [],
            },
        });
    });
});
