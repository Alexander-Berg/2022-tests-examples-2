import {AUTH_CONFIG} from '../../../config/auth';
import {Page} from '../../page';

export class BasePage extends Page {
    public constructor() {
        super({
            baseUrl: AUTH_CONFIG.PASSPORT.URL,
        });
    }
}
