/*
 * [The "BSD license"]
 *  Copyright (c) 2013 Terence Parr
 *  Copyright (c) 2013 Sam Harwell
 *  All rights reserved.
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions
 *  are met:
 *
 *  1. Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *  2. Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *  3. The name of the author may not be used to endorse or promote products
 *     derived from this software without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
 *  IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 *  OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 *  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
 *  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 *  NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 *  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 *  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 *  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
 *  THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/** A grammar for ANTLR v4 written in ANTLR v4.
*/
parser grammar ANTLRv4Parser;

options {
	tokenVocab=ANTLRv4Lexer;
}

// The main entry point for parsing a v4 grammar.
grammarSpec
	:	DOC_COMMENT?
		grammarType id SEMI
		prequelConstruct*
		rules
		modeSpec*
		EOF
	;

grammarType
	:	(	LEXER GRAMMAR
		|	PARSER GRAMMAR
		|	GRAMMAR
		)
	;

// This is the list of all constructs that can be declared before
// the set of rules that compose the grammar, and is invoked 0..n
// times by the grammarPrequel rule.
prequelConstruct
	:	optionsSpec
	|	delegateGrammars
	|	tokensSpec
	|	action
	;

// A list of options that affect analysis and/or code generation
optionsSpec
	:	OPTIONS (option SEMI)* RBRACE
	;

option
	:	id ASSIGN optionValue
	;

optionValue
	:	id (DOT id)*
	|	STRING_LITERAL
	|	ACTION
	|	INT
	;

delegateGrammars
	:	IMPORT delegateGrammar (COMMA delegateGrammar)* SEMI
	;

delegateGrammar
	:	id ASSIGN id
	|	id
	;

tokensSpec
	:	TOKENS id (COMMA id)* COMMA? RBRACE
	;

/** Match stuff like @parser::members {int i;} */
action
	:	AT (actionScopeName COLONCOLON)? id ACTION
	;

/** Sometimes the scope names will collide with keywords; allow them as
 *  ids for action scopes.
 */
actionScopeName
	:	id
	|	LEXER
	|	PARSER
	;

modeSpec
	:	MODE id SEMI lexerRule*
	;

rules
	:	ruleSpec*
	;

ruleSpec
	:	parserRuleSpec
	|	lexerRule
	;

parserRuleSpec
	:	DOC_COMMENT?
        ruleModifiers? RULE_REF ARG_ACTION?
        ruleReturns? throwsSpec? localsSpec?
		rulePrequel*
		COLON
            ruleBlock
		SEMI
		exceptionGroup
	;

exceptionGroup
	:	exceptionHandler* finallyClause?
	;

exceptionHandler
	:	CATCH ARG_ACTION ACTION
	;

finallyClause
	:	FINALLY ACTION
	;

rulePrequel
	:	optionsSpec
	|	ruleAction
	;

ruleReturns
	:	RETURNS ARG_ACTION
	;

throwsSpec
	:	THROWS id (COMMA id)*
	;

localsSpec
	:	LOCALS ARG_ACTION
	;

/** Match stuff like @init {int i;} */
ruleAction
	:	AT id ACTION
	;

ruleModifiers
	:	ruleModifier+
	;

// An individual access modifier for a rule. The 'fragment' modifier
// is an internal indication for lexer rules that they do not match
// from the input but are like subroutines for other lexer rules to
// reuse for certain lexical patterns. The other modifiers are passed
// to the code generation templates and may be ignored by the template
// if they are of no use in that language.
ruleModifier
	:	PUBLIC
	|	PRIVATE
	|	PROTECTED
	|	FRAGMENT
	;

ruleBlock
	:	ruleAltList
	;

ruleAltList
	:	labeledAlt (OR labeledAlt)*
	;

labeledAlt
	:	alternative (POUND id)?
	;

lexerRule
	:	DOC_COMMENT? FRAGMENT?
		TOKEN_REF COLON lexerRuleBlock SEMI
	;

lexerRuleBlock
	:	lexerAltList
	;

lexerAltList
	:	lexerAlt (OR lexerAlt)*
	;

lexerAlt
	:	lexerElements lexerCommands?
	|
	;

lexerElements
	:	lexerElement+
	;

lexerElement
	:	labeledLexerElement ebnfSuffix?
	|	lexerAtom ebnfSuffix?
	|	lexerBlock ebnfSuffix?
	|	ACTION QUESTION? // actions only allowed at end of outer alt actually,
                         // but preds can be anywhere
	;

labeledLexerElement
	:	id (ASSIGN|PLUS_ASSIGN)
		(	lexerAtom
		|	block
		)
	;

lexerBlock
	:	LPAREN lexerAltList RPAREN
	;

// E.g., channel(HIDDEN), skip, more, mode(INSIDE), push(INSIDE), pop
lexerCommands
	:	RARROW lexerCommand (COMMA lexerCommand)*
	;

lexerCommand
	:	lexerCommandName LPAREN lexerCommandExpr RPAREN
	|	lexerCommandName
	;

lexerCommandName
	:	id
	|	MODE
	;

lexerCommandExpr
	:	id
	|	INT
	;

altList
	:	alternative (OR alternative)*
	;

alternative
	:	elementOptions? element*
	;

element
	:	labeledElement
		(	ebnfSuffix
		|
		)
	|	atom
		(	ebnfSuffix
		|
		)
	|	ebnf
	|	ACTION QUESTION? // SEMPRED is ACTION followed by QUESTION
	;

labeledElement
	:	id (ASSIGN|PLUS_ASSIGN)
		(	atom
		|	block
		)
	;

ebnf:	block blockSuffix?
	;

blockSuffix
	:	ebnfSuffix // Standard EBNF
	;

ebnfSuffix
	:	QUESTION QUESTION?
  	|	STAR QUESTION?
   	|	PLUS QUESTION?
	;

lexerAtom
	:	range
	|	terminal
	|	RULE_REF
	|	notSet
	|	LEXER_CHAR_SET
	|	DOT elementOptions?
	;

atom
	:	range      #AtomRange  // Range x..y - only valid in lexers
	|	terminal   #AtomTerminal
	|	ruleref    #AtomRuleRef
	|	notSet     #AtomNotSet
	|	DOT elementOptions?  #AtomOptions
	;

notSet
	:	NOT setElement
	|	NOT blockSet
	;

blockSet
	:	LPAREN setElement (OR setElement)* RPAREN
	;

setElement
	:	TOKEN_REF elementOptions?
	|	STRING_LITERAL elementOptions?
	|	range
	|	LEXER_CHAR_SET
	;

block
	:	LPAREN
		( optionsSpec? ruleAction* COLON )?
		altList
		RPAREN
	;

ruleref
	:	RULE_REF ARG_ACTION? elementOptions?
	;

range
	: STRING_LITERAL RANGE STRING_LITERAL
	;

terminal
	:   TOKEN_REF elementOptions?
	|   STRING_LITERAL elementOptions?
	;

// Terminals may be adorned with certain options when
// reference in the grammar: TOK<,,,>
elementOptions
	:	LT elementOption (COMMA elementOption)* GT
	;

elementOption
	:	// This format indicates the default node option
		id
	|	// This format indicates option assignment
		id ASSIGN (id | STRING_LITERAL)
	;

id	:	RULE_REF
	|	TOKEN_REF
	;
