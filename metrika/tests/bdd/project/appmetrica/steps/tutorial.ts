import { Then, When } from "@cucumber/cucumber";
import { assert } from "chai";
import { OurWorld } from "../../../types";
import { ButtonElement } from "../../../lib";

When("I click {string} to the last slide", async function (this: OurWorld, selector: string) {
        const elements = await (
            await this.appmetrica.applicationsPage.reportFragment.tutorial.getElementsByText(
                selector,
                ButtonElement
            )
        ).init();
        for (let i = 0; i < elements.size(); i++) {
            const element = elements.get(i) as ButtonElement;
            await element.waitForVisible();
            await element.click();
        }
    }
);

Then("I see {int} steps tutorial", async function (this: OurWorld, expectedSteps: number) {
    const actualSteps = (
        await this.appmetrica.applicationsPage.reportFragment.tutorial.stepsLstReact.init()
    ).size();
    assert.equal(actualSteps, expectedSteps, "actual and expected steps are equal");
}
);

Then("I can close the tutorial by clicking at {string}", async function (this: OurWorld, selector: string) {
        const element =
            await this.appmetrica.applicationsPage.reportFragment.tutorial.getElementByText(
                selector
            );
        await element.waitForVisible();
        await element.click();
        const isVisible = await element.isVisible();
        assert.equal(isVisible, false, "element was disabled");
    }
);
