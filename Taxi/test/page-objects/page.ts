import {AUTH_CONFIG} from '../config/auth';

interface ConstructorProps {
    baseUrl: string;
}

export class Page {
    protected baseUrl: ConstructorProps['baseUrl'] = '';

    public constructor(props?: ConstructorProps) {
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
