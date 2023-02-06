package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un64;

public class PositionCaseInsensitiveUTF8LiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.positionCaseInsensitiveUTF8)
                .forArgs(s(""), s("b"))         .expect(un64(0))

                .forArgs(s("a"), s("b"))        .expect(un64(0))
                .forArgs(s("b"), s("b"))        .expect(un64(1))

                .forArgs(s("b"), s("B"))        .expect(un64(1))
                .forArgs(s("B"), s("b"))        .expect(un64(1))
                .forArgs(s("B"), s("B"))        .expect(un64(1))

                .forArgs(s("aB"), s("B"))       .expect(un64(2))
                .forArgs(s("aaB"), s("B"))      .expect(un64(3))
                .forArgs(s("aaaB"), s("B"))     .expect(un64(4))

                .forArgs(s("aB"), s("aB"))      .expect(un64(1))
                .forArgs(s("aaB"), s("aB"))     .expect(un64(2))
                .forArgs(s("aaaB"), s("aB"))    .expect(un64(3))

                .forArgs(s("something cool"), s("cool"))    .expect(un64(11))
                .forArgs(s("something COOL"), s("cool"))    .expect(un64(11))
                .forArgs(s("something cool"), s("COOL"))    .expect(un64(11))
                .forArgs(s("something cOOl"), s("CooL"))    .expect(un64(11))


                .forArgs(s("somethinG cool"), s("Something"))    .expect(un64(1))
                .forArgs(s("sOmEtHiNg COOL"), s("SoMeThInG"))    .expect(un64(1))
                .forArgs(s("SOMEthing cool"), s("someTHING"))    .expect(un64(1))

                .forArgs(s("чтО-тО крУтОЕ"), s("Что"))    .expect(un64(1))
                .forArgs(s("чтО-тО крУтОЕ"), s("-То"))    .expect(un64(4))
                .forArgs(s("чтО-тО крУтОЕ"), s("КрутоЕ")) .expect(un64(8))

                .build();
    }

}
