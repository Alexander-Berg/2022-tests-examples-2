import {
    Before,
    BeforeAll,
    AfterAll,
    After,
    setDefaultTimeout,
    AfterStep,
    Status,
    ITestStepHookParameter,
} from "@cucumber/cucumber";
import { chromium } from "playwright";
import { OurWorld } from "./types";
import { Appmetrica } from "./project/appmetrica/pages";

const HEADLESS: boolean = process.env.HEADLESS
    ? Boolean(process.env.HEADLESS)
    : true;
const TIMEOUT: number = process.env.TIMEOUT
    ? Number(process.env.HEADLESS)
    : 30000;
const LOG_ALL: boolean = process.env.LOG_ALL
    ? Boolean(process.env.LOG_ALL)
    : false;
const BASE_APPMETRICA_URL: string = process.env.BASE_APPMETRICA_URL
    ? process.env.BASE_APPMETRICA_URL
    : "https://test.appmetrica.yandex.ru";
const BASE_APPMETRICA_API_URL: string = process.env.BASE_APPMETRICA_API_URL
    ? process.env.BASE_APPMETRICA_API_URL
    : "http://test.api.appmetrica.metrika.yandex.net";
const WAIT_TIMEOUT: number = process.env.WAIT_TIMEOUT ? Number(process.env.WAIT_TIMEOUT) : 5000;
const CLICK_TIMEOUT: number = process.env.CLICK_TIMEOUT ? Number(process.env.CLICK_TIMEOUT) : 2000;

setDefaultTimeout(TIMEOUT);

BeforeAll(async function () {
    global.browser = await chromium.launch({
        headless: HEADLESS,
        slowMo: 150,
    });
    global.baseAppmetricaUrl = BASE_APPMETRICA_URL;
    global.baseAppmerticaAPIUrl = BASE_APPMETRICA_API_URL;
    global.waitTimeout = WAIT_TIMEOUT;
    global.clickTimeout = CLICK_TIMEOUT;
});

AfterAll(async function () {
    await global.browser.close();
});

Before(async function (this: OurWorld) {
    this.context = await global.browser.newContext({ignoreHTTPSErrors: true});
    this.page = await this.context.newPage();
    this.appmetrica = new Appmetrica(this.page);
});

After(async function (this: OurWorld) {
    await this.page.close();
    await this.context.close();
});

AfterStep(async function (this: OurWorld, testCase: ITestStepHookParameter) {
    if (LOG_ALL) {
        await attachLogs(this);
    } else if (testCase.result.status === Status.FAILED) {
        await attachLogs(this);
    }
});

async function attachLogs(world: OurWorld) {
    await world.page.screenshot().then((buffer) => {
        return world.attach(buffer, "image/png");
    });
    await world.attach(world.page.url());
    await world.attach(
        JSON.stringify(await world.context.storageState(), null, "\t")
    );
}
