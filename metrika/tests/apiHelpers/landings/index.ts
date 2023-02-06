import {
    createLanding,
    deleteLanding,
    getList,
} from 'server/api/admetrica/landings';
import { bindRequest } from 'tests/utils/api';

const bindedGetLandings = bindRequest(getList);
const bindedDeleteLanding = bindRequest(deleteLanding);
const bindedCreateLanding = bindRequest(createLanding);

const deleteLandingByName = async (name: string, advertiserId: string) => {
    const { landings } = await bindedGetLandings({ advertiserId });

    const landing = landings.find((landing) => {
        return landing.name === name;
    });

    if (landing) {
        await bindedDeleteLanding({
            advertiserId,
            id: landing.landingId,
        });
    }
};

const deleteLandingById = async (id: number, advertiserId: string) => {
    await bindedDeleteLanding({
        id,
        advertiserId,
    });
};

const getNewLanding = async (advertiserId: number) => {
    return bindedCreateLanding({
        advertiserId,
        payload: {
            name: 'test',
            url: 'https://test.ru',
        },
    });
};

export { deleteLandingByName, deleteLandingById, getNewLanding };
