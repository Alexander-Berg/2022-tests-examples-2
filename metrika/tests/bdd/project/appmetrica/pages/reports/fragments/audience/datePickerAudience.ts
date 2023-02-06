
import { Locator } from "playwright-core";
import { BaseComponent} from "../../../../../../lib";
import {ButtonReportElement} from "../../elements";

export class DatePickerAudienceFragment extends BaseComponent {
    today: ButtonReportElement;
    yesterday: ButtonReportElement;
    week: ButtonReportElement;
    twoWeeks: ButtonReportElement;
    month: ButtonReportElement;
    dateRangeButton: ButtonReportElement;
    groupByButton: ButtonReportElement;

    constructor(locator: Locator, parent: any) {
        super(locator, parent);
        this.today = new ButtonReportElement(
            this.locator.locator(".period__today"),
            this,
            'Today'
        );
        this.yesterday = new ButtonReportElement(
            this.locator.locator(".period__yesterday"),
            this,
            'Yesterday'
        );
        this.week = new ButtonReportElement(
            this.locator.locator(".period__week"),
            this,
            'Week'
        );
        this.twoWeeks = new ButtonReportElement(
            this.locator.locator(".period__two-weeks"),
            this,
            'Two weeks'
        );
        this.month = new ButtonReportElement(
            this.locator.locator(".period__month"),
            this,
            'Month'
        );
        this.dateRangeButton = new ButtonReportElement(
            this.locator.locator(".date-range-selector__selector-button"),
            this,
            'Calendar init button'
        );
        this.groupByButton = new ButtonReportElement(
            this.locator.locator(".period__grouping-wrapper.period__item button"),
            this,
            'Group by time dropdown init button'
        );
    }
}
