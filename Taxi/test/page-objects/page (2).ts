import {AUTH_CONFIG} from '../config/auth';
import {PageAbstract} from '../utils/types/page';

interface ConstructorProps {
    baseUrl: string;
}

export class Page extends PageAbstract {
    protected baseUrl: ConstructorProps['baseUrl'] = '';

    public constructor(props?: ConstructorProps) {
        super();

        const {baseUrl} = props || {};

        if (baseUrl) {
            this.baseUrl = baseUrl || AUTH_CONFIG.APP_URL;
        }
    }

    public open(path: string) {
        return browser.url(`${this.baseUrl}${path}`);
    }

    public selector(...args: Parameters<typeof $>) {
        return $(...args);
    }

    public multiplySelector(...args: Parameters<typeof $$>) {
        return $$(...args);
    }
}
