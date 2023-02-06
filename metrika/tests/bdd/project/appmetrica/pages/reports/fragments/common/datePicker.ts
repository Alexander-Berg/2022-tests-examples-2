
import { Locator } from "playwright-core";
import { BaseComponent} from "../../../../../../lib";
import {ButtonReportElement} from "../../elements";

export class DatePickerFragment extends BaseComponent {
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
            this.locator.locator("[value='today']"),
            this,
            'Today'
        );
        this.yesterday = new ButtonReportElement(
            this.locator.locator("[value='yesterday']"),
            this,
            'Yesterday'
        );
        this.week = new ButtonReportElement(
            this.locator.locator("[value='week']"),
            this,
            'Week'
        );
        this.twoWeeks = new ButtonReportElement(
            this.locator.locator("[value='two-weeks']"),
            this,
            'Two weeks'
        );
        this.month = new ButtonReportElement(
            this.locator.locator("[value='month']"),
            this,
            'Month'
        );
        this.dateRangeButton = new ButtonReportElement(
            this.locator.locator(".date-range-selector__selector-button"),
            this,
            'Calendar init button'
        );
        this.groupByButton = new ButtonReportElement(
            this.locator.locator(".ControlsBar__item [role='listbox']"),
            this,
            'Group by time dropdown init button'
        );
    }
}
