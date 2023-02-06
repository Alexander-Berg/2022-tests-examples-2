import { Locator } from "playwright-core";
import { BaseComponent } from ".";
import { BaseElement } from "./element";

export class Collection<C extends BaseElement | BaseComponent> {
    locator: Locator;
    elements: C[];
    parent: any;
    name: string | null;
    child: any;
    constructor(locator: Locator, parent: any, child: any, name: string) {
        this.locator = locator;
        this.parent = parent;
        this.child = child;
        this.name = name;
        this.elements = [];
    }

    async init() {
        await this.locator.first().waitFor({ state: "visible" });
        const count = await this.locator.count();
        for (let i = 0; i < count; i++) {
            const element = this.locator.nth(i);
            const name = (await element.allInnerTexts())[0].split('\n')[0];
            const tmp = new this.child(element, this.parent, name);
            this.elements.push(tmp);
        }
        return this;
    }

    async clear() {
        this.elements = [];
        return this;
    }

    get(index: number) {
        return this.elements[index];
    }

    getByName(name: string) {
        for (let i = 0; i < this.size(); i++) {
            if (this.get(i).name == name) {
                return this.get(i);
            }
        }
        throw `Element ${name} was not found.`;
    }

    async filterByAttribute(attribute: string, value: string) {
        const filteredElements: C[] = [];
        for (let i = 0; i < this.size(); i++) {
            const res = await this.get(i).locator.getAttribute(attribute);
            if(res === value){
                const element = this.get(i).locator;
                let name = this.get(i).name;
                if (name == null){name = res;}
                const tmp = new this.child(element, this.parent, name);
                filteredElements.push(tmp);
            }
        }
        if (filteredElements.length > 0){
            this.elements = filteredElements;
            return this;
        }
        throw `Elements with attribute: ${attribute}=${value} were not found.`;
    }

    size() {
        return this.elements.length;
    }
}
