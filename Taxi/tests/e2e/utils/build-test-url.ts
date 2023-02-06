export function buildTestUrl(path: string) {
    return new URL(path, `http://${process.env.TEST_HOST}`).href;
}
