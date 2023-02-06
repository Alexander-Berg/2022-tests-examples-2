declare module 'yandex-cfg' {
    
    import { GotOptions } from 'got';

    interface Config {
        version: string;
        bishop: {
            server: string;
            program: string;
            environment: string;
            mergePriority: 'local' | 'remote';
            clientOptions: Partial<GotOptions<string>>;
        };

        yav: {
            server: string;
            clientOptions: Partial<GotOptions<string>>;
            secrets: Array<{
                secret: string;
                version: string;
                from: string;
                to: string;
            }>;
        };
    }

    type RecursivePartial<T> = { [P in keyof T]?: RecursivePartial<T[P]> };

    export type AppConfig = RecursivePartial<Config>;

    const config: Config;
    export default config;
}
