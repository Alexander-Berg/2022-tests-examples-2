package ru.yandex.metrika.segments.clickhouse.g4;

import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

import org.antlr.v4.runtime.ANTLRInputStream;
import org.antlr.v4.runtime.CommonTokenStream;
import org.antlr.v4.runtime.tree.ParseTreeProperty;
import org.antlr.v4.runtime.tree.ParseTreeWalker;

import ru.yandex.metrika.segments.clickhouse.parse.ClickHouseParser;
import ru.yandex.metrika.util.collections.F;

/**
 * stateful
 * Created by orantius on 11/20/15.
 */
public class GrammarBuilder extends ANTLRv4ParserBaseListener {

    private final ParseTreeProperty<Element> elements = new ParseTreeProperty<>();
    private final ParseTreeProperty<ElementWithSuffix> elementWithSuffix = new ParseTreeProperty<>();
    private final ParseTreeProperty<Alternative> alternatives = new ParseTreeProperty<>();
    private final ParseTreeProperty<Rule> rules = new ParseTreeProperty<>();

    private final ANTLRv4Parser.GrammarSpecContext grammarSpec;

    private Grammar grammar;

    public GrammarBuilder(String path, Class<?> relClass) {
        ANTLRv4Lexer liteLexer = null;
        try {
            liteLexer = new ANTLRv4Lexer(new ANTLRInputStream(relClass.getResourceAsStream(path)));
        } catch (IOException ignore) {
        }
        //ANTLRv4Lexer liteLexer = new ANTLRv4Lexer(new ANTLRInputStream(ClickHouseParser.class.getResourceAsStream("test.g4")));
        CommonTokenStream tokens = new CommonTokenStream(liteLexer);
        ANTLRv4Parser parser = new ANTLRv4Parser(tokens);
        grammarSpec = parser.grammarSpec();
    }

    public Grammar build() {
        ParseTreeWalker ptw = new ParseTreeWalker();
        ptw.walk(this, grammarSpec);
        return grammar;
    }

    public static void main(String[] args) {
        GrammarBuilder gb = new GrammarBuilder("ClickHouseParser.g4", ClickHouseParser.class);
        Grammar grammar = gb.build();
        System.out.println( grammar);
    }

    @Override
    public void exitGrammarSpec(ANTLRv4Parser.GrammarSpecContext ctx) {
        List<ANTLRv4Parser.RuleSpecContext> rules = ctx.rules().ruleSpec();
        List<Rule> map = F.filter(F.map(rules, r -> this.rules.get(r)), r->r!=null);
        String grammarName = ctx.id().getText();
        grammar = new Grammar(grammarName, map);
        super.exitGrammarSpec(ctx);
    }

    @Override
    public void exitRuleSpec(ANTLRv4Parser.RuleSpecContext ctx) {
        if(ctx.parserRuleSpec()!=null) {
            rules.put(ctx, rules.get(ctx.parserRuleSpec()));
        }
        super.exitRuleSpec(ctx);
    }

    @Override
    public void exitParserRuleSpec(ANTLRv4Parser.ParserRuleSpecContext ctx) {
        String name = ctx.RULE_REF().getText();
        List<ANTLRv4Parser.LabeledAltContext> alts = ctx.ruleBlock().ruleAltList().labeledAlt();
        List<Alternative> map = F.map(alts, a -> alternatives.get(a));
        rules.put(ctx, new Rule(name, map));
        super.exitParserRuleSpec(ctx);
    }

    @Override
    public void exitLabeledAlt(ANTLRv4Parser.LabeledAltContext ctx) {
        Alternative alternative = alternatives.get(ctx.alternative());
        if(ctx.id()!=null) {
            String label;
            if(ctx.id().RULE_REF() !=null) {
                label = ctx.id().RULE_REF().getText();
            } else if (ctx.id().TOKEN_REF()!=null) {
                label = ctx.id().TOKEN_REF().getText();
            } else {
                throw new IllegalArgumentException("impossible id "+ctx.id());
            }
            alternative = new Alternative(label, alternative.getElements());
        }
        alternatives.put(ctx, alternative);
        super.exitLabeledAlt(ctx);
    }

    @Override
    public void exitAlternative(ANTLRv4Parser.AlternativeContext ctx) {
        List<ANTLRv4Parser.ElementContext> elems = ctx.element();
        if (elems != null) {
            alternatives.put(ctx, new Alternative(elems.stream().map(e->elementWithSuffix.get(e)).filter(e->e!=null).collect(Collectors.toList())));
        } else {
            alternatives.put(ctx, new Alternative(Collections.emptyList()));
        }
        super.exitAlternative(ctx);
    }

    @Override
    public void exitElement(ANTLRv4Parser.ElementContext ctx) {
        Operator operator = null;
        Element element = null;
        if (ctx.atom() != null) {
            element = elements.get(ctx.atom());
            operator = getOperator(ctx.ebnfSuffix());
        } else if (ctx.ebnf() != null) {
            element = elements.get(ctx.ebnf().block());
            if(ctx.ebnf().blockSuffix()!=null) {
                operator = getOperator(ctx.ebnf().blockSuffix().ebnfSuffix());
            }
        } else if(ctx.ACTION() != null) {
            // ignore action in elements.
        } else {
            // TODO labelled element
            throw new IllegalStateException("unsupported alternative in Element " + ctx.getText());
        }
        if (element!=null) {
            elementWithSuffix.put(ctx, new ElementWithSuffix(element, operator));
        }
        super.exitElement(ctx);
    }

    @Override
    public void exitAtomRuleRef(ANTLRv4Parser.AtomRuleRefContext ctx) {
        elements.put(ctx, new RuleRef(ctx.ruleref().RULE_REF().getText()));
        super.exitAtomRuleRef(ctx);
    }

    @Override
    public void exitAtomTerminal(ANTLRv4Parser.AtomTerminalContext ctx) {
        elements.put(ctx, new Token(ctx.terminal().TOKEN_REF().getText()));
        super.exitAtomTerminal(ctx);
    }

    @Override
    public void exitBlock(ANTLRv4Parser.BlockContext ctx) {
        List<ANTLRv4Parser.AlternativeContext> alts = ctx.altList().alternative();
        if (alts != null) {
            Block block = new Block(F.map(alts, a -> alternatives.get(a)));
            elements.put(ctx, block);
        } else {
            elements.put(ctx, new Block(Collections.emptyList()));
        }
        super.exitBlock(ctx);
    }

    private static Operator getOperator(ANTLRv4Parser.EbnfSuffixContext ctx) {
        if (ctx != null) {
            if (ctx.PLUS() != null) {
                return Operator.PLUS;
            } else if (ctx.STAR() != null) {
                return Operator.STAR;
            } else if (ctx.QUESTION() != null && !ctx.QUESTION().isEmpty()) {
                return Operator.QUESTION;
            } else {
                throw new IllegalArgumentException(ctx.getText());
            }
        }
        return null;
    }

}
