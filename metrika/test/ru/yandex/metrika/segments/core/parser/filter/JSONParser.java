// Generated from /home/orantius/dev/projects/metrika/metrika-api/segments/src/test/ru/yandex/metrika/segments/core/parser/filter/JSON.g4 by ANTLR 4.5.1
package ru.yandex.metrika.segments.core.parser.filter;

import java.util.List;

import org.antlr.v4.runtime.NoViableAltException;
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
public class JSONParser extends Parser {
    static { RuntimeMetaData.checkVersion("4.5.1", RuntimeMetaData.VERSION); }

    protected static final DFA[] _decisionToDFA;
    protected static final PredictionContextCache _sharedContextCache =
        new PredictionContextCache();
    public static final int
        COMMA=1, COLON=2, LBRA=3, RBRA=4, LCUR=5, RCUR=6, TRUE=7, FALSE=8, NULL=9,
        STRING=10, NUMBER=11, WS=12;
    public static final int
        RULE_json = 0, RULE_object = 1, RULE_pair = 2, RULE_key = 3, RULE_array = 4,
        RULE_value = 5;
    public static final String[] ruleNames = {
        "json", "object", "pair", "key", "array", "value"
    };

    private static final String[] _LITERAL_NAMES = {
        null, "','", "':'", "'['", "']'", "'{'", "'}'", "'true'", "'false'", "'null'"
    };
    private static final String[] _SYMBOLIC_NAMES = {
        null, "COMMA", "COLON", "LBRA", "RBRA", "LCUR", "RCUR", "TRUE", "FALSE",
        "NULL", "STRING", "NUMBER", "WS"
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
    public String getGrammarFileName() { return "JSON.g4"; }

    @Override
    public String[] getRuleNames() { return ruleNames; }

    @Override
    public String getSerializedATN() { return _serializedATN; }

    @Override
    public ATN getATN() { return _ATN; }

    public JSONParser(TokenStream input) {
        super(input);
        _interp = new ParserATNSimulator(this,_ATN,_decisionToDFA,_sharedContextCache);
    }
    public static class JsonContext extends ParserRuleContext {
        public ValueContext value() {
            return getRuleContext(ValueContext.class,0);
        }
        public JsonContext(ParserRuleContext parent, int invokingState) {
            super(parent, invokingState);
        }
        @Override public int getRuleIndex() { return RULE_json; }
        @Override
        public void enterRule(ParseTreeListener listener) {
            if ( listener instanceof JSONListener ) ((JSONListener)listener).enterJson(this);
        }
        @Override
        public void exitRule(ParseTreeListener listener) {
            if ( listener instanceof JSONListener ) ((JSONListener)listener).exitJson(this);
        }
    }

    public final JsonContext json() throws RecognitionException {
        JsonContext _localctx = new JsonContext(_ctx, getState());
        enterRule(_localctx, 0, RULE_json);
        try {
            enterOuterAlt(_localctx, 1);
            {
            setState(12);
            value();
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

    public static class ObjectContext extends ParserRuleContext {
        public TerminalNode LCUR() { return getToken(JSONParser.LCUR, 0); }
        public List<PairContext> pair() {
            return getRuleContexts(PairContext.class);
        }
        public PairContext pair(int i) {
            return getRuleContext(PairContext.class,i);
        }
        public TerminalNode RCUR() { return getToken(JSONParser.RCUR, 0); }
        public List<TerminalNode> COMMA() { return getTokens(JSONParser.COMMA); }
        public TerminalNode COMMA(int i) {
            return getToken(JSONParser.COMMA, i);
        }
        public ObjectContext(ParserRuleContext parent, int invokingState) {
            super(parent, invokingState);
        }
        @Override public int getRuleIndex() { return RULE_object; }
        @Override
        public void enterRule(ParseTreeListener listener) {
            if ( listener instanceof JSONListener ) ((JSONListener)listener).enterObject(this);
        }
        @Override
        public void exitRule(ParseTreeListener listener) {
            if ( listener instanceof JSONListener ) ((JSONListener)listener).exitObject(this);
        }
    }

    public final ObjectContext object() throws RecognitionException {
        ObjectContext _localctx = new ObjectContext(_ctx, getState());
        enterRule(_localctx, 2, RULE_object);
        int _la;
        try {
            setState(27);
            switch ( getInterpreter().adaptivePredict(_input,1,_ctx) ) {
            case 1:
                enterOuterAlt(_localctx, 1);
                {
                setState(14);
                match(LCUR);
                setState(15);
                pair();
                setState(20);
                _errHandler.sync(this);
                _la = _input.LA(1);
                while (_la==COMMA) {
                    {
                    {
                    setState(16);
                    match(COMMA);
                    setState(17);
                    pair();
                    }
                    }
                    setState(22);
                    _errHandler.sync(this);
                    _la = _input.LA(1);
                }
                setState(23);
                match(RCUR);
                }
                break;
            case 2:
                enterOuterAlt(_localctx, 2);
                {
                setState(25);
                match(LCUR);
                setState(26);
                match(RCUR);
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

    public static class PairContext extends ParserRuleContext {
        public KeyContext key() {
            return getRuleContext(KeyContext.class,0);
        }
        public TerminalNode COLON() { return getToken(JSONParser.COLON, 0); }
        public ValueContext value() {
            return getRuleContext(ValueContext.class,0);
        }
        public PairContext(ParserRuleContext parent, int invokingState) {
            super(parent, invokingState);
        }
        @Override public int getRuleIndex() { return RULE_pair; }
        @Override
        public void enterRule(ParseTreeListener listener) {
            if ( listener instanceof JSONListener ) ((JSONListener)listener).enterPair(this);
        }
        @Override
        public void exitRule(ParseTreeListener listener) {
            if ( listener instanceof JSONListener ) ((JSONListener)listener).exitPair(this);
        }
    }

    public final PairContext pair() throws RecognitionException {
        PairContext _localctx = new PairContext(_ctx, getState());
        enterRule(_localctx, 4, RULE_pair);
        try {
            enterOuterAlt(_localctx, 1);
            {
            setState(29);
            key();
            setState(30);
            match(COLON);
            setState(31);
            value();
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

    public static class KeyContext extends ParserRuleContext {
        public TerminalNode STRING() { return getToken(JSONParser.STRING, 0); }
        public KeyContext(ParserRuleContext parent, int invokingState) {
            super(parent, invokingState);
        }
        @Override public int getRuleIndex() { return RULE_key; }
        @Override
        public void enterRule(ParseTreeListener listener) {
            if ( listener instanceof JSONListener ) ((JSONListener)listener).enterKey(this);
        }
        @Override
        public void exitRule(ParseTreeListener listener) {
            if ( listener instanceof JSONListener ) ((JSONListener)listener).exitKey(this);
        }
    }

    public final KeyContext key() throws RecognitionException {
        KeyContext _localctx = new KeyContext(_ctx, getState());
        enterRule(_localctx, 6, RULE_key);
        try {
            enterOuterAlt(_localctx, 1);
            {
            setState(33);
            match(STRING);
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

    public static class ArrayContext extends ParserRuleContext {
        public TerminalNode LBRA() { return getToken(JSONParser.LBRA, 0); }
        public List<ValueContext> value() {
            return getRuleContexts(ValueContext.class);
        }
        public ValueContext value(int i) {
            return getRuleContext(ValueContext.class,i);
        }
        public TerminalNode RBRA() { return getToken(JSONParser.RBRA, 0); }
        public List<TerminalNode> COMMA() { return getTokens(JSONParser.COMMA); }
        public TerminalNode COMMA(int i) {
            return getToken(JSONParser.COMMA, i);
        }
        public ArrayContext(ParserRuleContext parent, int invokingState) {
            super(parent, invokingState);
        }
        @Override public int getRuleIndex() { return RULE_array; }
        @Override
        public void enterRule(ParseTreeListener listener) {
            if ( listener instanceof JSONListener ) ((JSONListener)listener).enterArray(this);
        }
        @Override
        public void exitRule(ParseTreeListener listener) {
            if ( listener instanceof JSONListener ) ((JSONListener)listener).exitArray(this);
        }
    }

    public final ArrayContext array() throws RecognitionException {
        ArrayContext _localctx = new ArrayContext(_ctx, getState());
        enterRule(_localctx, 8, RULE_array);
        int _la;
        try {
            setState(48);
            switch ( getInterpreter().adaptivePredict(_input,3,_ctx) ) {
            case 1:
                enterOuterAlt(_localctx, 1);
                {
                setState(35);
                match(LBRA);
                setState(36);
                value();
                setState(41);
                _errHandler.sync(this);
                _la = _input.LA(1);
                while (_la==COMMA) {
                    {
                    {
                    setState(37);
                    match(COMMA);
                    setState(38);
                    value();
                    }
                    }
                    setState(43);
                    _errHandler.sync(this);
                    _la = _input.LA(1);
                }
                setState(44);
                match(RBRA);
                }
                break;
            case 2:
                enterOuterAlt(_localctx, 2);
                {
                setState(46);
                match(LBRA);
                setState(47);
                match(RBRA);
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

    public static class ValueContext extends ParserRuleContext {
        public TerminalNode STRING() { return getToken(JSONParser.STRING, 0); }
        public TerminalNode NUMBER() { return getToken(JSONParser.NUMBER, 0); }
        public ObjectContext object() {
            return getRuleContext(ObjectContext.class,0);
        }
        public ArrayContext array() {
            return getRuleContext(ArrayContext.class,0);
        }
        public TerminalNode TRUE() { return getToken(JSONParser.TRUE, 0); }
        public TerminalNode FALSE() { return getToken(JSONParser.FALSE, 0); }
        public TerminalNode NULL() { return getToken(JSONParser.NULL, 0); }
        public ValueContext(ParserRuleContext parent, int invokingState) {
            super(parent, invokingState);
        }
        @Override public int getRuleIndex() { return RULE_value; }
        @Override
        public void enterRule(ParseTreeListener listener) {
            if ( listener instanceof JSONListener ) ((JSONListener)listener).enterValue(this);
        }
        @Override
        public void exitRule(ParseTreeListener listener) {
            if ( listener instanceof JSONListener ) ((JSONListener)listener).exitValue(this);
        }
    }

    public final ValueContext value() throws RecognitionException {
        ValueContext _localctx = new ValueContext(_ctx, getState());
        enterRule(_localctx, 10, RULE_value);
        try {
            setState(57);
            switch (_input.LA(1)) {
            case STRING:
                enterOuterAlt(_localctx, 1);
                {
                setState(50);
                match(STRING);
                }
                break;
            case NUMBER:
                enterOuterAlt(_localctx, 2);
                {
                setState(51);
                match(NUMBER);
                }
                break;
            case LCUR:
                enterOuterAlt(_localctx, 3);
                {
                setState(52);
                object();
                }
                break;
            case LBRA:
                enterOuterAlt(_localctx, 4);
                {
                setState(53);
                array();
                }
                break;
            case TRUE:
                enterOuterAlt(_localctx, 5);
                {
                setState(54);
                match(TRUE);
                }
                break;
            case FALSE:
                enterOuterAlt(_localctx, 6);
                {
                setState(55);
                match(FALSE);
                }
                break;
            case NULL:
                enterOuterAlt(_localctx, 7);
                {
                setState(56);
                match(NULL);
                }
                break;
            default:
                throw new NoViableAltException(this);
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
        "\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\3\16>\4\2\t\2\4\3\t"+
        "\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\3\2\3\2\3\3\3\3\3\3\3\3\7\3\25\n\3"+
        "\f\3\16\3\30\13\3\3\3\3\3\3\3\3\3\5\3\36\n\3\3\4\3\4\3\4\3\4\3\5\3\5\3"+
        "\6\3\6\3\6\3\6\7\6*\n\6\f\6\16\6-\13\6\3\6\3\6\3\6\3\6\5\6\63\n\6\3\7"+
        "\3\7\3\7\3\7\3\7\3\7\3\7\5\7<\n\7\3\7\2\2\b\2\4\6\b\n\f\2\2A\2\16\3\2"+
        "\2\2\4\35\3\2\2\2\6\37\3\2\2\2\b#\3\2\2\2\n\62\3\2\2\2\f;\3\2\2\2\16\17"+
        "\5\f\7\2\17\3\3\2\2\2\20\21\7\7\2\2\21\26\5\6\4\2\22\23\7\3\2\2\23\25"+
        "\5\6\4\2\24\22\3\2\2\2\25\30\3\2\2\2\26\24\3\2\2\2\26\27\3\2\2\2\27\31"+
        "\3\2\2\2\30\26\3\2\2\2\31\32\7\b\2\2\32\36\3\2\2\2\33\34\7\7\2\2\34\36"+
        "\7\b\2\2\35\20\3\2\2\2\35\33\3\2\2\2\36\5\3\2\2\2\37 \5\b\5\2 !\7\4\2"+
        "\2!\"\5\f\7\2\"\7\3\2\2\2#$\7\f\2\2$\t\3\2\2\2%&\7\5\2\2&+\5\f\7\2\'("+
        "\7\3\2\2(*\5\f\7\2)\'\3\2\2\2*-\3\2\2\2+)\3\2\2\2+,\3\2\2\2,.\3\2\2\2"+
        "-+\3\2\2\2./\7\6\2\2/\63\3\2\2\2\60\61\7\5\2\2\61\63\7\6\2\2\62%\3\2\2"+
        "\2\62\60\3\2\2\2\63\13\3\2\2\2\64<\7\f\2\2\65<\7\r\2\2\66<\5\4\3\2\67"+
        "<\5\n\6\28<\7\t\2\29<\7\n\2\2:<\7\13\2\2;\64\3\2\2\2;\65\3\2\2\2;\66\3"+
        "\2\2\2;\67\3\2\2\2;8\3\2\2\2;9\3\2\2\2;:\3\2\2\2<\r\3\2\2\2\7\26\35+\62"+
        ";";
    public static final ATN _ATN =
        new ATNDeserializer().deserialize(_serializedATN.toCharArray());
    static {
        _decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
        for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
            _decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
        }
    }
}
