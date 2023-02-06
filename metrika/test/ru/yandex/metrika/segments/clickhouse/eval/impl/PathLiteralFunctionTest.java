package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;

public class PathLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.path)

                .forArgs(s(""))                 .expect(s(""))
                .forArgs(s("qqq"))              .expect(s(""))
                .forArgs(s("q/q"))              .expect(s("/q"))
                .forArgs(s("q/q?q=q"))          .expect(s("/q"))
                .forArgs(s("q/q#q"))            .expect(s("/q"))
                .forArgs(s("q/q?q=q#q"))        .expect(s("/q"))

                .forArgs(s("metrika.yandex.ru/settings?id=24226447&tab=common"))        .expect(s("/settings"))
                .forArgs(s("metrika.yandex.ru/settings?id=24226447&tab=common#ref"))    .expect(s("/settings"))

                .forArgs(s("https://metrika.yandex.ru/settings?id=24226447&tab=common"))        .expect(s("/settings"))
                .forArgs(s("https://metrika.yandex.ru/settings?id=24226447&tab=common#ref"))    .expect(s("/settings"))

                // это не я придумал, это оно реально так работает ¯\_(ツ)_/¯
                .forArgs(s("это может быть всё что угодно только / не / путь ? Да !"))                  .expect(s("/ не / путь "))
                .forArgs(s("это может быть всё что угодно только // не / путь ? Да !"))                 .expect(s("/ путь "))
                .forArgs(s("это может быть всё что угодно только / не / путь ! #ClickhouseНеТормозит")) .expect(s("/ не / путь ! "))
                .build();
    }
}
