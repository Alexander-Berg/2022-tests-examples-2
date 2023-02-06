// Generated from /home/orantius/dev/projects/metrika/metrika-api/segments/src/test/ru/yandex/metrika/segments/clickhouse/xgb/BoosterLexer.g4 by ANTLR 4.7
package ru.yandex.metrika.segments.clickhouse.xgb;

import org.antlr.v4.runtime.CharStream;
import org.antlr.v4.runtime.Lexer;
import org.antlr.v4.runtime.RuntimeMetaData;
import org.antlr.v4.runtime.Vocabulary;
import org.antlr.v4.runtime.VocabularyImpl;
import org.antlr.v4.runtime.atn.ATN;
import org.antlr.v4.runtime.atn.ATNDeserializer;
import org.antlr.v4.runtime.atn.LexerATNSimulator;
import org.antlr.v4.runtime.atn.PredictionContextCache;
import org.antlr.v4.runtime.dfa.DFA;

@SuppressWarnings({"all", "warnings", "unchecked", "unused", "cast"})
public class BoosterLexer extends Lexer {
    static { RuntimeMetaData.checkVersion("4.7", RuntimeMetaData.VERSION); }

    protected static final DFA[] _decisionToDFA;
    protected static final PredictionContextCache _sharedContextCache =
        new PredictionContextCache();
    public static final int
        K_BOOSTER=1, K_YES=2, K_NO=3, K_MISSING=4, K_LEAF=5, COLON=6, COMMA=7,
        ASSIGN=8, LBRAKET=9, RBRAKET=10, LT=11, IDENTIFIER=12, NUMERIC_LITERAL=13,
        STRING_LITERAL=14, QUOTED_LITERAL=15, SPACES=16, UNEXPECTED_CHAR=17;
    public static String[] channelNames = {
        "DEFAULT_TOKEN_CHANNEL", "HIDDEN"
    };

    public static String[] modeNames = {
        "DEFAULT_MODE"
    };

    public static final String[] ruleNames = {
        "K_BOOSTER", "K_YES", "K_NO", "K_MISSING", "K_LEAF", "COLON", "COMMA",
        "ASSIGN", "LBRAKET", "RBRAKET", "LT", "IDENTIFIER", "NUMERIC_LITERAL",
        "STRING_LITERAL", "QUOTED_LITERAL", "SPACES", "UNEXPECTED_CHAR", "DIGIT",
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N",
        "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"
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


    public BoosterLexer(CharStream input) {
        super(input);
        _interp = new LexerATNSimulator(this,_ATN,_decisionToDFA,_sharedContextCache);
    }

    @Override
    public String getGrammarFileName() { return "BoosterLexer.g4"; }

    @Override
    public String[] getRuleNames() { return ruleNames; }

    @Override
    public String getSerializedATN() { return _serializedATN; }

    @Override
    public String[] getChannelNames() { return channelNames; }

    @Override
    public String[] getModeNames() { return modeNames; }

    @Override
    public ATN getATN() { return _ATN; }

    public static final String _serializedATN =
        "\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\23\u0109\b\1\4\2"+
        "\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4"+
        "\13\t\13\4\f\t\f\4\r\t\r\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22"+
        "\t\22\4\23\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4\30\t\30\4\31"+
        "\t\31\4\32\t\32\4\33\t\33\4\34\t\34\4\35\t\35\4\36\t\36\4\37\t\37\4 \t"+
        " \4!\t!\4\"\t\"\4#\t#\4$\t$\4%\t%\4&\t&\4\'\t\'\4(\t(\4)\t)\4*\t*\4+\t"+
        "+\4,\t,\4-\t-\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\3\3\3\3\3\3\3\3\4\3\4"+
        "\3\4\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\6\3\6\3\6\3\6\3\6\3\7\3\7\3\b\3"+
        "\b\3\t\3\t\3\n\3\n\3\13\3\13\3\f\3\f\3\r\3\r\7\r\u0086\n\r\f\r\16\r\u0089"+
        "\13\r\3\16\5\16\u008c\n\16\3\16\6\16\u008f\n\16\r\16\16\16\u0090\3\16"+
        "\3\16\7\16\u0095\n\16\f\16\16\16\u0098\13\16\5\16\u009a\n\16\3\16\3\16"+
        "\5\16\u009e\n\16\3\16\6\16\u00a1\n\16\r\16\16\16\u00a2\5\16\u00a5\n\16"+
        "\3\16\3\16\6\16\u00a9\n\16\r\16\16\16\u00aa\3\16\3\16\5\16\u00af\n\16"+
        "\3\16\6\16\u00b2\n\16\r\16\16\16\u00b3\5\16\u00b6\n\16\5\16\u00b8\n\16"+
        "\3\17\3\17\3\17\3\17\7\17\u00be\n\17\f\17\16\17\u00c1\13\17\3\17\3\17"+
        "\3\20\3\20\7\20\u00c7\n\20\f\20\16\20\u00ca\13\20\3\20\3\20\3\21\3\21"+
        "\3\21\3\21\3\22\3\22\3\23\3\23\3\24\3\24\3\25\3\25\3\26\3\26\3\27\3\27"+
        "\3\30\3\30\3\31\3\31\3\32\3\32\3\33\3\33\3\34\3\34\3\35\3\35\3\36\3\36"+
        "\3\37\3\37\3 \3 \3!\3!\3\"\3\"\3#\3#\3$\3$\3%\3%\3&\3&\3\'\3\'\3(\3(\3"+
        ")\3)\3*\3*\3+\3+\3,\3,\3-\3-\2\2.\3\3\5\4\7\5\t\6\13\7\r\b\17\t\21\n\23"+
        "\13\25\f\27\r\31\16\33\17\35\20\37\21!\22#\23%\2\'\2)\2+\2-\2/\2\61\2"+
        "\63\2\65\2\67\29\2;\2=\2?\2A\2C\2E\2G\2I\2K\2M\2O\2Q\2S\2U\2W\2Y\2\3\2"+
        "#\5\2C\\aac|\6\2\62;C\\aac|\4\2--//\3\2))\3\2bb\5\2\13\r\17\17\"\"\3\2"+
        "\62;\4\2CCcc\4\2DDdd\4\2EEee\4\2FFff\4\2GGgg\4\2HHhh\4\2IIii\4\2JJjj\4"+
        "\2KKkk\4\2LLll\4\2MMmm\4\2NNnn\4\2OOoo\4\2PPpp\4\2QQqq\4\2RRrr\4\2SSs"+
        "s\4\2TTtt\4\2UUuu\4\2VVvv\4\2WWww\4\2XXxx\4\2YYyy\4\2ZZzz\4\2[[{{\4\2"+
        "\\\\||\2\u00fd\2\3\3\2\2\2\2\5\3\2\2\2\2\7\3\2\2\2\2\t\3\2\2\2\2\13\3"+
        "\2\2\2\2\r\3\2\2\2\2\17\3\2\2\2\2\21\3\2\2\2\2\23\3\2\2\2\2\25\3\2\2\2"+
        "\2\27\3\2\2\2\2\31\3\2\2\2\2\33\3\2\2\2\2\35\3\2\2\2\2\37\3\2\2\2\2!\3"+
        "\2\2\2\2#\3\2\2\2\3[\3\2\2\2\5c\3\2\2\2\7g\3\2\2\2\tj\3\2\2\2\13r\3\2"+
        "\2\2\rw\3\2\2\2\17y\3\2\2\2\21{\3\2\2\2\23}\3\2\2\2\25\177\3\2\2\2\27"+
        "\u0081\3\2\2\2\31\u0083\3\2\2\2\33\u00b7\3\2\2\2\35\u00b9\3\2\2\2\37\u00c4"+
        "\3\2\2\2!\u00cd\3\2\2\2#\u00d1\3\2\2\2%\u00d3\3\2\2\2\'\u00d5\3\2\2\2"+
        ")\u00d7\3\2\2\2+\u00d9\3\2\2\2-\u00db\3\2\2\2/\u00dd\3\2\2\2\61\u00df"+
        "\3\2\2\2\63\u00e1\3\2\2\2\65\u00e3\3\2\2\2\67\u00e5\3\2\2\29\u00e7\3\2"+
        "\2\2;\u00e9\3\2\2\2=\u00eb\3\2\2\2?\u00ed\3\2\2\2A\u00ef\3\2\2\2C\u00f1"+
        "\3\2\2\2E\u00f3\3\2\2\2G\u00f5\3\2\2\2I\u00f7\3\2\2\2K\u00f9\3\2\2\2M"+
        "\u00fb\3\2\2\2O\u00fd\3\2\2\2Q\u00ff\3\2\2\2S\u0101\3\2\2\2U\u0103\3\2"+
        "\2\2W\u0105\3\2\2\2Y\u0107\3\2\2\2[\\\7d\2\2\\]\7q\2\2]^\7q\2\2^_\7u\2"+
        "\2_`\7v\2\2`a\7g\2\2ab\7t\2\2b\4\3\2\2\2cd\7{\2\2de\7g\2\2ef\7u\2\2f\6"+
        "\3\2\2\2gh\7p\2\2hi\7q\2\2i\b\3\2\2\2jk\7o\2\2kl\7k\2\2lm\7u\2\2mn\7u"+
        "\2\2no\7k\2\2op\7p\2\2pq\7i\2\2q\n\3\2\2\2rs\7n\2\2st\7g\2\2tu\7c\2\2"+
        "uv\7h\2\2v\f\3\2\2\2wx\7<\2\2x\16\3\2\2\2yz\7.\2\2z\20\3\2\2\2{|\7?\2"+
        "\2|\22\3\2\2\2}~\7]\2\2~\24\3\2\2\2\177\u0080\7_\2\2\u0080\26\3\2\2\2"+
        "\u0081\u0082\7>\2\2\u0082\30\3\2\2\2\u0083\u0087\t\2\2\2\u0084\u0086\t"+
        "\3\2\2\u0085\u0084\3\2\2\2\u0086\u0089\3\2\2\2\u0087\u0085\3\2\2\2\u0087"+
        "\u0088\3\2\2\2\u0088\32\3\2\2\2\u0089\u0087\3\2\2\2\u008a\u008c\7/\2\2"+
        "\u008b\u008a\3\2\2\2\u008b\u008c\3\2\2\2\u008c\u008e\3\2\2\2\u008d\u008f"+
        "\5%\23\2\u008e\u008d\3\2\2\2\u008f\u0090\3\2\2\2\u0090\u008e\3\2\2\2\u0090"+
        "\u0091\3\2\2\2\u0091\u0099\3\2\2\2\u0092\u0096\7\60\2\2\u0093\u0095\5"+
        "%\23\2\u0094\u0093\3\2\2\2\u0095\u0098\3\2\2\2\u0096\u0094\3\2\2\2\u0096"+
        "\u0097\3\2\2\2\u0097\u009a\3\2\2\2\u0098\u0096\3\2\2\2\u0099\u0092\3\2"+
        "\2\2\u0099\u009a\3\2\2\2\u009a\u00a4\3\2\2\2\u009b\u009d\5/\30\2\u009c"+
        "\u009e\t\4\2\2\u009d\u009c\3\2\2\2\u009d\u009e\3\2\2\2\u009e\u00a0\3\2"+
        "\2\2\u009f\u00a1\5%\23\2\u00a0\u009f\3\2\2\2\u00a1\u00a2\3\2\2\2\u00a2"+
        "\u00a0\3\2\2\2\u00a2\u00a3\3\2\2\2\u00a3\u00a5\3\2\2\2\u00a4\u009b\3\2"+
        "\2\2\u00a4\u00a5\3\2\2\2\u00a5\u00b8\3\2\2\2\u00a6\u00a8\7\60\2\2\u00a7"+
        "\u00a9\5%\23\2\u00a8\u00a7\3\2\2\2\u00a9\u00aa\3\2\2\2\u00aa\u00a8\3\2"+
        "\2\2\u00aa\u00ab\3\2\2\2\u00ab\u00b5\3\2\2\2\u00ac\u00ae\5/\30\2\u00ad"+
        "\u00af\t\4\2\2\u00ae\u00ad\3\2\2\2\u00ae\u00af\3\2\2\2\u00af\u00b1\3\2"+
        "\2\2\u00b0\u00b2\5%\23\2\u00b1\u00b0\3\2\2\2\u00b2\u00b3\3\2\2\2\u00b3"+
        "\u00b1\3\2\2\2\u00b3\u00b4\3\2\2\2\u00b4\u00b6\3\2\2\2\u00b5\u00ac\3\2"+
        "\2\2\u00b5\u00b6\3\2\2\2\u00b6\u00b8\3\2\2\2\u00b7\u008b\3\2\2\2\u00b7"+
        "\u00a6\3\2\2\2\u00b8\34\3\2\2\2\u00b9\u00bf\7)\2\2\u00ba\u00be\n\5\2\2"+
        "\u00bb\u00bc\7^\2\2\u00bc\u00be\7)\2\2\u00bd\u00ba\3\2\2\2\u00bd\u00bb"+
        "\3\2\2\2\u00be\u00c1\3\2\2\2\u00bf\u00bd\3\2\2\2\u00bf\u00c0\3\2\2\2\u00c0"+
        "\u00c2\3\2\2\2\u00c1\u00bf\3\2\2\2\u00c2\u00c3\7)\2\2\u00c3\36\3\2\2\2"+
        "\u00c4\u00c8\7b\2\2\u00c5\u00c7\n\6\2\2\u00c6\u00c5\3\2\2\2\u00c7\u00ca"+
        "\3\2\2\2\u00c8\u00c6\3\2\2\2\u00c8\u00c9\3\2\2\2\u00c9\u00cb\3\2\2\2\u00ca"+
        "\u00c8\3\2\2\2\u00cb\u00cc\7b\2\2\u00cc \3\2\2\2\u00cd\u00ce\t\7\2\2\u00ce"+
        "\u00cf\3\2\2\2\u00cf\u00d0\b\21\2\2\u00d0\"\3\2\2\2\u00d1\u00d2\13\2\2"+
        "\2\u00d2$\3\2\2\2\u00d3\u00d4\t\b\2\2\u00d4&\3\2\2\2\u00d5\u00d6\t\t\2"+
        "\2\u00d6(\3\2\2\2\u00d7\u00d8\t\n\2\2\u00d8*\3\2\2\2\u00d9\u00da\t\13"+
        "\2\2\u00da,\3\2\2\2\u00db\u00dc\t\f\2\2\u00dc.\3\2\2\2\u00dd\u00de\t\r"+
        "\2\2\u00de\60\3\2\2\2\u00df\u00e0\t\16\2\2\u00e0\62\3\2\2\2\u00e1\u00e2"+
        "\t\17\2\2\u00e2\64\3\2\2\2\u00e3\u00e4\t\20\2\2\u00e4\66\3\2\2\2\u00e5"+
        "\u00e6\t\21\2\2\u00e68\3\2\2\2\u00e7\u00e8\t\22\2\2\u00e8:\3\2\2\2\u00e9"+
        "\u00ea\t\23\2\2\u00ea<\3\2\2\2\u00eb\u00ec\t\24\2\2\u00ec>\3\2\2\2\u00ed"+
        "\u00ee\t\25\2\2\u00ee@\3\2\2\2\u00ef\u00f0\t\26\2\2\u00f0B\3\2\2\2\u00f1"+
        "\u00f2\t\27\2\2\u00f2D\3\2\2\2\u00f3\u00f4\t\30\2\2\u00f4F\3\2\2\2\u00f5"+
        "\u00f6\t\31\2\2\u00f6H\3\2\2\2\u00f7\u00f8\t\32\2\2\u00f8J\3\2\2\2\u00f9"+
        "\u00fa\t\33\2\2\u00faL\3\2\2\2\u00fb\u00fc\t\34\2\2\u00fcN\3\2\2\2\u00fd"+
        "\u00fe\t\35\2\2\u00feP\3\2\2\2\u00ff\u0100\t\36\2\2\u0100R\3\2\2\2\u0101"+
        "\u0102\t\37\2\2\u0102T\3\2\2\2\u0103\u0104\t \2\2\u0104V\3\2\2\2\u0105"+
        "\u0106\t!\2\2\u0106X\3\2\2\2\u0107\u0108\t\"\2\2\u0108Z\3\2\2\2\23\2\u0087"+
        "\u008b\u0090\u0096\u0099\u009d\u00a2\u00a4\u00aa\u00ae\u00b3\u00b5\u00b7"+
        "\u00bd\u00bf\u00c8\3\2\3\2";
    public static final ATN _ATN =
        new ATNDeserializer().deserialize(_serializedATN.toCharArray());
    static {
        _decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
        for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
            _decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
        }
    }
}
