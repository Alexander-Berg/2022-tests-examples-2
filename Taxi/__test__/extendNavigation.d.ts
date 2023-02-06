export interface INavMenuItem {
    url: string;
    title: string;
}

export declare function extendNavigation(id: string, navMenuItem: INavMenuItem | INavMenuItem[]): void;
