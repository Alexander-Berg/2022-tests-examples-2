import { Browser } from "playwright";

export interface global {}

declare global {
    var browser: Browser;
    var baseAppmetricaUrl: string;
    var baseAppmerticaAPIUrl: string;
    var waitTimeout: number;
    var clickTimeout: number;
}
