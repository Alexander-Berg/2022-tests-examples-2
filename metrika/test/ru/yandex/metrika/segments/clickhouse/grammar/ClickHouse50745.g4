grammar ClickHouse;

// эта грамматика написана по сорсам парсеров, имена правил примерно соответствуют парсерам в cpp.
// известные расхождения
// 1. скобки не обязательно сразу идут после имени функции.
// 2. многословные токены поделены на самостоятельные слова
// 3. для INSERT запроса не написана часть парсинга значений.

parse
 : ( query | error ) EOF
 ;

query
 :   (select_query
 |    insert_query
 |    create_query
 |    rename_query
 |    drop_query
 |    alter_query
 |    use_query
 |    set_query
 |    optimize_query
 |    table_properties_query
 |    show_processlist_query
 |    check_query)
 ;

// 1. QUERIES

select_query
 : K_SELECT (K_DISTINCT)? not_empty_expression_list K_FROM
            (database '.' table
            | table
            | table_function
            | subquery)
          ( K_FINAL)? (K_SAMPLE NUMERIC_LITERAL)? // wtf
          (K_ARRAY K_JOIN not_empty_expression_list)?
          join?
          (K_PREWHERE expression_with_optional_alias)?
          (K_WHERE expression_with_optional_alias)?
          (K_GROUP K_BY not_empty_expression_list)?
          (K_WITH K_TOTALS)?
          (K_HAVING expression_with_optional_alias)?
          (K_ORDER K_BY order_by_expression_list)?
          (K_LIMIT NUMERIC_LITERAL (',' NUMERIC_LITERAL)? )?
          (K_FORMAT identifier)?
          (K_UNION K_ALL select_query)?
 ;

insert_query
 :  K_INSERT K_INTO ( database '.' table | table )
          (K_ID '=' STRING_LITERAL)? // wtf?
          ( '(' columns ')' )?
          ( K_VALUES '(' literal (',' literal )* ')'(',' '(' literal (',' literal )* ')')* // ch тут дальше не парсит. а я написал скобки
          | K_FORMAT identifier // ch тут дальше не парсит, только доедает все пробелы или один перевод строки.
          | select_query )
 ;

create_query
 :  ( K_CREATE | K_ATTACH ) ( K_TEMPORARY )?
            ( K_DATABASE ( K_IF K_NOT K_EXISTS )? database
            | K_TABLE ( K_IF K_NOT K_EXISTS )? ( database '.' table | table )
               ( '(' columns_declaration ')' engine ( K_AS select_query)? // если VIEW - то есть и колонки и select.
               | engine K_AS (  select_query
                             |  ( database '.' table | table ) engine? // wtf
                             )
               )
            | ( K_MATERIALIZED ) ? K_VIEW ( K_IF K_NOT K_EXISTS )? ( database '.' table | table )
               ( '(' columns_declaration ')' )? engine? K_POPULATE? K_AS select_query
            )
 ;

rename_query
 :  K_RENAME K_TABLE table_to_table ( ',' table_to_table )*
 ;

drop_query
 :  ( K_DROP | K_DETACH )
            ( K_DATABASE ( K_IF K_EXISTS )? database
            | K_TABLE ( K_IF K_EXISTS )? ( database '.' table | table )
            )
 ;

alter_query
 : K_ALTER K_TABLE ( database '.' table | table )
        alter_query_element ( ',' alter_query_element )*
 ;

alter_query_element
 : K_ADD K_COLUMN compound_name_type_pair ( K_AFTER compound_identifier )?
 | K_DROP K_COLUMN compound_identifier
 | K_MODIFY K_COLUMN compound_name_type_pair
 ;

use_query
 : K_USE database
 ;

set_query
 : K_SET ( K_GLOBAL )? identifier '=' literal ( ',' identifier '=' literal )*
 ;

optimize_query
 : K_OPTIMIZE K_TABLE ( database '.' table | table )
 ;

table_properties_query
 : ( K_EXISTS | ( K_DESCRIBE | K_DESC ) | K_SHOW K_CREATE ) K_TABLE ( database '.' table | table ) ( K_FORMAT identifier )?
 ;

show_processlist_query
 : K_SHOW K_PROCESSLIST ( K_FORMAT identifier )?
 ;

check_query
 : K_CHECK K_TABLE ( database '.' table | table )
 ;

// 2. QUERY ELEMENTS

 table_to_table
 :   ( database '.' table | table ) K_TO ( database '.' table | table )
 ;
engine
 : K_ENGINE '=' identifier_with_optional_parameters
 ;

identifier_with_optional_parameters
 :    identifier_with_parameters
 |    identifier
 ;

identifier_with_parameters
 : function
 | nested_table
 ;

order_by_expression_list
 :  order_by_element ( ',' order_by_element)*
 ;

order_by_element
 : expression_with_optional_alias ( K_DESC | K_DESCENDING | K_ASC | K_ASCENDING )? ( K_COLLATE STRING_LITERAL )?
 ;

nested_table
 :   identifier '(' name_type_pair_list ')'
 ;

name_type_pair_list
 :  name_type_pair (',' name_type_pair)*
 ;

name_type_pair
 : identifier column_type
 ;

compound_name_type_pair
 : compound_identifier column_type
 ;

columns_declaration
 : column_declaration ( ',' column_declaration)*
 ;

column_declaration
 : identifier
      ( ( K_DEFAULT | K_MATERIALIZED | K_ALIAS ) ternary_operator_expression )
      | column_type
 ;

column_type
 : identifier_with_optional_parameters
 ;

columns
 :  identifier (',' identifier)*
 ;

alias
 : K_AS identifier
 ;

database
 :   identifier
 ;

table
 :   identifier
 ;

table_function
 :   function
 ;

join
 :  ( K_GLOBAL )? ( K_ANY | K_ALL ) ( K_INNER | K_LEFT ) K_JOIN
    ( identifier | subquery ) K_USING not_empty_expression_list
 ;

subquery
 :  '(' select_query ')'
 ;

//  EXPRESSIONS

expression_list
 :   not_empty_expression_list?
 ;

expression_element
 : subquery
 | parenthesis_expression
 | array
 | literal
 | function
 | compound_identifier
 | '*'
 ;

parenthesis_expression
 :   '('  not_empty_expression_list ')'
 ;

not_empty_expression_list
 : expression_with_optional_alias ( ',' expression_with_optional_alias )*
 ;

expression_with_optional_alias
 : lambda_expression alias?
 ;

lambda_expression
 :   ( '(' identifier ( ',' identifier )* ')' | identifier ( ',' identifier )* ) '->' ternary_operator_expression
 |   ternary_operator_expression
 ;

ternary_operator_expression
 : logical_or_expression ( '?' logical_or_expression ':' logical_or_expression )?
 ;

logical_or_expression
 : logical_and_expression ( K_OR logical_and_expression )*
 ;

 logical_and_expression
 : logical_not_expression ( K_AND logical_not_expression )*
 ;

logical_not_expression
 : ( K_NOT )? comparison_expression
 ;

 comparison_expression
 :  additive_expression
 ( '==' | '!=' | '<>' | '<=' | '>=' | '<' | '>' | '=' | K_LIKE | K_NOT K_LIKE | K_IN | K_NOT K_IN | K_GLOBAL K_IN | K_GLOBAL K_NOT K_IN )
    additive_expression
 ;

 additive_expression
 :  multiplicative_expression  ( ( '+' | '-' ) multiplicative_expression )*
 ;

multiplicative_expression
 :  unary_minus_expression ( ( '*' | '/' | '%' ) unary_minus_expression )*
 ;

unary_minus_expression
 : ( '-' )? access_expression
 ;

access_expression
 : expression_element ( '.' expression_with_optional_alias
                      | '[' expression_with_optional_alias ']' )*
 ;



array
 :   '[' expression_list ']'
 ;

function
 :   identifier '(' expression_list ')'  ( '(' expression_list ')' )?
 ;

identifier
 :  QUOTED_LITERAL
 |    IDENTIFIER
 ;

compound_identifier
: IDENTIFIER ('.' IDENTIFIER)*
| QUOTED_LITERAL
;


literal
 :   ( K_NULL
 |    NUMERIC_LITERAL
 |    STRING_LITERAL)
 ;

error
 : UNEXPECTED_CHAR
   {
     throw new RuntimeException("UNEXPECTED_CHAR=" + $UNEXPECTED_CHAR.text);
   }
 ;

K_ADD : A D D;
K_AFTER : A F T E R;
K_ALL : A L L;
K_ALIAS : A L I A S;
K_ALTER : A L T E R;
K_AND : A N D;
K_ANY : A N Y;
K_ARRAY : A R R A Y;
K_ASCENDING : A S C E N D I N G;
K_ASC : A S C;
K_AS : A S;
K_ATTACH : A T T A C H;
K_BY : B Y;
K_CHECK : C H E C K;
K_COLUMN : C O L U M N;
K_COLLATE : C O L L A T E;
K_CREATE : C R E A T E;
K_DESCRIBE : D E S C R I B E;
K_DESCENDING : D E S C E N D I N G;
K_DESC : D E S C;
K_DATABASE : D A T A B A S E;
K_DEFAULT : D E F A U L T;
K_DETACH : D E T A C H;
K_DISTINCT : D I S T I N C T;
K_DROP : D R O P;
K_ENGINE : E N G I N E;
K_EXISTS : E X I S T S;
K_FINAL : F I N A L;
K_FROM : F R O M;
K_FORMAT : F O R M A T;
K_GLOBAL : G L O B A L;
K_GROUP : G R O U P;
K_HAVING : H A V I N G;
K_ID : I D;
K_IF : I F;
K_INNER : I N N E R;
K_INSERT : I N S E R T;
K_INTO : I N T O;
K_IN : I N;
K_JOIN : J O I N;
K_LEFT : L E F T;
K_LIKE : L I K E;
K_LIMIT : L I M I T;
K_MATERIALIZED : M A T E R I A L I Z E D;
K_MODIFY : M O D I F Y;
K_NOT : N O T;
K_NULL : N U L L;
K_OPTIMIZE : O P T I M I Z E;
K_ORDER : O R D E R;
K_OR : O R;
K_POPULATE : P O P U L A T E;
K_PREWHERE : P R E W H E R E;
K_PROCESSLIST : P R O C E S S L I S T;
K_RENAME : R E N A M E;
K_SAMPLE : S A M P L E;
K_SELECT : S E L E C T;
K_SET : S E T;
K_SHOW : S H O W;
K_TABLE : T A B L E;
K_TEMPORARY : T E M P O R A R Y;
K_TOTALS : T O T A L S;
K_TO : T O;
K_VALUES : V A L U E S;
K_VIEW : V I E W;
K_UNION : U N I O N;
K_USE : U S E;
K_USING : U S I N G;
K_WHERE : W H E R E;
K_WITH : W I T H;

 IDENTIFIER
  : [a-zA-Z_] [a-zA-Z_0-9]*
  ;

NUMERIC_LITERAL
 : DIGIT+ ( '.' DIGIT* )? ( E [-+]? DIGIT+ )?
 | '.' DIGIT+ ( E [-+]? DIGIT+ )?
 ;

STRING_LITERAL
 : '\'' ( ~'\'' | '\'\'' )* '\''
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
