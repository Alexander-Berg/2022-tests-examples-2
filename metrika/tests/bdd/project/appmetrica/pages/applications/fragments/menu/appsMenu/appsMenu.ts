import { Locator } from "playwright-core";
import {
    BaseComponent,
    ButtonElement,
    InputElement,
} from "../../../../../../../lib";
import { AppsListFragment } from "./appsList";
import { FoldersFragment } from "./foldersList";

export class AppsMenuFragment extends BaseComponent {
    searchField: InputElement;
    addAppButton: ButtonElement;
    appsList: AppsListFragment;
    appsListInFolders: AppsListFragment;
    addFolderButton: ButtonElement;
    foldersFragment: FoldersFragment;

    constructor(locator: Locator, parent: any) {
        super(locator, parent, "Apps menu");

        this.addAppButton = new ButtonElement(
            this.locator.locator(".menu-apps__add"),
            this,
            "Add new app button"
        );
        this.searchField = new InputElement(
            this.locator.locator('[placeholder="Найти приложение"]'),
            this,
            "Search field"
        );
        this.appsList = new AppsListFragment(
            this.locator.locator(".menu-apps__apps-list"),
            this
        );
        this.appsListInFolders = new AppsListFragment(
            this.locator.locator(".menu-apps__folders-list"),
            this
        );
        this.addFolderButton = new ButtonElement(
            this.locator.locator(".menu-apps__add-folder"),
            this,
            "add new folder"
        );
        this.foldersFragment = new FoldersFragment(
            this.locator.locator(".menu-apps__folders-list"),
            this
        );
    }
}
