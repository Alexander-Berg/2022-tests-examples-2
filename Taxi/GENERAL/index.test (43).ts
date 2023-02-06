import {
    ConfigProvider,
    createEnvironmentGetter,
    Environment,
    MissedEnvironmentError,
    MissedLastSetEnvironmentError,
    TakeEnvironmentValueError
} from '.';

describe('config package', () => {
    it('should test "createEnvironmentGetter"', () => {
        let getEnv = createEnvironmentGetter('APP_ENV', 'NODE_ENV');
        expect(getEnv()).toEqual('test');

        getEnv = createEnvironmentGetter('BAD_ENV');
        expect(() => getEnv()).toThrow(TakeEnvironmentValueError);

        process.env.APP_ENV = 'foo';
        getEnv = createEnvironmentGetter('APP_ENV', 'NODE_ENV');
        expect(getEnv()).toEqual('foo');
        delete process.env.APP_ENV;
    });

    it('should set configuration', () => {
        const config = new ConfigProvider();
        const value = config.section<{foo: string}>().set('testing', {foo: 'bar'}).get('testing');
        expect(value).toEqual({foo: 'bar'});
    });

    it('should set from configuration', () => {
        const config = new ConfigProvider();
        const value = config
            .section<{foo: string}>()
            .set('testing', {foo: 'bar'})
            .setFrom('production', 'testing', (draft) => {
                draft.foo = 'baz';
            })
            .get('production');
        expect(value).toEqual({foo: 'baz'});

        expect(() =>
            config.section<{foo: string}>().setFrom('production', 'development', (draft) => {
                draft.foo = 'baz';
            })
        ).toThrow(MissedEnvironmentError);
    });

    it('should inherit configuration', () => {
        const config = new ConfigProvider();
        expect(() =>
            config.section<{foo: string}>().inherit('production', (draft) => {
                draft.foo = 'baz';
            })
        ).toThrow(MissedLastSetEnvironmentError);

        const value = config
            .section<{foo: string}>()
            .set('testing', {foo: 'bar'})
            .inherit('production', (draft) => {
                draft.foo = 'baz';
            })
            .get('production');
        expect(value).toEqual({foo: 'baz'});
    });

    it('should handle async bootstrap', async () => {
        const config = new ConfigProvider<Environment, {ok: boolean}>({
            bootstrap: new Promise((resolve) => {
                setTimeout(() => resolve({ok: true}), 100);
            })
        });

        expect(config.getBootstrap()).toEqual(undefined);

        await config.ready;

        expect(config.getBootstrap()).toEqual({ok: true});
    });
});
