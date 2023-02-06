export abstract class PageAbstract {
    public abstract open(path: string): ReturnType<typeof browser['url']>;
    public abstract selector(...args: Parameters<typeof $>): ReturnType<typeof $>;
}
