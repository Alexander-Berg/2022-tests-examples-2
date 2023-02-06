
import { Locator } from "playwright-core";
import {BaseComponent, InputElement, TextElement} from "../../../../../../../lib";
import {ButtonReportElement} from "../../../elements";

export class TableControlsFragment extends BaseComponent {
    currencyButton: ButtonReportElement;
    addGropingsAndMetricsButton: ButtonReportElement;
    searchField: InputElement;
    multilevelButton: ButtonReportElement;
    drilldownButton: ButtonReportElement;
    currentGroupingsTitle: TextElement;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Table controls");

        this.currencyButton = new ButtonReportElement(
            this.locator.locator(".ControlsBar.ControlsBar_size_s:nth-child(2) .ControlsBar__item:nth-child(1)"),
            this,
            "Currency switcher button"
        );
        this.addGropingsAndMetricsButton = new ButtonReportElement(
            this.locator.locator(".ControlsBar.ControlsBar_size_s:nth-child(2) .ControlsBar__item:nth-child(2)"),
            this,
            "Add groupings and metrics"
        );
        this.multilevelButton = new ButtonReportElement(
            this.locator.locator("[value='multilevel']"),
            this,
            "Switch to multilevel view"
        );
        this.drilldownButton = new ButtonReportElement(
            this.locator.locator("[value='drilldown']"),
            this,
            "Switch to drilldown view"
        );
        this.currentGroupingsTitle = new TextElement(
            this.locator.locator(".sc-bWFPNQ.khWvJw"),
            this,
            "Text representation of applied groupings"
        );
        this.searchField = new InputElement(
            this.locator.locator(".textinput__control"),
            this,
            "Search field"
        );
    }
}
