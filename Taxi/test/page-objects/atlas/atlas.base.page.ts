import {AUTH_CONFIG} from '../../config/auth';
import {Page} from '../page';

export type DataSource =
    {
        name: string,
        type: string,
        cluster: string,
        path: string,
        isPartitioned: boolean,
        key: string,
        template: string,
        description: string,
    }

export class AtlasBasePage extends Page {

    public async waitForElement(element: WebdriverIO.Element | undefined) {

        try{
            await element?.waitForDisplayed();
        }
        catch(error){
            console.info(error);
        }
    }

    public constructor() {
        super({
            baseUrl: AUTH_CONFIG.APP_URL,
        });

    }


}

export const atlasBasePage = new AtlasBasePage();
