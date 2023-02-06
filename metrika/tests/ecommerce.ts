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
    event_name: "purchase",
    page_location: "https://yaho.com",
    page_referer: "",
    page_title: "title",
    items: [
        {
            item_id: counterID,
            item_name: "name",
            item_brand: "brand",
            price: 2,
            coupon: "XXX",
            quantity: 1,
        },
        {
            item_id: counterID,
            item_name: "nameTwo",
            item_brand: "brandTwo",
            price: 1,
            coupon: "XXxX",
            quantity: 2,
        },
    ],
    transaction_id: "112XXlLLa",
    value: 4,
    coupon: "AAFF",
};
mockData["Counter ID"] = 12123;

const params: TestParams = [
    ["tid", counterID],
    ["et", 0],
    ["uid", 0],
    ["dl", "https%3A%2F%2Fyaho.com"],
    ["dt", mockData.page_title],
    ["t", "event"],
    ["pa", "purchase"],
    ["pr1id", mockData.items[0].item_id],
    ["pr1nm", mockData.items[0].item_name],
    ["pr1br", mockData.items[0].item_brand],
    ["pr1pr", mockData.items[0].price],
    ["pr1qt", mockData.items[0].quantity],
    ["pr1cc", mockData.items[0].coupon],
    ["pr2id", mockData.items[1].item_id],
    ["pr2nm", mockData.items[1].item_name],
    ["pr2br", mockData.items[1].item_brand],
    ["pr2pr", mockData.items[1].price],
    ["pr2qt", mockData.items[1].quantity],
    ["pr2cc", mockData.items[1].coupon],
    ["ti", mockData.transaction_id],
    ["tr", mockData.value],
    ["tcc", mockData.coupon],
];
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
