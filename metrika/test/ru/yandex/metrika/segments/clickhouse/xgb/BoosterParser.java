// Generated from /home/orantius/dev/projects/metrika/metrika-api/segments/src/test/ru/yandex/metrika/segments/clickhouse/xgb/BoosterParser.g4 by ANTLR 4.7
package ru.yandex.metrika.segments.clickhouse.xgb;

import java.util.List;

import org.antlr.v4.runtime.Parser;
import org.antlr.v4.runtime.ParserRuleContext;
import org.antlr.v4.runtime.RecognitionException;
import org.antlr.v4.runtime.RuntimeMetaData;
import org.antlr.v4.runtime.TokenStream;
import org.antlr.v4.runtime.Vocabulary;
import org.antlr.v4.runtime.VocabularyImpl;
import org.antlr.v4.runtime.atn.ATN;
import org.antlr.v4.runtime.atn.ATNDeserializer;
import org.antlr.v4.runtime.atn.ParserATNSimulator;
import org.antlr.v4.runtime.atn.PredictionContextCache;
import org.antlr.v4.runtime.dfa.DFA;
import org.antlr.v4.runtime.tree.ParseTreeListener;
import org.antlr.v4.runtime.tree.TerminalNode;

@SuppressWarnings({"all", "warnings", "unchecked", "unused", "cast"})
public class BoosterParser extends Parser {
    static { RuntimeMetaData.checkVersion("4.7", RuntimeMetaData.VERSION); }

    protected static final DFA[] _decisionToDFA;
    protected static final PredictionContextCache _sharedContextCache =
        new PredictionContextCache();
    public static final int
        K_BOOSTER=1, K_YES=2, K_NO=3, K_MISSING=4, K_LEAF=5, COLON=6, COMMA=7,
        ASSIGN=8, LBRAKET=9, RBRAKET=10, LT=11, IDENTIFIER=12, NUMERIC_LITERAL=13,
        STRING_LITERAL=14, QUOTED_LITERAL=15, SPACES=16, UNEXPECTED_CHAR=17;
    public static final int
        RULE_boosters = 0, RULE_booster = 1, RULE_node = 2, RULE_branch_node = 3,
        RULE_node_id = 4, RULE_leaf_node = 5;
    public static final String[] ruleNames = {
        "boosters", "booster", "node", "branch_node", "node_id", "leaf_node"
    };

    private static final String[] _LITERAL_NAMES = {
        null, "'booster'", "'yes'", "'no'", "'missing'", "'leaf'", "':'", "','",
        "'='", "'['", "']'", "'<'"
    };
    private static final String[] _SYMBOLIC_NAMES = {
        null, "K_BOOSTER", "K_YES", "K_NO", "K_MISSING", "K_LEAF", "COLON", "COMMA",
        "ASSIGN", "LBRAKET", "RBRAKET", "LT", "IDENTIFIER", "NUMERIC_LITERAL",
        "STRING_LITERAL", "QUOTED_LITERAL", "SPACES", "UNEXPECTED_CHAR"
    };
    public static final Vocabulary VOCABULARY = new VocabularyImpl(_LITERAL_NAMES, _SYMBOLIC_NAMES);

    /**
     * @deprecated Use {@link #VOCABULARY} instead.
     */
    @Deprecated
    public static final String[] tokenNames;
    static {
        tokenNames = new String[_SYMBOLIC_NAMES.length];
        for (int i = 0; i < tokenNames.length; i++) {
            tokenNames[i] = VOCABULARY.getLiteralName(i);
            if (tokenNames[i] == null) {
                tokenNames[i] = VOCABULARY.getSymbolicName(i);
            }

            if (tokenNames[i] == null) {
                tokenNames[i] = "<INVALID>";
            }
        }
    }

    @Override
    @Deprecated
    public String[] getTokenNames() {
        return tokenNames;
    }

    @Override

    public Vocabulary getVocabulary() {
        return VOCABULARY;
    }

    @Override
    public String getGrammarFileName() { return "BoosterParser.g4"; }

    @Override
    public String[] getRuleNames() { return ruleNames; }

    @Override
    public String getSerializedATN() { return _serializedATN; }

    @Override
    public ATN getATN() { return _ATN; }

    public BoosterParser(TokenStream input) {
        super(input);
        _interp = new ParserATNSimulator(this,_ATN,_decisionToDFA,_sharedContextCache);
    }
    public static class BoostersContext extends ParserRuleContext {
        public List<BoosterContext> booster() {
            return getRuleContexts(BoosterContext.class);
        }
        public BoosterContext booster(int i) {
            return getRuleContext(BoosterContext.class,i);
        }
        public BoostersContext(ParserRuleContext parent, int invokingState) {
            super(parent, invokingState);
        }
        @Override public int getRuleIndex() { return RULE_boosters; }
        @Override
        public void enterRule(ParseTreeListener listener) {
            if ( listener instanceof BoosterParserListener ) ((BoosterParserListener)listener).enterBoosters(this);
        }
        @Override
        public void exitRule(ParseTreeListener listener) {
            if ( listener instanceof BoosterParserListener ) ((BoosterParserListener)listener).exitBoosters(this);
        }
    }

    public final BoostersContext boosters() throws RecognitionException {
        BoostersContext _localctx = new BoostersContext(_ctx, getState());
        enterRule(_localctx, 0, RULE_boosters);
        int _la;
        try {
            enterOuterAlt(_localctx, 1);
            {
            setState(15);
            _errHandler.sync(this);
            _la = _input.LA(1);
            while (_la==K_BOOSTER) {
                {
                {
                setState(12);
                booster();
                }
                }
                setState(17);
                _errHandler.sync(this);
                _la = _input.LA(1);
            }
            }
        }
        catch (RecognitionException re) {
            _localctx.exception = re;
            _errHandler.reportError(this, re);
            _errHandler.recover(this, re);
        }
        finally {
            exitRule();
        }
        return _localctx;
    }

    public static class BoosterContext extends ParserRuleContext {
        public TerminalNode K_BOOSTER() { return getToken(BoosterParser.K_BOOSTER, 0); }
        public TerminalNode LBRAKET() { return getToken(BoosterParser.LBRAKET, 0); }
        public TerminalNode NUMERIC_LITERAL() { return getToken(BoosterParser.NUMERIC_LITERAL, 0); }
        public TerminalNode RBRAKET() { return getToken(BoosterParser.RBRAKET, 0); }
        public TerminalNode COLON() { return getToken(BoosterParser.COLON, 0); }
        public NodeContext node() {
            return getRuleContext(NodeContext.class,0);
        }
        public BoosterContext(ParserRuleContext parent, int invokingState) {
            super(parent, invokingState);
        }
        @Override public int getRuleIndex() { return RULE_booster; }
        @Override
        public void enterRule(ParseTreeListener listener) {
            if ( listener instanceof BoosterParserListener ) ((BoosterParserListener)listener).enterBooster(this);
        }
        @Override
        public void exitRule(ParseTreeListener listener) {
            if ( listener instanceof BoosterParserListener ) ((BoosterParserListener)listener).exitBooster(this);
        }
    }

    public final BoosterContext booster() throws RecognitionException {
        BoosterContext _localctx = new BoosterContext(_ctx, getState());
        enterRule(_localctx, 2, RULE_booster);
        try {
            enterOuterAlt(_localctx, 1);
            {
            setState(18);
            match(K_BOOSTER);
            setState(19);
            match(LBRAKET);
            setState(20);
            match(NUMERIC_LITERAL);
            setState(21);
            match(RBRAKET);
            setState(22);
            match(COLON);
            setState(23);
            node();
            }
        }
        catch (RecognitionException re) {
            _localctx.exception = re;
            _errHandler.reportError(this, re);
            _errHandler.recover(this, re);
        }
        finally {
            exitRule();
        }
        return _localctx;
    }

    public static class NodeContext extends ParserRuleContext {
        public Branch_nodeContext branch_node() {
            return getRuleContext(Branch_nodeContext.class,0);
        }
        public Leaf_nodeContext leaf_node() {
            return getRuleContext(Leaf_nodeContext.class,0);
        }
        public NodeContext(ParserRuleContext parent, int invokingState) {
            super(parent, invokingState);
        }
        @Override public int getRuleIndex() { return RULE_node; }
        @Override
        public void enterRule(ParseTreeListener listener) {
            if ( listener instanceof BoosterParserListener ) ((BoosterParserListener)listener).enterNode(this);
        }
        @Override
        public void exitRule(ParseTreeListener listener) {
            if ( listener instanceof BoosterParserListener ) ((BoosterParserListener)listener).exitNode(this);
        }
    }

    public final NodeContext node() throws RecognitionException {
        NodeContext _localctx = new NodeContext(_ctx, getState());
        enterRule(_localctx, 4, RULE_node);
        try {
            setState(27);
            _errHandler.sync(this);
            switch ( getInterpreter().adaptivePredict(_input,1,_ctx) ) {
            case 1:
                enterOuterAlt(_localctx, 1);
                {
                setState(25);
                branch_node();
                }
                break;
            case 2:
                enterOuterAlt(_localctx, 2);
                {
                setState(26);
                leaf_node();
                }
                break;
            }
        }
        catch (RecognitionException re) {
            _localctx.exception = re;
            _errHandler.reportError(this, re);
            _errHandler.recover(this, re);
        }
        finally {
            exitRule();
        }
        return _localctx;
    }

    public static class Branch_nodeContext extends ParserRuleContext {
        public List<Node_idContext> node_id() {
            return getRuleContexts(Node_idContext.class);
        }
        public Node_idContext node_id(int i) {
            return getRuleContext(Node_idContext.class,i);
        }
        public TerminalNode COLON() { return getToken(BoosterParser.COLON, 0); }
        public TerminalNode LBRAKET() { return getToken(BoosterParser.LBRAKET, 0); }
        public TerminalNode IDENTIFIER() { return getToken(BoosterParser.IDENTIFIER, 0); }
        public TerminalNode LT() { return getToken(BoosterParser.LT, 0); }
        public TerminalNode NUMERIC_LITERAL() { return getToken(BoosterParser.NUMERIC_LITERAL, 0); }
        public TerminalNode RBRAKET() { return getToken(BoosterParser.RBRAKET, 0); }
        public TerminalNode K_YES() { return getToken(BoosterParser.K_YES, 0); }
        public List<TerminalNode> ASSIGN() { return getTokens(BoosterParser.ASSIGN); }
        public TerminalNode ASSIGN(int i) {
            return getToken(BoosterParser.ASSIGN, i);
        }
        public List<TerminalNode> COMMA() { return getTokens(BoosterParser.COMMA); }
        public TerminalNode COMMA(int i) {
            return getToken(BoosterParser.COMMA, i);
        }
        public TerminalNode K_NO() { return getToken(BoosterParser.K_NO, 0); }
        public TerminalNode K_MISSING() { return getToken(BoosterParser.K_MISSING, 0); }
        public List<NodeContext> node() {
            return getRuleContexts(NodeContext.class);
        }
        public NodeContext node(int i) {
            return getRuleContext(NodeContext.class,i);
        }
        public Branch_nodeContext(ParserRuleContext parent, int invokingState) {
            super(parent, invokingState);
        }
        @Override public int getRuleIndex() { return RULE_branch_node; }
        @Override
        public void enterRule(ParseTreeListener listener) {
            if ( listener instanceof BoosterParserListener ) ((BoosterParserListener)listener).enterBranch_node(this);
        }
        @Override
        public void exitRule(ParseTreeListener listener) {
            if ( listener instanceof BoosterParserListener ) ((BoosterParserListener)listener).exitBranch_node(this);
        }
    }

    public final Branch_nodeContext branch_node() throws RecognitionException {
        Branch_nodeContext _localctx = new Branch_nodeContext(_ctx, getState());
        enterRule(_localctx, 6, RULE_branch_node);
        try {
            enterOuterAlt(_localctx, 1);
            {
            setState(29);
            node_id();
            setState(30);
            match(COLON);
            setState(31);
            match(LBRAKET);
            setState(32);
            match(IDENTIFIER);
            setState(33);
            match(LT);
            setState(34);
            match(NUMERIC_LITERAL);
            setState(35);
            match(RBRAKET);
            setState(36);
            match(K_YES);
            setState(37);
            match(ASSIGN);
            setState(38);
            node_id();
            setState(39);
            match(COMMA);
            setState(40);
            match(K_NO);
            setState(41);
            match(ASSIGN);
            setState(42);
            node_id();
            setState(43);
            match(COMMA);
            setState(44);
            match(K_MISSING);
            setState(45);
            match(ASSIGN);
            setState(46);
            node_id();
            setState(47);
            node();
            setState(48);
            node();
            }
        }
        catch (RecognitionException re) {
            _localctx.exception = re;
            _errHandler.reportError(this, re);
            _errHandler.recover(this, re);
        }
        finally {
            exitRule();
        }
        return _localctx;
    }

    public static class Node_idContext extends ParserRuleContext {
        public TerminalNode NUMERIC_LITERAL() { return getToken(BoosterParser.NUMERIC_LITERAL, 0); }
        public Node_idContext(ParserRuleContext parent, int invokingState) {
            super(parent, invokingState);
        }
        @Override public int getRuleIndex() { return RULE_node_id; }
        @Override
        public void enterRule(ParseTreeListener listener) {
            if ( listener instanceof BoosterParserListener ) ((BoosterParserListener)listener).enterNode_id(this);
        }
        @Override
        public void exitRule(ParseTreeListener listener) {
            if ( listener instanceof BoosterParserListener ) ((BoosterParserListener)listener).exitNode_id(this);
        }
    }

    public final Node_idContext node_id() throws RecognitionException {
        Node_idContext _localctx = new Node_idContext(_ctx, getState());
        enterRule(_localctx, 8, RULE_node_id);
        try {
            enterOuterAlt(_localctx, 1);
            {
            setState(50);
            match(NUMERIC_LITERAL);
            }
        }
        catch (RecognitionException re) {
            _localctx.exception = re;
            _errHandler.reportError(this, re);
            _errHandler.recover(this, re);
        }
        finally {
            exitRule();
        }
        return _localctx;
    }

    public static class Leaf_nodeContext extends ParserRuleContext {
        public Node_idContext node_id() {
            return getRuleContext(Node_idContext.class,0);
        }
        public TerminalNode COLON() { return getToken(BoosterParser.COLON, 0); }
        public TerminalNode K_LEAF() { return getToken(BoosterParser.K_LEAF, 0); }
        public TerminalNode ASSIGN() { return getToken(BoosterParser.ASSIGN, 0); }
        public TerminalNode NUMERIC_LITERAL() { return getToken(BoosterParser.NUMERIC_LITERAL, 0); }
        public Leaf_nodeContext(ParserRuleContext parent, int invokingState) {
            super(parent, invokingState);
        }
        @Override public int getRuleIndex() { return RULE_leaf_node; }
        @Override
        public void enterRule(ParseTreeListener listener) {
            if ( listener instanceof BoosterParserListener ) ((BoosterParserListener)listener).enterLeaf_node(this);
        }
        @Override
        public void exitRule(ParseTreeListener listener) {
            if ( listener instanceof BoosterParserListener ) ((BoosterParserListener)listener).exitLeaf_node(this);
        }
    }

    public final Leaf_nodeContext leaf_node() throws RecognitionException {
        Leaf_nodeContext _localctx = new Leaf_nodeContext(_ctx, getState());
        enterRule(_localctx, 10, RULE_leaf_node);
        try {
            enterOuterAlt(_localctx, 1);
            {
            setState(52);
            node_id();
            setState(53);
            match(COLON);
            setState(54);
            match(K_LEAF);
            setState(55);
            match(ASSIGN);
            setState(56);
            match(NUMERIC_LITERAL);
            }
        }
        catch (RecognitionException re) {
            _localctx.exception = re;
            _errHandler.reportError(this, re);
            _errHandler.recover(this, re);
        }
        finally {
            exitRule();
        }
        return _localctx;
    }

    public static final String _serializedATN =
        "\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\23=\4\2\t\2\4\3\t"+
        "\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\3\2\7\2\20\n\2\f\2\16\2\23\13\2\3\3"+
        "\3\3\3\3\3\3\3\3\3\3\3\3\3\4\3\4\5\4\36\n\4\3\5\3\5\3\5\3\5\3\5\3\5\3"+
        "\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\6\3\6\3\7"+
        "\3\7\3\7\3\7\3\7\3\7\3\7\2\2\b\2\4\6\b\n\f\2\2\28\2\21\3\2\2\2\4\24\3"+
        "\2\2\2\6\35\3\2\2\2\b\37\3\2\2\2\n\64\3\2\2\2\f\66\3\2\2\2\16\20\5\4\3"+
        "\2\17\16\3\2\2\2\20\23\3\2\2\2\21\17\3\2\2\2\21\22\3\2\2\2\22\3\3\2\2"+
        "\2\23\21\3\2\2\2\24\25\7\3\2\2\25\26\7\13\2\2\26\27\7\17\2\2\27\30\7\f"+
        "\2\2\30\31\7\b\2\2\31\32\5\6\4\2\32\5\3\2\2\2\33\36\5\b\5\2\34\36\5\f"+
        "\7\2\35\33\3\2\2\2\35\34\3\2\2\2\36\7\3\2\2\2\37 \5\n\6\2 !\7\b\2\2!\""+
        "\7\13\2\2\"#\7\16\2\2#$\7\r\2\2$%\7\17\2\2%&\7\f\2\2&\'\7\4\2\2\'(\7\n"+
        "\2\2()\5\n\6\2)*\7\t\2\2*+\7\5\2\2+,\7\n\2\2,-\5\n\6\2-.\7\t\2\2./\7\6"+
        "\2\2/\60\7\n\2\2\60\61\5\n\6\2\61\62\5\6\4\2\62\63\5\6\4\2\63\t\3\2\2"+
        "\2\64\65\7\17\2\2\65\13\3\2\2\2\66\67\5\n\6\2\678\7\b\2\289\7\7\2\29:"+
        "\7\n\2\2:;\7\17\2\2;\r\3\2\2\2\4\21\35";
    public static final ATN _ATN =
        new ATNDeserializer().deserialize(_serializedATN.toCharArray());
    static {
        _decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
        for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
            _decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
        }
    }
}
