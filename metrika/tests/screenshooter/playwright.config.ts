import { devices, PlaywrightTestConfig } from "@playwright/test";

const BASE_URL = process.env.BASE_URL ? process.env.BASE_URL : "";
const HEADLESS: boolean = process.env.HEADLESS
    ? Boolean(process.env.HEADLESS)
    : true;
const config: PlaywrightTestConfig = {
    timeout: 60000,
    use: {
        launchOptions: {
            slowMo: 500,
            headless: HEADLESS
        },
        baseURL: BASE_URL,
    },
    projects: [
        {
            name: "auth",
            use: { ...devices["Desktop Chrome"] },
            testMatch: /auth.spec.ts/,
            retries: 3,
        },
        {
            name: "appmetrica-desktop",
            use: { ...devices["Desktop Chrome"] },
            testMatch: /.*appmetrica.desktop.spec.ts/,
            retries: 3,
        },
        {
            name: "appmetrica-desktop-ff",
            use: { ...devices["Desktop Firefox"] },
            testMatch: /.*appmetrica.desktop.spec.ts/,
            retries: 3,
        },
        {
            name: "metrika-desktop",
            use: { ...devices["Desktop Chrome"] },
            testMatch: /.*metrika.desktop.spec.ts/,
            retries: 3,
        },
        {
            name: "metrika-desktop-ff",
            use: { ...devices["Desktop Firefox"] },
            testMatch: /.*metrika.desktop.spec.ts/,
            retries: 3,
        },
        {
            name: "metrika-mobile-chromium",
            use: {
                browserName: "chromium",
                ...devices["Pixel 4"],
            },
            testMatch: /.*metrika.mobile.spec.ts/,
            retries: 3,
        },
        {
            name: "metrika-mobile-ios",
            use: {
                browserName: "webkit",
                ...devices["iPhone 13 Pro Max"],
            },
            testMatch: /.*metrika.mobile.spec.ts/,
            retries: 3,
        },
        {
            name: "radar-desktop",
            use: { ...devices["Desktop Chrome"] },
            testMatch: /.*radar.desktop.spec.ts/,
            retries: 3,
        },
        {
            name: "radar-desktop-ff",
            use: { ...devices["Desktop Firefox"] },
            testMatch: /.*radar.desktop.spec.ts/,
            retries: 3,
        },
        {
            name: "radar-mobile",
            use: {
                browserName: "chromium",
                ...devices["Pixel 4"],
            },
            testMatch: /.*radar.mobile.spec.ts/,
            retries: 3,
        },
        {
            name: "radar-mobile-ios",
            use: {
                browserName: "webkit",
                ...devices["iPhone 13 Pro Max"],
            },
            testMatch: /.*radar.mobile.spec.ts/,
            retries: 3,
        },
    ],
    reporter: [["allure-playwright"], ["line"]],
};
export default config;
