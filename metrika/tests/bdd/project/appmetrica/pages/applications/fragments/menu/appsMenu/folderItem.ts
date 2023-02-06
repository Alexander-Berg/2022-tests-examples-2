import { Locator } from "playwright-core";
import {
    BaseComponent,
    ButtonElement, InputElement,
    TextElement,
} from "../../../../../../../lib";

export class FolderItemComponent extends BaseComponent {
    title: TextElement;
    editFolder: ButtonElement;
    saveFolder: ButtonElement;
    folderButton: ButtonElement;
    deleteFolder: ButtonElement;
    folderNameInput: InputElement;
    folderClearInput: ButtonElement;
    folderIconOpened: ButtonElement;

    constructor(locator: Locator, parent: any, name: string) {
        super(locator, parent, name);
        this.title = new TextElement(
            this.locator.locator(".menu-apps-folder__title"),
            this,
            name
        );
        this.folderButton = new ButtonElement(
            this.locator.locator(".menu-apps-folder__link"),
            this,
            name
        );
        this.editFolder = new ButtonElement(
            this.locator.locator(".menu-apps-folder__edit"),
            this,
            name
        );
        this.deleteFolder = new ButtonElement(
            this.locator.locator(".menu-apps-folder__editable-folder-delete"),
            this,
            name
        );
        this.saveFolder = new ButtonElement(
            this.locator.locator(".menu-apps-folder__editable-folder-save"),
            this,
            name
        );
        this.folderNameInput = new InputElement(
            this.locator.locator(".input__control"),
            this,
            "input folder name field"
        );
        this.folderClearInput = new ButtonElement(
            this.locator.locator(".input__clear_visibility_visible"),
            this,
            "Clear input field"
        );
        this.folderIconOpened = new ButtonElement(
            this.locator.locator(".icon__folder_open_yes"),
            this,
            "Icon of opened folder"
        );
    }
}
