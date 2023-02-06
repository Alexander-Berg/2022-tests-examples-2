import { Locator } from "playwright-core";
import {
    BaseComponent
} from "../../../../../lib";
import {FirstFormComponent, SecondFormComponent, ThirdFormComponent} from ".";

export class AddNewAppFragment extends BaseComponent {

    firstForm: FirstFormComponent;
    secondForm: SecondFormComponent;
    thirdForm: ThirdFormComponent;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Forms list");

        this.firstForm = new FirstFormComponent(
            this.locator.locator("form").first(),
            this,
            "first form"
        );

        this.secondForm = new SecondFormComponent(
            this.locator.locator("form").last(),
            this,
            "second form"
        );

        this.thirdForm = new ThirdFormComponent(
            this.locator.locator(".sc-itybZL.chknVF"),
            this,
            "third form"
        );
    }
}
