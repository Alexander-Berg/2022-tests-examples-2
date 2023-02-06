
import { Locator } from "playwright-core";
import {BaseComponent, ButtonElement, Collection} from "../../../../../../../lib";
import {ButtonReportElement} from "../../../elements";
import {DraggableItemFragment} from "./draggableItem";

export class MetricPickerPopupFragment extends BaseComponent {
    groupingsList: Collection<DraggableItemFragment>;
    metricsList: Collection<DraggableItemFragment>;
    groupingsAddButton: ButtonElement;
    metricsAddButton: ButtonElement;
    applyChanges: ButtonReportElement;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Metrics and gropings picker");

        this.groupingsList = new Collection(
            this.locator.locator(".izCiVT .sc-daURTG.ianbjX"),
            this,
            DraggableItemFragment,
            "List of selected groupings"
        );
        this.metricsList = new Collection(
            this.locator.locator(".fNWslT .sc-daURTG.ianbjX"),
            this,
            DraggableItemFragment,
            "List of selected metrics"
        );
        this.groupingsAddButton = new ButtonElement(
            this.locator.locator(".cnjYzN .sc-eVrGFk.ePXgNh"),
            this,
            "Add groupings button"
        );
        this.metricsAddButton = new ButtonElement(
            this.locator.locator(".bqMhQJ .sc-eVrGFk.ePXgNh"),
            this,
            "Add metrics button"
        );
        this.applyChanges = new ButtonReportElement(
            this.locator.locator(".sc-cCbPEh.fGQIRP button"),
            this,
            "Apply changes button"
        );
    }
}
