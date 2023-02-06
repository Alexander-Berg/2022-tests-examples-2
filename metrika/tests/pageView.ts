import { encodeParams, TestParams } from "./utils/encoder";
import { Ctx } from "./utils/types";

declare function mock(apiName: string, ...a: any[]): undefined;
declare function runCode(ctx: Ctx): undefined;
declare function assertThat(a: any): any;
declare function assertApi(apiName: string): {
    wasCalled: () => void;
};
const counterID = 12123;
const mockData: Ctx = {
    event_name: "page_view",
    page_location: "https://ya.ru",
    page_referer: "",
    page_title: "title",
};
const params: TestParams = [
    ["tid", counterID],
    ["et", 0],
    ["uid", 0],
    ["dl", "https%3A%2F%2Fya.ru"],
    ["dt", mockData.page_title],
    ["t", "pageview"],
];
mockData["Counter ID"] = counterID;
mock("getEventData", (key: string) => {
    return mockData[key];
});
mock("getTimestampMillis", () => {
    return 0;
});
mock("getCookieValues", () => {
    return ["0"];
});
mock("sendHttpGet", (url: string, ok: (status: number) => void) => {
    assertThat(url).isEqualTo(encodeParams(params));
    return ok(200);
});
runCode(mockData);
assertApi("sendHttpGet").wasCalled();
assertApi("gtmOnSuccess").wasCalled();
