package ru.yandex.metrika.segments.core.parser;

import java.util.Map;

import org.junit.Before;

import ru.yandex.metrika.segments.clickhouse.ast.CHLiteral;
import ru.yandex.metrika.segments.clickhouse.ast.Condition;
import ru.yandex.metrika.segments.clickhouse.ast.Expression;
import ru.yandex.metrika.segments.clickhouse.ast.ExpressionTransformer;
import ru.yandex.metrika.segments.clickhouse.literals.CHNotNull;
import ru.yandex.metrika.segments.clickhouse.types.CHType;
import ru.yandex.metrika.segments.clickhouse.types.TBoolean;
import ru.yandex.metrika.segments.core.ApiUtils;
import ru.yandex.metrika.segments.core.query.QueryContext;
import ru.yandex.metrika.segments.core.secure.UserType;
import ru.yandex.metrika.util.locale.LocaleDomain;
import ru.yandex.metrika.util.locale.LocaleLangs;

import static org.junit.Assert.assertEquals;

/**
 * Наследники этого класса не совсем юнит тесты. Ну или смотря что считать юнитом. Тут мы скорее проверяем,
 * что поведение некоторого подмножества кода парсинга и рендеринга запросов ведёт себя консистентно и ожидаемо
 */
public abstract class AbstractTest {
    protected ApiUtils apiUtils;
    protected QueryParserFactory qpf;
    protected SelectPartParser spp;
    protected SimpleTestAttributeBundle bundle;


    @Before
    public void setUp() throws Exception {
        SimpleTestSetup simpleTestSetup = new SimpleTestSetup();
        apiUtils = simpleTestSetup.getApiUtils();
        qpf = apiUtils.getParserFactory();
        spp = apiUtils.getSelectPartParser();
        bundle = simpleTestSetup.getBundle();
    }

    public QueryContext.Builder contextBuilder() {
        return QueryContext.defaultFields()
                .apiUtils(apiUtils)
                .startDate("2012-01-01")
                .endDate("2012-01-02")
                .idsByName(Map.of("counter", new int[]{100}))
                .lang("ru");
    }

    public QueryParams builder() {
        return QueryParams.create()
                .counterId(100)
                .startDate("2012-01-01")
                .endDate("2012-01-02")
                .metrics("ym:s:visits")
                .userType(UserType.MANAGER)
                .lang(LocaleLangs.RU)
                .domain(LocaleDomain.getDefaultChDomain());
    }

    protected void assertEqualExpressions(Expression<?> expected, Expression<?> actual) {
        assertEquals(
                expected.visit(Normalizer.INSTANCE),
                actual.visit(Normalizer.INSTANCE)
        );
    }

    private static final class Normalizer implements ExpressionTransformer {

        private static final Normalizer INSTANCE = new Normalizer();

        @Override
        public Expression<TBoolean> visit(Condition arg) {
            //избавляемся от Condition
            return arg.getExpr().visit(this);
        }

        @Override
        public <U extends CHType> Expression<U> visit(CHLiteral<U> arg) {
            // избавляемся от nullable обёрток не nullable констант
            return arg instanceof CHNotNull ? ((CHNotNull<U>) arg).asValue() : arg;
        }
    }
}
