package ru.yandex.metrika.segments.clickhouse.xgb;

/**
 * Created by orantius on 14.04.17.
 */
public class Branch implements Node {
    String factor;
    double value;
    // if(factor < value, left, right)   missing?
    Node left;
    Node right;

    public Branch(String factor, double value, Node left, Node right) {
        this.factor = factor;
        this.value = value;
        this.left = left;
        this.right = right;
    }

    @Override
    public String toString() {
        return "if("+ factor + '<' + value +", " + left +", " + right +')';
    }
}
