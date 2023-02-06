import { Locator } from "playwright-core";
import {
    BaseComponent,
    ButtonElement, Collection
} from "../../../../../lib";

export class DropDownFragment extends BaseComponent {
    dropDownSelector: Collection<ButtonElement>;
    constructor(locator: Locator, parent: any, name: string) {
        super(locator, parent, name);

        this.dropDownSelector = new Collection(
            this.locator.locator("[role='option']"),
            this,
            ButtonElement,
            "drop-down list"
        );
    }
}
