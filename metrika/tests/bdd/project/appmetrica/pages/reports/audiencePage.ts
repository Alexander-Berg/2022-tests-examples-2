import {BasePage} from "../../../../lib";
import {Page} from "playwright-core";
import {
    DatePickerAudienceFragment,
    SegmentationContainerFragment,
    ChartHeaderAudienceFragment,
    ChartCheckboxesFragment, TableAdapterControlsAudienceFragment, TableAudienceComponent
} from "./fragments";
import {BaseElement} from "../../../../lib/base/element";
import {ButtonReportElement} from "./elements";


export class AudiencePage extends BasePage {
    datePickerFragment: DatePickerAudienceFragment;
    segmentationContainerFragment: SegmentationContainerFragment;
    chartHeaderFragment: ChartHeaderAudienceFragment;
    chartCheckboxesFragment: ChartCheckboxesFragment;
    chartBody: BaseElement;
    dimensionsControl: TableAdapterControlsAudienceFragment;
    table: TableAudienceComponent;
    showMoreButton: ButtonReportElement;

    constructor(page: Page) {
        super(page, "Apps", "/application/list");
        this.datePickerFragment = new DatePickerAudienceFragment(
            this.page.locator('.advanced-statistic__period'),
            this);
        this.segmentationContainerFragment = new SegmentationContainerFragment(
            this.page.locator('.advanced-statistic__segmentation-container'),
            this);
        this.chartHeaderFragment = new ChartHeaderAudienceFragment(
            this.page.locator('.statistic-visualizer__chart-header'),
            this);
        this.chartBody = new BaseElement(
            this.page.locator('.highcharts-container'),
            this);
        this.chartCheckboxesFragment = new ChartCheckboxesFragment(
            this.page.locator('.chart-legend__list'),
            this);
        this.dimensionsControl = new TableAdapterControlsAudienceFragment(
            this.page.locator(".statistic-table-adapter__group-switcher"),
            this
        );
        this.table = new TableAudienceComponent(
            this.page.locator(".statistic-table-adapter__table-wrapper"),
            this
        );
        this.showMoreButton = new ButtonReportElement(
            this.page.locator(".statistic-table-adapter__show-more button"),
            this,
            "Show more"
        );
    }
}

export function getAudiencePage(page: Page) {
    return new AudiencePage(page);
}
