import got from "got";
import { users } from "../project/common/data/users";

const VAULT_TOKEN = process.env.VAULT_TOKEN ? process.env.VAULT_TOKEN : "";
const SECRET = "sec-01fyzze5zfvjz1mfq5pz8nr3at";

export async function getToken(login: keyof typeof users) {
    const key = users[login];
    const response = await got.get(
        `https://vault-api.passport.yandex.net/1/versions/${SECRET}`,
        {
            headers: {
                "Content-Type": "application/json",
                Authorization: `OAuth ${VAULT_TOKEN}`,
            },
        }
    );
    const data = JSON.parse(response.body)["version"]["value"];
    for (let i = 0; i < data.length; i++) {
        if (data[i].key == key) {
            return data[i].value;
        } else {
            throw "Unrecognized user";
        }
    }
}
