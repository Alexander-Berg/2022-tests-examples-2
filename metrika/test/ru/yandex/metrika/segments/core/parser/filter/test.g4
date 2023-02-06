parser grammar test;





filter
    : LPAREN filter RPAREN                                                          # Paren
    | K_NOT LPAREN filter RPAREN                                                    # Not
    | quantor ( identifier ( COMMA identifier ) * K_WITH ) ? LPAREN filter RPAREN   # Quantifier
    | filter K_AND filter ( K_AND filter ) *                                        # And
    | filter K_OR filter ( K_OR filter ) *                                          # Or
    | expr relation expr                                                            # Simple
    ;

expr
    : identifier                                                    # SelectPartId
    | value                                                         # Val
    ;
value
    : NUMERIC_LITERAL
    | K_NULL
    | STRING_LITERAL
    ;
relation
    :  EQ
    ;

identifier
    : IDENTIFIER
    ;
quantor
    : K_EXISTS
    | K_ALL
    | K_NONE
    ;
