lexer grammar BoosterLexer;

K_BOOSTER : 'booster' ;

K_YES     : 'yes' ;
K_NO      : 'no' ;
K_MISSING : 'missing' ;
K_LEAF    : 'leaf';

COLON        : ':'                    ;
COMMA        : ','                    ;
ASSIGN       : '='                    ;
LBRAKET      : '['                    ;
RBRAKET      : ']'                    ;
LT           : '<'                    ;


IDENTIFIER
  : [a-zA-Z_] [a-zA-Z_0-9]*
  ;

NUMERIC_LITERAL
 : '-'? DIGIT+ ( '.' DIGIT* )? ( E [-+]? DIGIT+ )?
 | '.' DIGIT+ ( E [-+]? DIGIT+ )?
 ;

STRING_LITERAL
 : '\'' ( ~'\'' | '\\\'' )* '\''
 ;

QUOTED_LITERAL
 : '`' ( ~'`' )* '`'
 ;

SPACES
 : [ \u000B\t\r\n] -> channel(HIDDEN)
 ;

UNEXPECTED_CHAR
 : .
 ;

fragment DIGIT : [0-9];

fragment A : [aA];
fragment B : [bB];
fragment C : [cC];
fragment D : [dD];
fragment E : [eE];
fragment F : [fF];
fragment G : [gG];
fragment H : [hH];
fragment I : [iI];
fragment J : [jJ];
fragment K : [kK];
fragment L : [lL];
fragment M : [mM];
fragment N : [nN];
fragment O : [oO];
fragment P : [pP];
fragment Q : [qQ];
fragment R : [rR];
fragment S : [sS];
fragment T : [tT];
fragment U : [uU];
fragment V : [vV];
fragment W : [wW];
fragment X : [xX];
fragment Y : [yY];
fragment Z : [zZ];
