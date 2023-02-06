// Generated from /home/orantius/dev/projects/metrika/metrika-api/segments/src/test/ru/yandex/metrika/segments/clickhouse/xgb/BoosterParser.g4 by ANTLR 4.7
package ru.yandex.metrika.segments.clickhouse.xgb;
import org.antlr.v4.runtime.tree.ParseTreeListener;

/**
 * This interface defines a complete listener for a parse tree produced by
 * {@link BoosterParser}.
 */
public interface BoosterParserListener extends ParseTreeListener {
    /**
     * Enter a parse tree produced by {@link BoosterParser#boosters}.
     * @param ctx the parse tree
     */
    void enterBoosters(BoosterParser.BoostersContext ctx);
    /**
     * Exit a parse tree produced by {@link BoosterParser#boosters}.
     * @param ctx the parse tree
     */
    void exitBoosters(BoosterParser.BoostersContext ctx);
    /**
     * Enter a parse tree produced by {@link BoosterParser#booster}.
     * @param ctx the parse tree
     */
    void enterBooster(BoosterParser.BoosterContext ctx);
    /**
     * Exit a parse tree produced by {@link BoosterParser#booster}.
     * @param ctx the parse tree
     */
    void exitBooster(BoosterParser.BoosterContext ctx);
    /**
     * Enter a parse tree produced by {@link BoosterParser#node}.
     * @param ctx the parse tree
     */
    void enterNode(BoosterParser.NodeContext ctx);
    /**
     * Exit a parse tree produced by {@link BoosterParser#node}.
     * @param ctx the parse tree
     */
    void exitNode(BoosterParser.NodeContext ctx);
    /**
     * Enter a parse tree produced by {@link BoosterParser#branch_node}.
     * @param ctx the parse tree
     */
    void enterBranch_node(BoosterParser.Branch_nodeContext ctx);
    /**
     * Exit a parse tree produced by {@link BoosterParser#branch_node}.
     * @param ctx the parse tree
     */
    void exitBranch_node(BoosterParser.Branch_nodeContext ctx);
    /**
     * Enter a parse tree produced by {@link BoosterParser#node_id}.
     * @param ctx the parse tree
     */
    void enterNode_id(BoosterParser.Node_idContext ctx);
    /**
     * Exit a parse tree produced by {@link BoosterParser#node_id}.
     * @param ctx the parse tree
     */
    void exitNode_id(BoosterParser.Node_idContext ctx);
    /**
     * Enter a parse tree produced by {@link BoosterParser#leaf_node}.
     * @param ctx the parse tree
     */
    void enterLeaf_node(BoosterParser.Leaf_nodeContext ctx);
    /**
     * Exit a parse tree produced by {@link BoosterParser#leaf_node}.
     * @param ctx the parse tree
     */
    void exitLeaf_node(BoosterParser.Leaf_nodeContext ctx);
}
