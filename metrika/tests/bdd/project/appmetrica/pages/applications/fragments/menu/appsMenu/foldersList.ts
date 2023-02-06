import { Locator } from "playwright-core";
import { FolderItemComponent } from "./folderItem";
import {
    BaseComponent,
    Collection,
    ButtonElement,
} from "../../../../../../../lib";

export class FoldersFragment extends BaseComponent {
    folderButton: ButtonElement;
    foldersList: Collection<FolderItemComponent>;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Folders list in menu");

        this.folderButton = new ButtonElement(
            this.locator.locator(".menu-apps-folder"),
            this,
            "Folder button"
        );
        this.foldersList = new Collection(
            this.locator.locator(".menu-apps-folder"),
            this,
            FolderItemComponent,
            "Folders"
        );
    }

    async getFolderNames() {
        const folderNames = await this.locator
            .locator(".menu-apps-folder")
            .allInnerTexts();
        for (let i = 0; i < folderNames.length; i++) {
            folderNames[i] = folderNames[i].replace(/\n\W*/,'');
        }
        return folderNames;
    }

}
