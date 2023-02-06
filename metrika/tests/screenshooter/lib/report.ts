import {Mock} from "./mock";

export type Report = {
    url: string;
    name?: string;
    selector: string;
    loaderSelector: string;
    isMobile?: boolean;
    mobileSelector?: string;
    mobileLoaderSelector?: string;
    compositeImage?: boolean;
    ignoreElements?: string[];
    pause?: number;
    mocks?: Mock[];
};
