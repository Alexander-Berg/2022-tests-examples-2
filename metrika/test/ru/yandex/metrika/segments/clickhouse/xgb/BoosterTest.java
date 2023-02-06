package ru.yandex.metrika.segments.clickhouse.xgb;

import java.nio.charset.Charset;

import org.antlr.v4.runtime.ANTLRInputStream;
import org.antlr.v4.runtime.BailErrorStrategy;
import org.antlr.v4.runtime.CommonTokenStream;
import org.antlr.v4.runtime.Parser;
import org.antlr.v4.runtime.RecognitionException;
import org.antlr.v4.runtime.tree.ParseTree;
import org.antlr.v4.runtime.tree.ParseTreeProperty;
import org.antlr.v4.runtime.tree.ParseTreeWalker;
import org.junit.Ignore;
import org.springframework.util.StreamUtils;

/**
 * Created by orantius on 13.04.17.
 */
@Ignore("METRIQA-936")
public class BoosterTest {


    private static Model parseStringWithANTLR(String arg) {
        ANTLRInputStream input = new ANTLRInputStream(arg);
        BoosterLexer lexer = new BoosterLexer(input);
        lexer.removeErrorListeners();
        CommonTokenStream tokens = new CommonTokenStream(lexer);
        BoosterParser parser = new BoosterParser(tokens);
        parser.removeErrorListeners();
        parser.setErrorHandler(new BailErrorStrategy() {
            @Override
            public void recover(Parser recognizer, RecognitionException e) {
                throw new RuntimeException(e.getMessage());
            }
        });
        ParseTree tree = parser.boosters();
        ParseTreeWalker walker = new ParseTreeWalker();
        BuilderModel listener = new BuilderModel();
        walker.walk(listener, tree);
        return listener.model;
    }


    static class BuilderModel extends BoosterParserBaseListener {
        Model model = new Model();
        ParseTreeProperty<Node> nodes = new ParseTreeProperty<>();

        @Override
        public void exitBooster(BoosterParser.BoosterContext ctx) {
            super.exitBooster(ctx);
            model.addTree(nodes.get(ctx.node()));
        }

        @Override
        public void exitNode(BoosterParser.NodeContext ctx) {
            super.exitNode(ctx);
            if (ctx.branch_node() != null) {
                nodes.put(ctx, nodes.get(ctx.branch_node()));
            }
            if (ctx.leaf_node() != null) {
                nodes.put(ctx, nodes.get(ctx.leaf_node()));
            }
        }

        @Override
        public void exitBranch_node(BoosterParser.Branch_nodeContext ctx) {
            super.exitBranch_node(ctx);
            nodes.put(ctx, new Branch(ctx.IDENTIFIER().getText(),
                    Double.parseDouble(ctx.NUMERIC_LITERAL().getText()),
                    nodes.get(ctx.node(0)),
                    nodes.get(ctx.node(1))));
        }

        @Override
        public void exitLeaf_node(BoosterParser.Leaf_nodeContext ctx) {
            super.exitLeaf_node(ctx);
            nodes.put(ctx, new Leaf(Double.parseDouble(ctx.NUMERIC_LITERAL().getText())));
        }
    }

    public static void main(String[] args) throws Exception {
        String text = StreamUtils.copyToString(BoosterTest.class.getResourceAsStream("example3.txt"), Charset.defaultCharset());
        Model model = parseStringWithANTLR(text);
        System.out.println("model = " + model);
    }

}
