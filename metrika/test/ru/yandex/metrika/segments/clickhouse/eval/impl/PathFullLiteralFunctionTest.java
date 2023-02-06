package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;

public class PathFullLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.pathFull)

                .forArgs(s(""))                 .expect(s(""))
                .forArgs(s("qqq"))              .expect(s(""))
                .forArgs(s("q/q"))              .expect(s("/q"))
                .forArgs(s("q/q?q=q"))          .expect(s("/q?q=q"))
                .forArgs(s("q/q#q"))            .expect(s("/q#q"))
                .forArgs(s("q/q?q=q#q"))        .expect(s("/q?q=q#q"))

                .forArgs(s("metrika.yandex.ru/settings?id=24226447&tab=common"))        .expect(s("/settings?id=24226447&tab=common"))
                .forArgs(s("metrika.yandex.ru/settings?id=24226447&tab=common#ref"))    .expect(s("/settings?id=24226447&tab=common#ref"))

                .forArgs(s("https://metrika.yandex.ru/settings?id=24226447&tab=common"))        .expect(s("/settings?id=24226447&tab=common"))
                .forArgs(s("https://metrika.yandex.ru/settings?id=24226447&tab=common#ref"))    .expect(s("/settings?id=24226447&tab=common#ref"))

                // это не я придумал, это оно реально так работает ¯\_(ツ)_/¯
                .forArgs(s("это может быть всё что угодно только / не / путь ? Да !"))                  .expect(s("/ не / путь ? Да !"))
                .forArgs(s("это может быть всё что угодно только // не / путь ? Да !"))                 .expect(s("/ путь ? Да !"))
                .forArgs(s("это может быть всё что угодно только / не / путь ! #ClickhouseНеТормозит")) .expect(s("/ не / путь ! #ClickhouseНеТормозит"))
                .build();
    }
}
