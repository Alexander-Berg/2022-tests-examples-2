import {BasePage, ButtonElement, Collection} from "../../../../lib";
import {Page} from "playwright-core";
import {
    DatePickerFragment,
    ChartHeaderFragment,
    ChartCheckboxesFragment,
    TableControlsFragment,
    TableComponent,
    AddGropingsPopupFragment,
    AddMetricsPopupFragment,
    MetricByDurationPopupFragment, PeriodsListPopupFragment,
    MetricPickerPopupFragment, MetricWithEventsPopupFragment
} from "./fragments";
import {BaseElement} from "../../../../lib/base/element";
import {ButtonReportElement} from "./elements";
import {MetricBySessionsPopupFragment} from "./fragments/common/popups/metricBySessionsPopup";

// Base report page - predecessor for UA, Remarketing, Revenue, Ecommerce, Engagement, Events
export class CommonPage extends BasePage {
    datePickerFragment: DatePickerFragment;
    chartHeaderFragment: ChartHeaderFragment;
    chartCheckboxesFragment: ChartCheckboxesFragment;
    chartBody: BaseElement;
    tableControls: TableControlsFragment;
    table: TableComponent;
    showMoreButtonList: Collection<ButtonReportElement>;
    metricPickerPopup: MetricPickerPopupFragment;
    metricPickerPopupCloseButton: ButtonElement;
    addGroupingsPopup: AddGropingsPopupFragment;
    addMetricsPopup: AddMetricsPopupFragment | undefined;
    metricByDurationPopup: MetricByDurationPopupFragment | undefined;
    metricPeriodsListPopup: PeriodsListPopupFragment | undefined;
    metricBySessionsPopup: MetricBySessionsPopupFragment | undefined;
    metricWithEventsPopup: MetricWithEventsPopupFragment | undefined;
    private _addMetricsPopupLocator = '.sc-iNovjJ.ghqNQB';
    private _metricByDurationPopupLocator = '.sc-cIbcTr.fOIabi';
    private _metricPeriodsListPopupLocator = '.popup2_direction_bottom-left.popup2_target_anchor.select2__popup';
    private _metricBySessionsPopupLocator = '.popup2_direction_right-center.popup2_target_anchor';
    private _metricWithEventsPopupLocator = '.sc-hgeeVt.jXdbLN';

    constructor(page: Page) {
        super(page, "Apps", "/application/list");
        this.datePickerFragment = new DatePickerFragment(
            this.page.locator('.sc-fKGOjr.iMuUbL'),
            this);
        this.chartHeaderFragment = new ChartHeaderFragment(
            this.page.locator('.sc-hycgNl.kjSLzI'),
            this);
        this.chartBody = new BaseElement(
            this.page.locator('.highcharts-container'),
            this);
        this.chartCheckboxesFragment = new ChartCheckboxesFragment(
            this.page.locator('.sc-hTQSVH.hcwkSy'),
            this);
        this.tableControls = new TableControlsFragment(
            this.page.locator('.sc-gleUXh.cdwlJP'),
            this);
        this.table = new TableComponent(
            this.page.locator(".sc-fHSTwm.zlOcr"),
            this
        );
        this.showMoreButtonList = new Collection(
            this.page.locator(".sc-jWBwVP.fzXqiW .button2"),
            this,
            ButtonReportElement,
            "Show more buttons list"
        );
        this.metricPickerPopup = new MetricPickerPopupFragment(
            this.page.locator(".sc-eomEcv.eFfHTW"),
            this
        );
        this.metricPickerPopupCloseButton = new ButtonElement(
            this.page.locator("div.sc-gqjmRU.kJJXJp > button").last(),
            this,
            "Metric picker popup close button"
        );
        this.addGroupingsPopup = new AddGropingsPopupFragment(
            this.page.locator(".sc-iNovjJ.ghqNQB").first(),
            this
        );
    }

    async addGroupings(object: Record<string, string[]>) {
        await this.tableControls.addGropingsAndMetricsButton.click();
        await this.metricPickerPopup.groupingsAddButton.click();
        await this.addGroupingsPopup.openAllGroups();
        const list = await this.addGroupingsPopup.groupingsList.init();
        await this.metricPickerPopup.groupingsAddButton.click();
        const map = new Map(Object.entries(object));
        if (Object.prototype.hasOwnProperty.call(object,"groupings")) {
            const groupings = CommonPage.getValueFromObject("groupings", map);
            for (const grouping of groupings) {
                await this.metricPickerPopup.groupingsAddButton.click();
                await list.getByName(grouping).click();
            }
        }
        await this.metricPickerPopup.applyChanges.click();
    }

    async addMetrics(object: Record<string, string>[]){
        this.addMetricsPopup = new AddMetricsPopupFragment(
            this.page.locator(this._addMetricsPopupLocator).last(),
            this
        );
        await this.tableControls.addGropingsAndMetricsButton.click();
        await this.metricPickerPopup.metricsAddButton.click();
        await this.addMetricsPopup.openAllGroups();
        const list = await this.addMetricsPopup.metricsList.init();
        await this.metricPickerPopup.metricsAddButton.click();
        for (const obj of object) {
            await this.metricPickerPopup.metricsAddButton.click();
            const map = new Map(Object.entries(obj));
            if(Object.prototype.hasOwnProperty.call(obj,"metric")){
                const metric = CommonPage.getValueFromObject("metric", map);
                await list.getByName(metric).clickAndWait(this);
            }
            if(Object.prototype.hasOwnProperty.call(obj,"event")){
                const event = CommonPage.getValueFromObject("event", map);
                this.metricWithEventsPopup = new MetricWithEventsPopupFragment(
                    this.page.locator(this._metricWithEventsPopupLocator),
                    this
                );
                await this.metricWithEventsPopup.searchField.fill(event);
                await this.metricWithEventsPopup.delay(500);
                const eventsList = await this.metricWithEventsPopup.eventsList.init();
                await eventsList.getByName(event).waitForVisible();
                await eventsList.getByName(event).click();
                await this.metricWithEventsPopup.applyChangesButton.click();
                continue;
            }
            if(Object.prototype.hasOwnProperty.call(obj,"period")
                && Object.prototype.hasOwnProperty.call(obj,"duration")){
                const period = CommonPage.getValueFromObject("period", map);
                const duration = CommonPage.getValueFromObject("duration", map);
                this.metricByDurationPopup = new MetricByDurationPopupFragment(
                    this.page.locator(this._metricByDurationPopupLocator),
                    this
                );
                await this.metricByDurationPopup.durationInput.fill(duration);
                await this.metricByDurationPopup.periodButton.click();
                this.metricPeriodsListPopup = new PeriodsListPopupFragment(
                    this.page
                        .locator(this._metricPeriodsListPopupLocator),
                    this
                );
                const periods = await this.metricPeriodsListPopup.periodsList.init();
                await periods.getByName(period).click();
                await this.metricByDurationPopup.applyChangesButton.click();
                continue;
            }
            if(Object.prototype.hasOwnProperty.call(obj,"number_of_sessions")){
                const number = CommonPage.getValueFromObject("number_of_sessions", map);
                this.metricBySessionsPopup = new MetricBySessionsPopupFragment(
                    this.page
                        .locator(this._metricBySessionsPopupLocator),
                    this
                );
                await this.metricBySessionsPopup.numberOfSessions.fill(number);
                await this.metricBySessionsPopup.applyChangesButton.click();
            }
        }
        await this.metricPickerPopup.applyChanges.click();
    }

    private static getValueFromObject(key: string, map: Map<string, any>){
            const value = map.get(key);
            if (typeof value !== "undefined"){
                return value;
            }
            else { throw new Error("Invalid object properties");}
    }
}

export function getCommonPage(page: Page) {
    return new CommonPage(page);
}

