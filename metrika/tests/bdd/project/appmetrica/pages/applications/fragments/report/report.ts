
import { Locator } from "playwright-core";
import { BaseComponent, TextElement } from "../../../../../../lib";
import { TutorialFragment } from ".";

export class ReportFragment extends BaseComponent {
    reportTitle: TextElement;
    tutorial: TutorialFragment;
    emptyFolderReport: BaseComponent;


    constructor(locator: Locator, parent: any) {
        super(locator, parent, 'Apps menu');

        this.reportTitle = new TextElement(this.locator.locator('.page-app-statistic__title'),
                                           this,
                                           'Report title');
        this.tutorial = new TutorialFragment(this.locator.locator('.page-app-statistic__report-content'), this);

        this.emptyFolderReport = new BaseComponent(this.locator.locator('.page-app-list__empty-folder'), this, "Empty Folder report");
    }
}
