import { campaigns as reducer } from '../campaigns';
import * as actions from '../../actions/campaign';
import { Campaign } from 'shared/types/api';

describe('campaigns reducer', () => {
    it('should append campaign to state', () => {
        expect(
            reducer(
                {},
                actions.getCampaign.success({
                    campaignId: 1,
                    name: 'Немцы фольц осень 2018',
                    dateStart: '2018-06-23',
                    dateEnd: '2018-10-23',
                    realDateStart: '2018-06-23',
                    realDateEnd: '2018-10-23',
                    status: 'active',
                    permission: 'own',
                    planImpressions: 1,
                    planClicks: 1,
                    planCtr: 1,
                    planCpm: 1,
                    planCpc: 1,
                    goals: [],
                    placements: [],
                    viewabilityStandard: 'mrc',
                    goalPlans: [],
                    landing: {
                        landingId: 237,
                        name: 'Test Landing 2',
                        url: 'http://url.com',
                    },
                    createTime: '2019-01-20 13:59:47',
                } as Campaign),
            ),
        ).toEqual({
            1: {
                campaignId: 1,
                name: 'Немцы фольц осень 2018',
                dateStart: '2018-06-23',
                dateEnd: '2018-10-23',
                realDateStart: '2018-06-23',
                realDateEnd: '2018-10-23',
                status: 'active',
                permission: 'own',
                planImpressions: 1,
                planClicks: 1,
                planCtr: 1,
                planCpm: 1,
                planCpc: 1,
                goals: [],
                placements: [],
                viewabilityStandard: 'mrc',
                goalPlans: [],
                landing: {
                    landingId: 237,
                    name: 'Test Landing 2',
                    url: 'http://url.com',
                },
                createTime: '2019-01-20 13:59:47',
            },
        });
    });
});
