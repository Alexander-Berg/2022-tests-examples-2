import ts from 'typescript';

import {
    createArrayType,
    createImportNode,
    createIndexedSignature,
    createIntersectionNode,
    createLiteralUnion,
    createPartial,
    createPlainType,
    createPropertySignature,
    createSimpleIndexed,
    createSourceFile,
    createTypeAlias,
    createUnionNode,
    createUnknown,
    getSimpleIndexedType,
    isSimpleType,
    isUnknownAst,
    printAst,
    printFile,
} from '../ast';

const INDEXED_SIGNATURE = (type = 'any') => `{
    [x: string]: ${type};
}`;

describe('utils/ast', () => {
    test('createTypeLiteral', () => {
        const sf = createSourceFile('test.d.ts');
        const result = printAst(createPlainType({ type: 'string' }), sf);

        expect(result).toBe('string');
    });

    test('createTypeAlias', () => {
        expect(
            printFile('test.d.ts', [
                createTypeAlias({
                    typeName: 'Test',
                    value: createPlainType({ type: 'boolean' }),
                }),
            ]).trim(),
        ).toBe('export type Test = boolean;');
    });

    test('createIndexed', () => {
        const sf = createSourceFile('test.d.ts');
        const result = printAst(createSimpleIndexed(), sf);

        expect(result).toBe(INDEXED_SIGNATURE());
    });

    test('createImportNode', () => {
        expect(
            printFile('test.d.ts', [
                createImportNode('./test.d.ts', [
                    ['A', undefined],
                    ['B', 'X'],
                ]),
            ]).trim(),
        ).toBe('import { A, B as X } from "./test.d.ts";');
    });

    test('createPartial', () => {
        const sf = createSourceFile('test.d.ts');
        const result = printAst(createPartial([createSimpleIndexed()]), sf);

        expect(result).toBe(`Partial<${INDEXED_SIGNATURE()}>`);
    });

    test('isUnknownAst', () => {
        expect(isUnknownAst(createUnknown())).toBe(true);
        expect(isUnknownAst(createSimpleIndexed())).toBe(false);
    });

    test('isSimpleType', () => {
        expect(isSimpleType(createUnknown())).toBe(true);

        expect(isSimpleType(ts.createKeywordTypeNode(ts.SyntaxKind.BooleanKeyword))).toBe(true);

        expect(isSimpleType(createSimpleIndexed())).toBe(false);
    });

    test('createUnionTypeNode', () => {
        const sf = createSourceFile('test.d.ts');
        const result = printAst(
            createUnionNode([createSimpleIndexed(), undefined, createUnknown(), createUnknown()]),
            sf,
        );

        expect(result).toBe(`${INDEXED_SIGNATURE()} | unknown`);
    });

    test('getSimpleIndexedType', () => {
        expect(getSimpleIndexedType(createSimpleIndexed())).toEqual([ts.SyntaxKind.AnyKeyword]);

        expect(
            getSimpleIndexedType(
                ts.createTypeLiteralNode([
                    createIndexedSignature(ts.createKeywordTypeNode(ts.SyntaxKind.BooleanKeyword)),
                    createIndexedSignature(ts.createKeywordTypeNode(ts.SyntaxKind.NumberKeyword)),
                ]),
            ),
        ).toEqual([ts.SyntaxKind.BooleanKeyword, ts.SyntaxKind.NumberKeyword]);

        expect(
            getSimpleIndexedType(
                ts.createTypeLiteralNode([
                    createIndexedSignature(ts.createKeywordTypeNode(ts.SyntaxKind.BooleanKeyword)),
                    createPropertySignature('x', createUnknown()),
                ]),
            ),
        ).toEqual(null);

        expect(
            getSimpleIndexedType(
                ts.createTypeLiteralNode([createIndexedSignature(ts.createTypeReferenceNode('xxx', []))]),
            ),
        ).toEqual(null);
    });

    test('createIntersectionNode', () => {
        const sf = createSourceFile('test.d.ts');
        const result = printAst(
            createIntersectionNode([
                createSimpleIndexed(),
                undefined,
                createPlainType({ type: 'boolean' }),
                createPlainType({ type: 'boolean' }),
                createIntersectionNode([
                    createSimpleIndexed(),
                    undefined,
                    createPlainType({ type: 'boolean' }),
                    createPlainType({ type: 'boolean' }),
                    createIntersectionNode([
                        createSimpleIndexed(ts.SyntaxKind.NumberKeyword),
                        undefined,
                        createPlainType({ type: 'boolean' }),
                        createPlainType({ type: 'boolean' }),
                    ]),
                ]),
            ]),
            sf,
        );

        expect(result).toBe(`${INDEXED_SIGNATURE()} & boolean & ${INDEXED_SIGNATURE('number')}`);
    });

    test('createUnionNode', () => {
        const sf = createSourceFile('test.d.ts');
        const result = printAst(
            createUnionNode([
                createSimpleIndexed(),
                undefined,
                createUnknown(),
                createUnknown(),
                createUnionNode([
                    createSimpleIndexed(),
                    undefined,
                    createUnknown(),
                    createUnknown(),
                    createUnionNode([
                        createSimpleIndexed(ts.SyntaxKind.NumberKeyword),
                        undefined,
                        createUnknown(),
                        createUnknown(),
                    ]),
                ]),
            ]),
            sf,
        );

        expect(result).toBe(`${INDEXED_SIGNATURE()} | unknown | ${INDEXED_SIGNATURE('number')}`);
    });

    test('createLiteralUnion string', () => {
        const sf = createSourceFile('test.d.ts');
        const result = printAst(createLiteralUnion(['1', '2']), sf);

        expect(result).toBe('"1" | "2"');
    });

    test('createLiteralUnion number', () => {
        const sf = createSourceFile('test.d.ts');
        const result = printAst(createLiteralUnion([1, 2]), sf);

        expect(result).toBe('1 | 2');
    });

    test('createArrayType brackets', () => {
        const sf = createSourceFile('test.d.ts');
        const result = printAst(createArrayType(createUnknown()), sf);

        expect(result).toBe('unknown[]');
    });

    test('createArrayType Array', () => {
        const sf = createSourceFile('test.d.ts');
        const result = printAst(
            createArrayType(
                createUnionNode([createPlainType({ type: 'string' }), createPlainType({ type: 'number' })]),
            ),
            sf,
        );

        expect(result).toBe('Array<string | number>');
    });
});
