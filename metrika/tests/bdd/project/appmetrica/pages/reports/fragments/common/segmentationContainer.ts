
import { Locator } from "playwright-core";
import { BaseComponent} from "../../../../../../lib";
import {ButtonReportElement} from "../../elements";

export class SegmentationContainerFragment extends BaseComponent {
    firstPlusButton: ButtonReportElement;
    secondPlusButton: ButtonReportElement;
    savedSegmentsButton: ButtonReportElement;
    clearSegmentsButton: ButtonReportElement;

    constructor(locator: Locator, parent: any) {
        super(locator, parent);
        this.firstPlusButton = new ButtonReportElement(
            this.locator.locator(".SectionHeader__addFilter").nth(1),
            this,
            'Segment by users button'
        );
        this.secondPlusButton = new ButtonReportElement(
            this.locator.locator(".SectionHeader__addFilter").nth(2),
            this,
            'Second segments button'
        );
        this.savedSegmentsButton = new ButtonReportElement(
            this.locator.locator(".MySegments button"),
            this,
            'Saved segments button'
        );
        this.clearSegmentsButton = new ButtonReportElement(
            this.locator.locator(".ClearFilters__btn"),
            this,
            'Clear all segments button'
        );
    }
}
