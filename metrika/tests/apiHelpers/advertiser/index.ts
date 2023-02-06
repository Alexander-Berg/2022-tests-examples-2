import {
    createAdvertiser,
    deleteAdvertiser,
    getAdvertisers,
} from 'server/api/admetrica/advertisers';
import { bindRequest } from 'tests/utils/api';

const boundGetAdvertisers = bindRequest(getAdvertisers);
const boundDeleteAdvertiser = bindRequest(deleteAdvertiser);
const boundCreateAdvertiser = bindRequest(createAdvertiser);

const deleteAdvertiserByName = async (name: string) => {
    const { advertisers } = await boundGetAdvertisers({});

    const advertiser = advertisers.find((advertiser) => {
        return advertiser.name === name;
    });

    if (advertiser) {
        await boundDeleteAdvertiser({
            id: advertiser.advertiserId,
        });
    }
};

const deleteAdvertiserById = async (id: number) => {
    await boundDeleteAdvertiser({ id });
};

const getNewAdvertiseId = async () => {
    const advertiser = await boundCreateAdvertiser({
        payload: {
            name: 'test',
            postClickDays: 30,
            postViewDays: 30,
            grants: [],
        },
    });

    return advertiser.advertiserId;
};

const createAdvertiserWithName = async (name: string) => {
    const advertiser = await boundCreateAdvertiser({
        payload: {
            name,
            postClickDays: 30,
            postViewDays: 30,
            grants: [],
        },
    });

    return advertiser;
};

export {
    deleteAdvertiserByName,
    deleteAdvertiserById,
    getNewAdvertiseId,
    createAdvertiserWithName,
};
