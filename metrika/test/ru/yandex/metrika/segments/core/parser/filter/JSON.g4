
/** Taken from "The Definitive ANTLR 4 Reference" by Terence Parr */

// Derived from http://json.org
grammar JSON;

json
   : value
   ;

object
   : LCUR pair (COMMA pair)* RCUR
   | LCUR RCUR
   ;

pair
   : key COLON value
   ;

key
   : STRING
   ;

array
   : LBRA value (COMMA value)* RBRA
   | LBRA RBRA
   ;

value
   : STRING
   | NUMBER
   | object
   | array
   | TRUE
   | FALSE
   | NULL
   ;

COMMA : ',' ;
COLON : ':' ;
LBRA  : '[' ;
RBRA  : ']' ;
LCUR  : '{' ;
RCUR  : '}' ;
TRUE  : 'true';
FALSE : 'false';
NULL  : 'null' ;

STRING
   : '"' (ESC | ~ ["\\])* '"'
   ;


fragment ESC
   : '\\' (["\\/bfnrt] | UNICODE)
   ;


fragment UNICODE
   : 'u' HEX HEX HEX HEX
   ;


fragment HEX
   : [0-9a-fA-F]
   ;


NUMBER
   : '-'? INT '.' [0-9] + EXP? | '-'? INT EXP | '-'? INT
   ;


fragment INT
   : '0' | [1-9] [0-9]*
   ;

// no leading zeros

fragment EXP
   : [Ee] [+\-]? INT
   ;

// \- since - means "range" inside [...]

WS
   : [ \t\n\r] + -> skip
   ;
