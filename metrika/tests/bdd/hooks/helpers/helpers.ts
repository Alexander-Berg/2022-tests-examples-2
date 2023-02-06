import { ITestCaseHookParameter } from "@cucumber/cucumber";
import { getToken } from "../../lib/yav";
import { users } from "../../project/common/data/users";

export function getStepParameters(scenario: ITestCaseHookParameter): string {
    const text = scenario.gherkinDocument.comments[0].text;
    return text.slice(text.indexOf("{"));
}

export async function getOAuthToken(
    scenario: ITestCaseHookParameter
): Promise<string> {
    const step = scenario.pickle.steps[0];
    if (step.text.includes("Authorize")) {
        const login = step.text.slice(
            step.text.indexOf("'") + 1,
            step.text.length - 1
        );
        return await getToken(login as keyof typeof users);
    } else {
        throw "Unrecognized user";
    }
}

export async function getDefaultHeaders(oauthToken?: string): Promise<any> {
    if (oauthToken) {
        return {
            "Content-Type": "application/json",
            "Authorization": `OAuth ${oauthToken}`,
        };
    } else {
        return {
            "Content-Type": "application/json",
        };
    }
}
