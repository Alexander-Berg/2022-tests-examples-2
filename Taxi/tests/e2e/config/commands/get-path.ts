export async function getPath(this: WebdriverIO.Browser) {
    const url = new URL(await this.getUrl());
    return url.pathname;
}

export type GetPath = typeof getPath;
