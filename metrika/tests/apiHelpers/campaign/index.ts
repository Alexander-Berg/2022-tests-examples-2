import {
    deleteCampaign,
    getList,
    createCampaign as createCampaignRequest,
} from 'server/api/admetrica/campaigns';
import { bindRequest } from 'tests/utils/api';

const boundGetCampaigns = bindRequest(getList);
const boundDeleteCampaign = bindRequest(deleteCampaign);
const boundCreateCampaign = bindRequest(createCampaignRequest);

const deleteCampaignByName = async (name: string) => {
    const { campaigns } = await boundGetCampaigns({});

    const campaign = campaigns.find((campaign) => {
        return campaign.name === name;
    });

    if (campaign) {
        await boundDeleteCampaign({
            advertiserId: campaign.advertiserId,
            id: campaign.campaignId,
        });
    }
};

type Options = {
    advertiserId: number;
    name: string;
    landingId: number;
};

const createCampaign = ({ advertiserId, name, landingId }: Options) => {
    return boundCreateCampaign({
        advertiserId,
        payload: {
            name,
            dateEnd: '2020-02-20',
            dateStart: '2020-02-20',
            planClicks: 10,
            planCpc: 10,
            planCpm: 10,
            planCtr: 10,
            planImpressions: 10,
            goals: [],
            goalPlans: [],
            viewabilityStandard: 'yandex',
            placements: [
                {
                    landingId,
                    name: 'test',
                    site: {
                        siteId: 12001,
                        name: 'Яндекс.Директ',
                        url: 'direct.yandex.ru',
                        tracking: true,
                        viewability: true,
                        siteType: 'adv_network' as const,
                    },
                    creatives: [{ comment: 'comment' }],
                    placementType: 'banner',
                    pricingModel: 'cpm',
                    siteId: 12001,
                    cost: 10,
                    volume: 10,
                },
            ],
        },
    });
};

export { deleteCampaignByName, createCampaign };
