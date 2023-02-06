import {Then, When} from "@cucumber/cucumber";
import {assert, expect} from "chai";

import { OurWorld } from "../../../types";
import {defaultDimensions, defaultMetrics} from "../data/scenarioKeysets/reportDefaultDimensionsAndMetrics";

When("I add dimensions {string}", async function (this: OurWorld, dimensions: string){
    const dimensionsArr = dimensions.split("; ");
    const page = await this.appmetrica.commonReportPage;
    await page.addGroupings({groupings:dimensionsArr});
    await page.waitForReport();
    }
);

When("I delete dimensions {string}", async function (this: OurWorld, dimensions: string){
    const dimensionsArr = dimensions.split("; ");
    const page = await this.appmetrica.commonReportPage;
    await page.tableControls.addGropingsAndMetricsButton.click();
    const pickedDimensions = await page.metricPickerPopup.groupingsList.init();
    for (let i = 0; i < dimensionsArr.length; i++) {
        const curr = await pickedDimensions.get(i).getText();
        if (curr === dimensionsArr[i]){
            await pickedDimensions.get(i).locator.hover();
            await pickedDimensions.get(i).deleteItem.click();
        }
    }
    await page.metricPickerPopup.applyChanges.clickAndWait(page);
    }
);

When("I click on the dimension cell repeatedly to the last dimension cell in the list",
    async  function (this: OurWorld){
        const page = await this.appmetrica.commonReportPage;
        const selectedDimensionsTitle = await page.tableControls.currentGroupingsTitle.getText();
        const selectedDimensionsArr = selectedDimensionsTitle?.split(", ");
        if (selectedDimensionsArr !== undefined){
            for (let i = 0; i < selectedDimensionsArr.length-1; i++) {
                const rowsList = await page.table.tableBody.rowsList.init();
                await rowsList.get(0).dimensionCellFragment.dimensionCellListView.click();
            }
        }
    }
);

When("I click to the last link in the breadcrumbs",
    async  function (this: OurWorld){
        const page = await this.appmetrica.commonReportPage;
        await page.table.tableHead.breadcrumbs.clear();
        const breadcrumbs = await page.table.tableHead.breadcrumbs.init();
        await breadcrumbs.get(breadcrumbs.size()-1).clickAndWait(page);
    }
);

When("I click to the drilldown table view button",
    async  function (this: OurWorld){
        const page = await this.appmetrica.commonReportPage;
        await page.tableControls.drilldownButton.click();
    }
);

When("I click on expand button at the {int} dimension cell for each level to last level of the table",
    async  function (this: OurWorld, parentNumber: number){
        const page = await this.appmetrica.commonReportPage;
        await page.table.tableBody.rowsList.clear();
        for (let i = 0; i < 9; i++) {
            const rowsList = await page.table.tableBody.rowsList.init();
            try{
                const expandButton =
                    rowsList.get(parentNumber+i-1).dimensionCellFragment.drilldownPlus;
                if (await expandButton.isVisible()) {
                    await expandButton.clickAndWait(page);
                } else {break;}
            } catch (Err){throw new Error("Row with index "+ (parentNumber+i) +" doesn't exist");}
            await page.table.tableBody.rowsList.clear();
        }
    }
);

When("I click on reduce button at the {int} dimension cell for each level from last to parent level of the table",
    async  function (this: OurWorld, parentNumber: number){
        const page = await this.appmetrica.commonReportPage;
        const levelsCount = (await page.tableControls.currentGroupingsTitle.getText())?.split(", ").length;
        if (levelsCount !== undefined){
            await page.table.tableBody.rowsList.clear();
            for (let i = 1; i < levelsCount; i++) {
                const rowsList = await page.table.tableBody.rowsList.init();
                try{
                    const reduceButton =
                        rowsList.get(levelsCount-1+parentNumber-1-i).dimensionCellFragment.drilldownPlus;
                    await reduceButton.clickAndWait(page);
                } catch (Err){throw new Error("Row with index "+ (levelsCount-1+parentNumber-i) +" doesn't exist");}
                await page.table.tableBody.rowsList.clear();
            }
        }
    }
);

When("I add metric {string} with the event {string}", async function (this: OurWorld, metric: string, event: string){
        const page = await this.appmetrica.commonReportPage;
        await page.addMetrics([{metric:metric, event: event}]);
    }
);

Then("I see the {string} metric as a table column",
    async function (this: OurWorld, expectedMetric: string) {
        const page = await this.appmetrica.commonReportPage;
        const actualMetrics = await page.table.tableHead.getColumnMetricNames();
        expect(actualMetrics).to.contain(expectedMetric,"Metric exist as a table column");
        await page.waitForReport();
    }
);

Then("I see {int} rows of data in the table",
    async function (this: OurWorld, expectedCount: number) {
        const page = await this.appmetrica.commonReportPage;
        await page.table.tableBody.rowsList.clear();
        const rowsList = await page.table.tableBody.rowsList.init();
        assert.equal(rowsList.size(), expectedCount, "Expected count of rows reached");
    }
);

Then("I see {int} rows of data in the last level of the table",
    async function (this: OurWorld, expectedCount: number) {
        const page = await this.appmetrica.commonReportPage;
        await page.table.tableBody.rowsList.clear();
        const rowsList = await page.table.tableBody.rowsList.init();
        let actualCount = 0;
        for (let i = 0; i < rowsList.size(); i++) {
            if(!await page.table.tableBody.rowsList.get(i)
                .dimensionCellFragment.drilldownPlus.isVisible()){
                actualCount++;
            }
        }
        assert.equal(actualCount, expectedCount, "Expected count of rows reached");
        await page.waitForReport();
    }
);

Then("I see metrics {string} picked for report in this order",
    async function (this: OurWorld, metrics: string) {
        if(defaultMetrics[metrics] !== undefined){metrics = defaultMetrics[metrics];}
        const expectedMetrics = metrics.split("; ");
        const page = await this.appmetrica.commonReportPage;
        const actualMetrics = await page.table.tableHead.getColumnMetricNames();
        expect(actualMetrics).to.eql(expectedMetrics,"Metrics are equal");
        await page.waitForReport();
    }
);

Then("I see {int} dimensions in the picked dimensions list",
    async function (this: OurWorld, expectedDimensionsSize: number) {
        const page = await this.appmetrica.commonReportPage;
        await page.tableControls.addGropingsAndMetricsButton.click();
        await page.metricPickerPopup.groupingsList.clear();
        const actualDimensionsSize = (await page.metricPickerPopup.groupingsList.init()).size();
        expect(actualDimensionsSize).to
            .equal(expectedDimensionsSize,"Size of the picked dimensions are equal");
        await page.metricPickerPopupCloseButton.click();
    }
);

Then("I see dimensions {string} picked for report in this order",
    async function (this: OurWorld, expectedDimensions: string) {
        if(defaultDimensions[expectedDimensions] !== undefined){
            expectedDimensions = defaultDimensions[expectedDimensions];
        }
        const page = await this.appmetrica.commonReportPage;
        expectedDimensions = expectedDimensions.replace(/[;]/g,",");
        const actualDimensions = await page.tableControls.currentGroupingsTitle.getText();
        expect(actualDimensions).to.equal(expectedDimensions,"Dimensions are equal");
    }
);

Then("I can not add eleventh dimension to report", async function (this: OurWorld){
    const page = await this.appmetrica.commonReportPage;
    await page.tableControls.addGropingsAndMetricsButton.click();
    const selectedDimensions = await page.metricPickerPopup.groupingsList.init();
    if (selectedDimensions.size() != 10){throw new Error("There are not 10 picked dimensions");}
    await page.metricPickerPopup.groupingsAddButton.click();
    const disabledDimension = await page.addGroupingsPopup.locator
        .locator(".sc-jKJlTe.jOHEWl div .sc-ckVGcZ.fwkQzp").nth(3).isVisible();
    assert.equal(disabledDimension, true, "Can not add more dimensions, fields are disabled");
    await page.metricPickerPopupCloseButton.click();
    }
);

Then("I see {int} previously clicked dimension cells in the breadcrumbs",
    async function (this: OurWorld, count: number) {
        const page = await this.appmetrica.commonReportPage;
        const breadcrumbs = await page.table.tableHead.breadcrumbs.init();
        assert.equal(breadcrumbs.size(), count,
            "Count of breadcrumbs are equal to count of previously clicked dimensions");
    }
);

Then("I see a dimension cell with name {string}",
    async function (this: OurWorld, expectedName: string) {
        const page = await this.appmetrica.commonReportPage;
        const cellNames = [];
        await page.table.tableBody.rowsList.clear();
        const rowsArr = await page.table.tableBody.rowsList.init();
        for (let i = 0; i < rowsArr.size(); i++) {
            cellNames.push(await rowsArr.get(i).dimensionCellFragment.dimensionCellListView.getText());
        }
        expect(cellNames).to.contain(expectedName, "Dimension cell with the given name is visible");
    }
);
