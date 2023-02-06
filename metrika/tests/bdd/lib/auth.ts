import {
    CommonParams,
    GetAccountParams,
    TUSClient,
} from "@yandex-int/tus-client";
import { Page } from "playwright-core";

const PASSPORT_URL = "https://passport.yandex.ru";
const TUS_TOKEN = process.env.TUS_TOKEN ? process.env.TUS_TOKEN : "";

const TUS_PARAMS: CommonParams = {
    tus_consumer: "metrika-ui",
    env: "prod",
};

export async function authorize(page: Page, login: string) {
    const password = await getPassword(login);
    const authUrl = `${PASSPORT_URL}/auth?mode=password&retpath=${encodeURIComponent(
        PASSPORT_URL
    )}`;

    const timestamp = Math.round(new Date().getTime() / 1000);
    const html = `
        <html>
            <form method="POST" id="authForm" action="${authUrl}">
                <input name="login" value="${login}">
                <input type="password" name="passwd" value="${password}">
                <input type="checkbox" name="twoweeks" value="no">
                <input type="hidden" name="timestamp" value="${timestamp}">
                <button type="submit">Login</button>
            </form>
        <html>
    `;
    await page.setContent(html);
    await page.waitForSelector("#authForm");
    await page.click("button");
    await page.waitForFunction(
        `window.location.href === "${PASSPORT_URL}/profile";`
    );
}

async function getPassword(login: string) {
    const tusClient = new TUSClient(TUS_TOKEN, TUS_PARAMS);
    const tusLoginParam: GetAccountParams = {
        login: login,
    };
    return (await tusClient.getAccount(tusLoginParam)).account.password;
}
