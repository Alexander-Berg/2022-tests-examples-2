package ru.yandex.autotests.metrika.filters;

import ru.yandex.autotests.metrika.data.report.v1.enums.ReportFilterType;

import java.util.function.Function;

import static org.apache.commons.lang3.StringUtils.*;

/**
 * Created by sourx on 10.06.16.
 */
public class Node implements Expression {

    private enum LogicalOperator {
        AND(ReportFilterType::getAnd),
        OR(ReportFilterType::getOr);

        private Function<ReportFilterType, String> stringMapper;

        LogicalOperator(Function<ReportFilterType, String> stringMapper) {
            this.stringMapper = stringMapper;
        }

        public String toString(ReportFilterType type) {
            return stringMapper.apply(type);
        }
    }

    private Expression left;
    private Expression right;
    private LogicalOperator logicalOperator;

    private Node(Expression left) {
        this.left = left;
    }

    public static Node left(Expression left) {
        return new Node(left);
    }

    @Override
    public String build(ReportFilterType type) {
        String leftString = left.build(type);
        String rightString = right.build(type);

        if (isBlank(leftString) && isNotBlank(rightString)) {
            return rightString;
        } else if (isNotBlank(leftString) && isBlank(rightString)) {
            return leftString;
        } else if (isBlank(leftString) && isBlank(rightString)) {
            return EMPTY;
        }
        return String.format(type.getFormat(), leftString, logicalOperator.toString(type), rightString);
    }

    @Override
    public Expression and(Expression expression) {
        if (right == null) {
            right = expression;
            logicalOperator = LogicalOperator.AND;
            return this;
        } else {
            return left(this).and(expression);
        }
    }

    @Override
    public Expression or(Expression expression) {
        if (right == null) {
            right = expression;
            logicalOperator = LogicalOperator.OR;
            return this;
        } else {
            return left(this).or(expression);
        }
    }
}
