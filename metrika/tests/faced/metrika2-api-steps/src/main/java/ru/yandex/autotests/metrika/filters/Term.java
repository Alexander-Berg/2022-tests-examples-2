package ru.yandex.autotests.metrika.filters;

import org.apache.commons.lang3.StringUtils;
import ru.yandex.autotests.metrika.converters.FilterOperandStringConverter;
import ru.yandex.autotests.metrika.data.report.v1.enums.ReportFilterType;

import java.util.List;

import static ch.lambdaj.collection.LambdaCollections.with;
import static ru.yandex.autotests.metrika.filters.Node.left;
import static ru.yandex.autotests.metrika.utils.Utils.wrapFilterValue;

/**
 * Created by konkov on 08.10.2014.
 * <p/>
 * Выражение фильтра
 */
public class Term implements Expression {

    private static final String SEPARATOR = ",";
    private final String attribute;
    private Operator operator;
    private Object operand;
    private boolean hasOperand = false;

    private Term(String attribute) {
        this.attribute = attribute;
    }

    public static Term term(String attribute) {
        return new Term(attribute);
    }

    public static Term metric(String metricName) {
        return term(metricName);
    }

    public static Term dimension(String dimensionName) {
        return term(dimensionName);
    }

    public static Term empty() {
        return new Term(null);
    }

    public Term withOperator(Operator operator) {
        this.operator = operator;
        return this;
    }

    public Term withOperand(Object operand) {
        this.operand = operand;
        this.hasOperand = true;
        return this;
    }

    public Term withOutOperand() {
        this.hasOperand = false;
        return this;
    }

    public Term in(Object operand) {
        return withOperator(Operator.IN).withOperand(operand);
    }

    public Term inAlias(Object operand) {
        return withOperator(Operator.IN_ALIAS).withOperand(operand);
    }

    public Term in(Object... operand) {
        return withOperator(Operator.IN).withOperand(operand);
    }

    public Term inAlias(Object... operand) {
        return withOperator(Operator.IN_ALIAS).withOperand(operand);
    }

    public Term notIn(Object... operand) {
        return withOperator(Operator.NOT_IN).withOperand(operand);
    }

    public Term notInAlias(Object... operand) {
        return withOperator(Operator.NOT_IN_ALIAS).withOperand(operand);
    }

    public Term equalTo(Object operand) {
        return withOperator(Operator.EQUAL).withOperand(operand);
    }

    public Term equalToAlias(Object operand) {
        return withOperator(Operator.EQUAL_ALIAS).withOperand(operand);
    }

    public Term notEqualTo(Object operand) {
        return withOperator(Operator.NOT_EQUAL).withOperand(operand);
    }

    public Term notEqualToAlias(Object operand) {
        return withOperator(Operator.NOT_EQUAL_ALIAS).withOperand(operand);
    }

    public Term lessThan(Object operand) {
        return withOperator(Operator.LESS).withOperand(operand);
    }

    public Term greaterThan(Object operand) {
        return withOperator(Operator.GREATER).withOperand(operand);
    }

    public Term notDefined() {
        return equalTo(null);
    }

    public Term notDefinedAlias() {
        return withOperator(Operator.NOT_DEFINED).withOutOperand();
    }

    public Term notDefinedAlias2() {
        return withOperator(Operator.NOT_DEFINED_ALIAS).withOutOperand();
    }

    public Term notDefinedAlias3() {
        return withOperator(Operator.NOT_DEFINED_ALIAS2).withOutOperand();
    }

    public Term defined() {
        return notEqualTo((Object) null);
    }

    public Term definedAlias() {
        return withOperator(Operator.DEFINED).withOutOperand();
    }

    public Term definedAlias2() {
        return withOperator(Operator.DEFINED_ALIAS).withOutOperand();
    }

    public Term definedAlias3() {
        return withOperator(Operator.DEFINED_ALIAS2).withOutOperand();
    }

    public Term greaterThanOrEqualTo(Object operand) {
        return withOperator(Operator.GREATER_OR_EQUAL).withOperand(operand);
    }

    public Term lessThanOrEqualTo(Object operand) {
        return withOperator(Operator.LESS_OR_EQUAL).withOperand(operand);
    }

    public Term matchSubstring(Object operand) {
        return withOperator(Operator.SUBSTRING).withOperand(operand);
    }

    public Term matchSubstringAlias(Object operand) {
        return withOperator(Operator.SUBSTRING_ALIAS).withOperand(operand);
    }

    public Term matchSubstringAlias2(Object operand) {
        return withOperator(Operator.SUBSTRING_ALIAS2).withOperand(operand);
    }

    public Term notMatchSubstring(Object operand) {
        return withOperator(Operator.NOT_SUBSTRING).withOperand(operand);
    }

    public Term notMatchSubstringAlias(Object operand) {
        return withOperator(Operator.NOT_SUBSTRING_ALIAS).withOperand(operand);
    }

    public Term notMatchSubstringAlias2(Object operand) {
        return withOperator(Operator.NOT_SUBSTRING_ALIAS2).withOperand(operand);
    }

    public Term matchRegEx(Object operand) {
        return withOperator(Operator.REGEX).withOperand(operand);
    }

    public Term matchRegExAlias(Object operand) {
        return withOperator(Operator.REGEX_ALIAS).withOperand(operand);
    }

    public Term matchRegExAlias2(Object operand) {
        return withOperator(Operator.REGEX_ALIAS2).withOperand(operand);
    }

    public Term notMatchRegEx(Object operand) {
        return withOperator(Operator.NOT_REGEX).withOperand(operand);
    }

    public Term notMatchRegExAlias(Object operand) {
        return withOperator(Operator.NOT_REGEX_ALIAS).withOperand(operand);
    }

    public Term notMatchRegExAlias2(Object operand) {
        return withOperator(Operator.NOT_REGEX_ALIAS2).withOperand(operand);
    }

    public Term matchStar(Object operand) {
        return withOperator(Operator.EQUAL_STAR).withOperand(operand);
    }

    public Term matchStarAlias(Object operand) {
        return withOperator(Operator.EQUAL_STAR_ALIAS).withOperand(operand);
    }

    public Term notMatchStar(Object operand) {
        return withOperator(Operator.NOT_EQUAL_STAR).withOperand(operand);
    }

    public Term notMatchStarAlias(Object operand) {
        return withOperator(Operator.NOT_EQUAL_STAR_ALIAS).withOperand(operand);
    }

    @Override
    public String build(ReportFilterType type) {
        StringBuilder builder = new StringBuilder();

        if (!StringUtils.isEmpty(attribute)) {
            appendAttribute(builder);
            appendOperator(builder);
            appendOperand(builder);
        }

        return builder.toString();
    }

    private void appendAttribute(StringBuilder builder) {
        builder.append(attribute);
    }

    private void appendOperator(StringBuilder builder) {
        builder.append(operator.getValue());
    }

    private void appendOperand(StringBuilder builder) {
        if (!hasOperand)
            return;
        if (operand == null) {
            builder.append("null");
            return;
        }
        if (operand instanceof List) {
            builder.append("(")
                    .append(with((List) operand).convert(new FilterOperandStringConverter()).join(SEPARATOR))
                    .append(")");
            return;
        }
        if (operand.getClass().isArray()) {
            builder.append("(")
                    .append(with((Object[]) operand).convert(new FilterOperandStringConverter()).join(SEPARATOR))
                    .append(")");
            return;
        }
        builder.append(wrapFilterValue(operand));
    }

    @Override
    public String toString() {
        return build();
    }

    @Override
    public Expression and(Expression expression) {
        return left(this).and(expression);
    }

    @Override
    public Expression or(Expression expression) {
        return left(this).or(expression);
    }
}
