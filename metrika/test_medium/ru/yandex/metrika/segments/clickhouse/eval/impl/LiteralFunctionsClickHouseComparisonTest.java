package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.lang.reflect.Modifier;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

import org.apache.logging.log4j.Level;
import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.reflections.Reflections;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.clickhouse.settings.ClickHouseProperties;
import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.clickhouse.ClickHouseSource;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplate;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplateImpl;
import ru.yandex.metrika.dbclients.mysql.RowMappers;
import ru.yandex.metrika.segments.clickhouse.ast.CHLiteral;
import ru.yandex.metrika.segments.clickhouse.func.CHFunction;
import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;
import ru.yandex.metrika.segments.clickhouse.types.TNumber;
import ru.yandex.metrika.util.collections.Try;
import ru.yandex.metrika.util.log.Log4jSetup;

import static java.util.function.Predicate.not;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.unwrapNumUnchecked;

/**
 * Медиум тест который, который проверяет корректность работы реализаций LiteralFunction с помощью реального ClickHouse
 * Работает он так:
 * 1. Сканит пакет ru.yandex.metrika.segments.clickhouse.eval.impl и находи в нём всех наследников ParametrizedLiteralFunctionTest
 * 2. Достаёт их всех классов их (почти) все тесткейсы
 * 3. Отправляет в CH выражения вида f(args) = expected и ожидает получить 1
 */
@RunWith(Parameterized.class)
public class LiteralFunctionsClickHouseComparisonTest {

    static {
        Log4jSetup.basicArcadiaSetup(Level.INFO);
    }

    private static final Logger log = LoggerFactory.getLogger(LiteralFunctionsClickHouseComparisonTest.class);

    private final HttpTemplate template;

    @Parameterized.Parameter
    public String checkExpression;

    @Parameterized.Parameters(name = "{index}: {0}")
    public static Collection<Object[]> cases() {
        var unitTests = new Reflections("ru.yandex.metrika.segments.clickhouse.eval.impl")
                .getSubTypesOf(ParametrizedLiteralFunctionTest.class);

        log.info("Found unit tests classes: {}", unitTests);

        //noinspection unchecked
        return unitTests.stream().flatMap(clazz -> Arrays.stream(clazz.getDeclaredMethods()))
                .filter(method -> Modifier.isStatic(method.getModifiers()) && method.isAnnotationPresent(Parameterized.Parameters.class))
                .map(method -> (Collection<Object[]>) Try.of(() -> method.invoke(null)).orThrow())
                .flatMap(Collection::stream)
                .filter(not(LiteralFunctionsClickHouseComparisonTest::isKnownInconsistencyCase))
                .map(arr -> (String) arr[3]/*sql*/)
                .sorted()
                .map(sql -> new Object[]{sql})
                .collect(Collectors.toList());
    }

    /**
     * Предикат предназначенный для выфильтровывания известных неконсистентностей между Java реализацией функций и их
     * реализацией в Clickhouse.
     * Список:
     * 1. arrayElement(*, 0) {@link ru.yandex.metrika.segments.clickhouse.eval.LiteralFunctions#arrayElement}
     */
    public static boolean isKnownInconsistencyCase(Object[] params) {
        CHFunction function = (CHFunction) params[0];
        //noinspection unchecked
        List<CHLiteral<?>> args = (List<CHLiteral<?>>) params[1];
        return function.equals(CHFunctions.arrayElement) && args.size() == 2 && args.get(1) instanceof TNumber && unwrapNumUnchecked(args.get(1)).longValue() == 0;
    }

    public LiteralFunctionsClickHouseComparisonTest() {
        var clickHouseSource = new ClickHouseSource(EnvironmentHelper.clickhouseHost, EnvironmentHelper.clickhousePort, "default");
        var clickHouseProperties = new ClickHouseProperties();
        clickHouseProperties.setUser(EnvironmentHelper.clickhouseUser);
        clickHouseProperties.setPassword(EnvironmentHelper.clickhousePassword);
        this.template = new HttpTemplateImpl(clickHouseSource, clickHouseProperties);
    }

    @Test
    public void test() {
        var passed = template.queryForObject("select " + checkExpression, RowMappers.BOOLEAN);
        Assert.assertTrue(checkExpression + " turns out to be false", passed);
    }
}
