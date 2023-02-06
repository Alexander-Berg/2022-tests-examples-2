
import { Locator } from "playwright-core";
import {BaseComponent, ButtonElement} from "../../../../../../../lib";

export class DraggableItemFragment extends BaseComponent {
    item: ButtonElement;
    deleteItem: ButtonElement;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Groupings selector");
        this.item = new ButtonElement(
            this.locator.locator(".sc-htoDjs.cdParH"),
            this,
            "Item"
        );
        this.deleteItem = new ButtonElement(
            this.locator.locator(".sc-gZMcBi.iGVxvt"),
            this,
            "Delete item button"
        );
    }
}

