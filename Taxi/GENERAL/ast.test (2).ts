import {createImport, createVar, printAst} from './ast';
import {formatContent} from './prettier';
import ts from 'typescript';

describe('createVar', () => {
    test('const variable', () => {
        const result = printAst(createVar('a', ts.factory.createStringLiteral('1')));
        expect(result).toBe(formatContent("const a = '1'"));
    });

    test('let variable', () => {
        const result = printAst(createVar('a', ts.factory.createStringLiteral('1'), 1));
        expect(result).toBe(formatContent("let a = '1'"));
    });
});

describe('createImport', () => {
    test('default import', () => {
        const params = {defaultIdentifier: 'Test', path: '../components/path'};
        const result = printAst(createImport(params));
        expect(result).toBe(formatContent(`import ${params.defaultIdentifier} from "${params.path}"`));
    });
});
