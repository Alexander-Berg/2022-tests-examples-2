import {Page} from "playwright-core";
import {
    SegmentationContainerFragment
} from "./fragments";
import {CommonPage} from "./commonPage";


export class UAPage extends CommonPage {
    segmentationContainer: SegmentationContainerFragment;

    constructor(page: Page) {
        super(page);
        this.segmentationContainer = new SegmentationContainerFragment(
            this.page.locator('.advanced-statistic__segmentation-container'),
            this);
    }
}

export function getUAPage(page: Page) {
    return new UAPage(page);
}

