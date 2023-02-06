/* eslint-disable @typescript-eslint/explicit-function-return-type */
import { GraphQLError, GraphQLString } from 'graphql';

import { Entity, EntityInput } from '@shared/entity/decorators/entity';
import { EntityField } from '@shared/entity/decorators/field';
import { EntityBase } from '@shared/entity/entity-base';
import { GraphQLEnumWrap, GraphQLOptional, GraphQLTypeWrap } from '@shared/graphql/field-types';
import { GraphQLArg, GraphQLOperationArgs } from '@shared/graphql/args';
import { Logger } from '@server-libs/node-tools/logger';

import { GraphQLController, GraphQLMutation, GraphQLQuery } from '../controller';
import { createGraphQLEndpoint } from '../endpoint';
import { GraphQLResolver } from '../resolver';
import { GraphQLEnum } from '../enum';

const loggerInfoMock = jest.fn();
const loggerErrorMock = jest.fn();
const loggerWarnMock = jest.fn();
jest.mock('@server-libs/node-tools/logger.ts', () => {
    const logger = <jest.Mock & { withContext: jest.Mock }>jest.fn().mockImplementation(function () {
        return {
            info: loggerInfoMock,
            error: loggerErrorMock,
            warn: loggerWarnMock,
        };
    });

    logger.withContext = jest.fn().mockImplementation(logger);

    return {
        Logger: logger,
    };
});

enum TestEnum {
    Foo = 'foo',
    Bar = 'bar',
    Baz = 'baz',
}

class EnumTypes {
    @GraphQLEnum({ name: 'TestEnum' })
    public static readonly testEnum = TestEnum;
}

@Entity('Resolvable')
class Resolvable extends EntityBase {
    @EntityField(GraphQLString)
    name!: string;
}

@Entity('TestEntity')
class TestEntity extends EntityBase {
    @EntityField(GraphQLString)
    name!: string;
    @EntityField(GraphQLOptional.of(GraphQLString))
    optional!: string | null;
    @EntityField(GraphQLString)
    notOptional!: string | null;
    @EntityField(GraphQLEnumWrap.of(TestEnum))
    testEnum!: TestEnum;
    @EntityField(GraphQLTypeWrap.of(Resolvable))
    resolvable!: Resolvable;
    @EntityField(GraphQLTypeWrap.of(Resolvable))
    resolvableAsync!: Resolvable;
}

@Entity('TestEntity')
class TestEntityResolver extends TestEntity {
    constructor(name: string) {
        super();
        this.name = name;
        this.optional = null;
        this.notOptional = null;
        this.testEnum = TestEnum.Foo;
    }

    @GraphQLResolver({ name: 'resolvable', type: GraphQLTypeWrap.of(Resolvable) })
    // eslint-disable-next-line @typescript-eslint/explicit-function-return-type
    public getResolvable() {
        return { name: 'Resolvable' };
    }

    @GraphQLResolver({ name: 'resolvableAsync', type: GraphQLTypeWrap.of(Resolvable) })
    // eslint-disable-next-line @typescript-eslint/explicit-function-return-type
    public async getResolvableAsync() {
        return { name: 'Resolvable Async' };
    }
}

@EntityInput('TestInputEntity')
class TestInputEntity extends EntityBase {
    @EntityField(GraphQLString)
    id!: string;
    @EntityField(GraphQLString)
    name!: string;
}

@GraphQLOperationArgs()
class TestQueryArgs {
    @GraphQLArg(GraphQLTypeWrap.of(TestInputEntity))
    testArg!: TestInputEntity;
}

class TestClient {
    public getTestEntity() {
        return new TestEntityResolver('Test Entity');
    }
}

@GraphQLController()
class TestController {
    @GraphQLQuery({ name: 'testQuery', argsType: TestQueryArgs, type: GraphQLTypeWrap.of(TestEntityResolver) })
    // eslint-disable-next-line @typescript-eslint/explicit-function-return-type
    public async getTestEntity(args: TestQueryArgs) {
        const client = new TestClient();
        return client.getTestEntity();
    }

    @GraphQLMutation({ name: 'testMutation', argsType: TestQueryArgs, type: GraphQLString })
    // eslint-disable-next-line @typescript-eslint/explicit-function-return-type
    public async setTestEntity(args: TestQueryArgs) {
        return 'OK';
    }
}

describe('graphQL endpoint', () => {
    const controller = new TestController();
    const queryMethodSpy = jest.spyOn(controller, 'getTestEntity');
    const mutationMethodSpy = jest.spyOn(controller, 'setTestEntity');
    const entityResolverSpy = jest.spyOn(TestEntityResolver.prototype, 'getResolvable');
    const asyncEntityResolverSpy = jest.spyOn(TestEntityResolver.prototype, 'getResolvableAsync');
    const endpoint = createGraphQLEndpoint({
        entityTypes: [TestEntityResolver, Resolvable, TestInputEntity],
        enumTypes: EnumTypes,
        controllers: [controller],
    });
    const ctx = { logger: new Logger() };

    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('endpoint creation', () => {
        it('should throw error if field type is not present in entityTypes prop', () => {
            expect(() =>
                createGraphQLEndpoint({
                    entityTypes: [],
                    enumTypes: EnumTypes,
                    controllers: [new TestController()],
                })
            ).toThrow(`Unknown type "${TestEntityResolver.toString()}"`);
        });

        it('should throw error if field type is not present in enumTypes prop', () => {
            expect(() =>
                createGraphQLEndpoint({
                    entityTypes: [TestEntityResolver, Resolvable, TestInputEntity],
                    enumTypes: undefined,
                    controllers: [new TestController()],
                })
            ).toThrow(`Unknown enum type for "${JSON.stringify(TestEnum)}" field`);
        });

        it('should log registration info', async () => {
            createGraphQLEndpoint({
                entityTypes: [TestEntityResolver, Resolvable, TestInputEntity],
                enumTypes: EnumTypes,
                controllers: [controller],
            });
            expect(loggerInfoMock).toHaveBeenCalledWith(`Register type and alias '${TestEntityResolver.getName()}'`);
            expect(loggerInfoMock).toHaveBeenCalledWith(`Register type and alias '${Resolvable.getName()}'`);
            expect(loggerInfoMock).toHaveBeenCalledWith(`Register type and alias '${TestInputEntity.getName()}'`);
            expect(loggerInfoMock).toHaveBeenCalledWith(`Register enum type 'TestEnum'`);
            expect(loggerInfoMock).toHaveBeenCalledWith(`Register query 'testQuery'`);
            expect(loggerInfoMock).toHaveBeenCalledWith(`Register mutation 'testMutation'`);
        });

        it('should return Object with execute method', () => {
            expect(endpoint).toBeInstanceOf(Object);
            expect(endpoint).toHaveProperty('execute');
            expect(endpoint.execute.bind(endpoint)).toBeInstanceOf(Function);
        });
    });

    describe('query execution', () => {
        it('should return promise on execute call', async () => {
            const result = endpoint.execute('{testQuery (id: "1") {name}}', ctx);
            expect(result).toBeInstanceOf(Promise);
        });

        it('should return error on invalid input args', async () => {
            const result = await endpoint.execute(`{testQuery (testArg: { id: "foo" }) {name}}`, ctx);
            expect(result.data).toBeUndefined();
            expect(result.errors).toBeDefined();
            expect(result.errors?.[0]).toBeInstanceOf(GraphQLError);
        });

        it('should call corresponded contoller method on query', async () => {
            await endpoint.execute(`{testQuery (testArg: { id: "foo", name: "bar" }) {data {name}}}`, ctx);
            const queryArgs = queryMethodSpy.mock.calls[0];
            expect(queryArgs[0]).toBeInstanceOf(TestQueryArgs);
            expect(queryArgs[0].testArg).toBeInstanceOf(TestInputEntity);
            expect(queryMethodSpy).toHaveBeenCalledWith({ testArg: { id: 'foo', name: 'bar' } }, ctx);
        });

        it('should call entity field resolver with args', async () => {
            await endpoint.execute(
                '{testQuery (testArg: { id: "foo", name: "bar" }) {data {name, resolvable {name}}}}',
                ctx
            );
            expect(entityResolverSpy).toHaveBeenCalledWith(ctx);
        });

        it('should call async entity field resolver with args', async () => {
            await endpoint.execute(
                '{testQuery (testArg: { id: "foo", name: "bar" }) {data {name, resolvableAsync {name}}}}',
                ctx
            );
            expect(asyncEntityResolverSpy).toHaveBeenCalledWith(ctx);
        });

        it('should return expected data', async () => {
            const result = await endpoint.execute(
                '{testQuery (testArg: { id: "foo", name: "bar" }) {data {name, resolvable {name}}}}',
                ctx
            );
            expect(JSON.stringify(result.data)).toBe(
                '{"testQuery":{"data":{"name":"Test Entity","resolvable":{"name":"Resolvable"}}}}'
            );
        });

        it('should return error on invalid fields in query', async () => {
            const result = await endpoint.execute(
                '{testQuery (testArg: { id: "foo", name: "bar" }) {invalidName}}',
                ctx
            );
            expect(result.data).toBeUndefined();
            expect(result.errors).toBeDefined();
            expect(result.errors?.[0]).toBeInstanceOf(GraphQLError);
        });

        it('should return null for null in non-nullable field', async () => {
            const result = await endpoint.execute(
                '{testQuery (testArg: { id: "foo", name: "bar" }) {data {notOptional}}}',
                ctx
            );
            expect(JSON.stringify(result.data)).toBe('{"testQuery":{"data":null}}');
            expect(result.errors).toBeDefined();
            expect(result.errors?.[0]).toBeInstanceOf(GraphQLError);
        });

        it('should return expected data for null in nullable field', async () => {
            const result = await endpoint.execute(
                '{testQuery (testArg: { id: "foo", name: "bar" }) {data {optional}}}',
                ctx
            );
            expect(JSON.stringify(result.data)).toBe('{"testQuery":{"data":{"optional":null}}}');
            expect(JSON.stringify(result.errors)).toBeUndefined();
        });

        it('should return expected data with async resolver', async () => {
            const result = await endpoint.execute(
                '{testQuery (testArg: { id: "foo", name: "bar" }) {data {name, resolvableAsync {name}}}}',
                ctx
            );
            expect(JSON.stringify(result.data)).toBe(
                '{"testQuery":{"data":{"name":"Test Entity","resolvableAsync":{"name":"Resolvable Async"}}}}'
            );
        });

        it('should return errors on exeption in query', async () => {
            const error = new Error('Query Error');
            queryMethodSpy.mockImplementationOnce(() => {
                throw error;
            });
            const result = await endpoint.execute(
                '{testQuery (testArg: { id: "foo", name: "bar" }) {data {name}}}',
                ctx
            );
            expect(result.data?.testQuery).toBe(null);
            expect(result.errors).toBeDefined();
            expect(result.errors?.[0].message).toBe(error.message);
        });

        it('should return errors on exeption in resolver', async () => {
            const error = new Error('Resolver Error');
            entityResolverSpy.mockImplementationOnce(() => {
                throw error;
            });
            const result = await endpoint.execute(
                '{testQuery (testArg: { id: "foo", name: "bar" }) {data {name, resolvable {name}}}}',
                ctx
            );
            expect(JSON.stringify(result.data)).toBe('{"testQuery":{"data":null}}');
            expect(result.errors).toBeDefined();
            expect(result.errors?.[0].message).toBe(error.message);
        });
    });

    describe('mutation execution', () => {
        it('should call corresponded contoller method on mutation', async () => {
            await endpoint.execute(`mutation { testMutation (testArg: { id: "foo", name: "bar" }) {data} }`, ctx);
            const mutationArgs = mutationMethodSpy.mock.calls[0];
            expect(mutationArgs[0]).toBeInstanceOf(TestQueryArgs);
            expect(mutationArgs[0].testArg).toBeInstanceOf(TestInputEntity);
            expect(mutationMethodSpy).toHaveBeenCalledWith({ testArg: { id: 'foo', name: 'bar' } }, ctx);
        });

        it('should return expected data', async () => {
            const result = await endpoint.execute(
                'mutation {testMutation (testArg: { id: "foo", name: "bar" }) {data} }',
                ctx
            );
            expect(JSON.stringify(result.data)).toBe('{"testMutation":{"data":"OK"}}');
        });

        it('should return errors on exeption in mutation', async () => {
            const error = new Error('Mutation Error');
            mutationMethodSpy.mockImplementationOnce(() => {
                throw error;
            });
            const result = await endpoint.execute(
                'mutation {testMutation (testArg: { id: "foo", name: "bar" }) {data} }',
                ctx
            );
            expect(result.data?.testMutation).toBe(null);
            expect(result.errors).toBeDefined();
            expect(result.errors?.[0].message).toBe(error.message);
        });
    });

    describe('logs', () => {
        it('should log field resolve error', async () => {
            const resolvableFieldError = new Error('Resolve error');
            entityResolverSpy.mockImplementationOnce(() => {
                throw resolvableFieldError;
            });
            await endpoint.execute(
                '{testQuery (testArg: { id: "foo", name: "bar" }) {data {name, resolvable {name}}}}',
                ctx
            );
            expect(loggerWarnMock).toHaveBeenCalledWith(
                `Type "${TestEntityResolver.getName()}", field "resolvable" resolve with error`
            );
        });

        it('should log query execution start', async () => {
            await endpoint.execute(
                '{testQuery (testArg: { id: "foo", name: "bar" }) {data {name, resolvable {name}}}}',
                ctx
            );
            expect(loggerInfoMock).toHaveBeenCalledWith(
                `Start executing Query "testQuery" with args: "{"testArg":{"id":"foo","name":"bar"}}"`
            );
        });

        it('should log mutation execution start', async () => {
            await endpoint.execute('mutation {testMutation (testArg: { id: "foo", name: "bar" }) {data} }', ctx);
            expect(loggerInfoMock).toHaveBeenCalledWith(
                `Start executing Mutation "testMutation" with args: "{"testArg":{"id":"foo","name":"bar"}}"`
            );
        });

        it('should log query resolve error', async () => {
            const queryError = new Error('Query error');
            queryMethodSpy.mockImplementationOnce(() => {
                throw queryError;
            });
            await endpoint.execute('{testQuery (testArg: { id: "foo", name: "bar" }) {data {name}}}', ctx);
            expect(loggerWarnMock).toHaveBeenCalledWith(`Query "testQuery" resolve with error: Query error`);
        });

        it('should log mutation resolve error', async () => {
            const mutationError = new Error('Mutation error');
            mutationMethodSpy.mockImplementationOnce(() => {
                throw mutationError;
            });
            await endpoint.execute('mutation {testMutation (testArg: { id: "foo", name: "bar" }) {data} }', ctx);
            expect(loggerWarnMock).toHaveBeenCalledWith(`Mutation "testMutation" resolve with error: Mutation error`);
        });
    });
});
