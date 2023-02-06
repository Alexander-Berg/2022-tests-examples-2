import { Locator } from "playwright-core";
import {BaseComponent, Collection} from "../../../../../../../lib";
import {ButtonReportElement} from "../../../elements";

export class TableHeadAudienceFragment extends BaseComponent {
    sortButtons: Collection<ButtonReportElement>;
    loadUsersChart: ButtonReportElement;
    loadNewUsersChart: ButtonReportElement;
    loadNewUsersShareChart: ButtonReportElement;
    switchPercentsUsers: ButtonReportElement;
    switchPercentsNewUsers: ButtonReportElement;

    constructor(locator: Locator, parent: any){
        super(locator, parent, "Table head");

        this.sortButtons = new Collection<ButtonReportElement>(
            this.locator.locator(".statistic-table-adapter__sort-button-title"),
            this,
            ButtonReportElement,
            "Sort asc/desc button"
        );
        this.loadUsersChart = new ButtonReportElement(
            this.locator.locator("[value='ym:u:activeUsers'][type='radio']"),
            this,
            "Show Users on chart"
        );
        this.switchPercentsUsers = new ButtonReportElement(
            this.locator.locator("[value='ym:u:activeUsers'][role='button']"),
            this,
            "Switch Users metric to percents"
        );
        this.loadNewUsersChart = new ButtonReportElement(
            this.locator.locator("[value='ym:u:NewUsers'][type='radio']"),
            this,
            "Show New users on chart"
        );
        this.switchPercentsNewUsers = new ButtonReportElement(
            this.locator.locator("[value='ym:u:NewUsers'][role='button']"),
            this,
            "Switch New users metric to percents"
        );
        this.loadNewUsersShareChart = new ButtonReportElement(
            this.locator.locator("[value='ym:u:newUsersShare'][type='radio']"),
            this,
            "Show New users share on chart"
        );
    }
}
