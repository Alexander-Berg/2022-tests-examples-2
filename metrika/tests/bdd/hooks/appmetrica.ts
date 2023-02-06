import { After, Before } from "@cucumber/cucumber";
import got from "got";
import { getDefaultHeaders, getOAuthToken, getStepParameters } from "./helpers";
import { newApplicationTemplate } from "../project/appmetrica/data/apiTemplates";

let appId: number;
let oauth: string;

Before({ tags: "@createApp" }, async function (scenario) {
    oauth = await getOAuthToken(scenario);
    const params = getStepParameters(scenario);
    const app = newApplicationTemplate(JSON.parse(params)["appName"]);

    const response = await got.post(
        `${global.baseAppmerticaAPIUrl}/management/v1/applications`,
        {
            headers: await getDefaultHeaders(oauth),
            body: JSON.stringify(app),
        }
    );
    appId = Number(
        JSON.stringify(JSON.parse(response.body)["application"]["id"])
    );
});

After({ tags: "@createApp" }, async function () {
    await got.delete(
        `${global.baseAppmerticaAPIUrl}/management/v1/application/${appId}`,
        {
            headers: await getDefaultHeaders(oauth),
        }
    );
});
