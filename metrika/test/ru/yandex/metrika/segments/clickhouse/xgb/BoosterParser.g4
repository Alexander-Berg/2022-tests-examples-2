parser grammar BoosterParser;

options {
	tokenVocab=BoosterLexer;
}

boosters
  : booster *
  ;


booster
  : K_BOOSTER LBRAKET NUMERIC_LITERAL RBRAKET COLON
  node
  ;

node
  : branch_node
  | leaf_node
  ;

branch_node
  : node_id COLON LBRAKET IDENTIFIER LT NUMERIC_LITERAL RBRAKET
      K_YES ASSIGN node_id COMMA
      K_NO ASSIGN node_id COMMA
      K_MISSING ASSIGN node_id
      node node
  ;

node_id
  : NUMERIC_LITERAL
  ;

leaf_node : node_id COLON K_LEAF ASSIGN NUMERIC_LITERAL;