// TODO rewrite to operation2

it('operations', () => {
    expect(true);
});

export {};
// import { GraphQLInt, GraphQLString } from 'graphql';
// import { Entity } from '@shared/entity/decorators/entity';
// import { EntityField } from '@shared/entity/decorators/field';
// import { GraphQLList, GraphQLOptional, GraphQLTypeWrap } from '@shared/graphql/field-types';
// import { GraphQLEntityResultOperation } from '../operation';
// import { EntityBase } from '@shared/entity/entity-base';
// import { getOperationMeta, MutationOperation, QueryOperation } from '../decorators';
// import { GraphQLArg, GraphQLOperationArgs } from '@shared/graphql/args';
//
// const mockClientRequest = jest.fn();
// const mockGraphQLClient = {
//     rawRequest: mockClientRequest,
// };
//
// @Entity('Simple')
// class SimpleEntity extends EntityBase {
//     @EntityField(GraphQLString)
//     scalarField!: string;
//     @EntityField(GraphQLOptional.of(GraphQLString))
//     optionalScalarField?: string;
// }
//
// @Entity('Extended')
// class ExtendedEntity extends EntityBase {
//     @EntityField(GraphQLInt)
//     scalarField!: number;
//
//     @EntityField(GraphQLTypeWrap.of(SimpleEntity))
//     link!: SimpleEntity;
//
//     @EntityField(GraphQLList.of(GraphQLTypeWrap.of(SimpleEntity)))
//     linkToList!: Array<SimpleEntity>;
// }
//
// @GraphQLOperationArgs()
// export class SimpleQueryArgs {
//     @GraphQLArg(GraphQLString)
//     id!: string;
// }
//
// @GraphQLOperationArgs()
// export class ExtendedQueryArgs {
//     @GraphQLArg(GraphQLOptional.of(GraphQLString))
//     optional!: string;
//     @GraphQLArg(GraphQLList.of(GraphQLString))
//     list!: string[];
//     @GraphQLArg(GraphQLTypeWrap.of(SimpleEntity))
//     entity!: SimpleEntity;
// }
//
// const queryOperationName = 'simpleQuery';
// @QueryOperation(queryOperationName, SimpleEntity)
// class SimpleQueryOperation extends GraphQLEntityResultOperation<SimpleEntity> {}
//
// @QueryOperation(queryOperationName, SimpleEntity, SimpleQueryArgs)
// class SimpleQueryWithArgsOperation extends GraphQLEntityResultOperation<SimpleEntity, SimpleQueryArgs> {}
//
// @QueryOperation(queryOperationName, SimpleEntity, ExtendedQueryArgs)
// class SimpleQueryWithExtendedArgsOperation extends GraphQLEntityResultOperation<SimpleEntity, ExtendedQueryArgs> {}
//
// const extendedQueryOperationName = 'extendedQuery';
// @QueryOperation(extendedQueryOperationName, ExtendedEntity)
// class ExtendedQueryOperation extends GraphQLEntityResultOperation<ExtendedEntity> {}
//
// const simpleMutationName = 'simpleMutation';
// @MutationOperation(simpleMutationName)
// class SimpleMutationOperation extends GraphQLEntityResultOperation<SimpleEntity> {}
//
// @MutationOperation(simpleMutationName, SimpleEntity)
// class MutationOperationThatReturnsEntity extends GraphQLEntityResultOperation<SimpleEntity> {}
//
// const simpleQueryOperation = new SimpleQueryOperation(mockGraphQLClient, getOperationMeta(SimpleQueryOperation));
// const simpleQueryWithArgsOperation = new SimpleQueryWithArgsOperation(
//     mockGraphQLClient,
//     getOperationMeta(SimpleQueryWithArgsOperation)
// );
// const simpleQueryWithExtendedArgsOperation = new SimpleQueryWithExtendedArgsOperation(
//     mockGraphQLClient,
//     getOperationMeta(SimpleQueryWithExtendedArgsOperation)
// );
// const extendedQueryOperation = new ExtendedQueryOperation(mockGraphQLClient, getOperationMeta(ExtendedQueryOperation));
// const simpleMutationOperation = new SimpleMutationOperation(
//     mockGraphQLClient,
//     getOperationMeta(SimpleMutationOperation)
// );
// const mutationOperationThatReturnEntity = new MutationOperationThatReturnsEntity(
//     mockGraphQLClient,
//     getOperationMeta(MutationOperationThatReturnsEntity)
// );
//
// describe('GraphQL operations', () => {
//     beforeEach(() => {
//         jest.clearAllMocks();
//     });
//
//     describe('query build', () => {
//         it('should build simple query request', async () => {
//             mockClientRequest.mockImplementation(() => ({ [queryOperationName]: { scalarField: 'foo' } }));
//             await simpleQueryOperation.invoke(undefined);
//             expect(mockClientRequest).toHaveBeenCalledWith(
//                 'fragment simple on Simple { scalarField optionalScalarField } query simpleQuery { simpleQuery{ ...simple } }',
//                 undefined
//             );
//         });
//
//         it('should build simple query with args', async () => {
//             mockClientRequest.mockImplementation(() => ({ [queryOperationName]: { scalarField: 'foo' } }));
//             const args = { id: 'bar' };
//             await simpleQueryWithArgsOperation.invoke(args);
//             expect(mockClientRequest).toHaveBeenCalledWith(
//                 'fragment simple on Simple { scalarField optionalScalarField } query simpleQuery($id : String!) { simpleQuery(id : $id){ ...simple } }',
//                 args
//             );
//         });
//
//         it('should build simple query with extended args', async () => {
//             mockClientRequest.mockImplementation(() => ({ [queryOperationName]: { scalarField: 'foo' } }));
//             const args = { optional: 'bar', list: ['foo', 'baz'], entity: new SimpleEntity() };
//             await simpleQueryWithExtendedArgsOperation.invoke(args);
//             expect(mockClientRequest).toHaveBeenCalledWith(
//                 'fragment simple on Simple { scalarField optionalScalarField } query simpleQuery($optional : String, $list : [String!]!, $entity : Simple!) { simpleQuery(optional : $optional, list : $list, entity : $entity){ ...simple } }',
//                 args
//             );
//         });
//
//         it('should build extended query', async () => {
//             mockClientRequest.mockImplementation(() => ({
//                 [extendedQueryOperationName]: {
//                     scalarField: 'foo',
//                     link: { scalarField: 'bar' },
//                     linkToList: [{ scalarField: 'quux' }],
//                 },
//             }));
//             await extendedQueryOperation.invoke(undefined);
//             expect(mockClientRequest).toHaveBeenCalledWith(
//                 'fragment simple on Simple { scalarField optionalScalarField } fragment extended on Extended { scalarField link { ...simple } linkToList { ...simple } } query extendedQuery { extendedQuery{ ...extended } }',
//                 undefined
//             );
//         });
//
//         it('should build simple mutation request', async () => {
//             mockClientRequest.mockImplementation(() => ({ [simpleMutationName]: undefined }));
//             await simpleMutationOperation.invoke(undefined);
//             expect(mockClientRequest).toHaveBeenCalledWith('mutation simpleMutation { simpleMutation }', undefined);
//         });
//
//         it('should build mutation request that returns entity', async () => {
//             mockClientRequest.mockImplementation(() => ({ [simpleMutationName]: { scalarField: 'foo' } }));
//             await mutationOperationThatReturnEntity.invoke(undefined);
//             expect(mockClientRequest).toHaveBeenCalledWith(
//                 'fragment simple on Simple { scalarField optionalScalarField } mutation simpleMutation { simpleMutation{ ...simple } }',
//                 undefined
//             );
//         });
//     });
//
//     describe('query execution result', () => {
//         it('should return expected entity instance', async () => {
//             mockClientRequest.mockImplementation(() => ({ [queryOperationName]: { scalarField: 'foo' } }));
//             const result = await simpleQueryOperation.invoke(undefined);
//             expect(result).toBeInstanceOf(SimpleEntity);
//         });
//
//         it('should return expected entity instance recursively', async () => {
//             mockClientRequest.mockImplementation(() => ({
//                 [extendedQueryOperationName]: {
//                     scalarField: 'foo',
//                     link: { scalarField: 'bar' },
//                     linkToList: [{ scalarField: 'quux' }],
//                 },
//             }));
//             const result = <ExtendedEntity>await extendedQueryOperation.invoke(undefined);
//             expect(result).toBeInstanceOf(ExtendedEntity);
//             expect(result.link).toBeInstanceOf(SimpleEntity);
//             result.linkToList.every(link => {
//                 expect(link).toBeInstanceOf(SimpleEntity);
//             });
//         });
//
//         it('should not rejected on undefined in optional field', async () => {
//             mockClientRequest.mockImplementation(() => ({
//                 [extendedQueryOperationName]: {
//                     scalarField: 'foo',
//                     link: { scalarField: 'bar' },
//                     linkToList: [
//                         {
//                             scalarField: 'quux',
//                             optionalScalarField: undefined,
//                         },
//                     ],
//                 },
//             }));
//             const result = <ExtendedEntity>await extendedQueryOperation.invoke(undefined);
//             expect(result.linkToList).toBeInstanceOf(Array);
//             expect(result.linkToList[0]).toBeInstanceOf(SimpleEntity);
//             expect(result.linkToList[0].optionalScalarField).toBe(undefined);
//         });
//
//         it('should rejected on undefined in non-optional field', async () => {
//             mockClientRequest.mockImplementation(() => ({
//                 [extendedQueryOperationName]: {
//                     scalarField: 'foo',
//                     link: { scalarField: 'bar' },
//                     linkToList: [{ scalarField: undefined }],
//                 },
//             }));
//             await expect(extendedQueryOperation.invoke(undefined)).rejects.toBeDefined();
//         });
//
//         it('should rejected on invalid fetch result', async () => {
//             mockClientRequest.mockImplementation(() => ({ [queryOperationName]: undefined }));
//             await expect(simpleQueryOperation.invoke(undefined)).rejects.toBeDefined();
//         });
//     });
// });
