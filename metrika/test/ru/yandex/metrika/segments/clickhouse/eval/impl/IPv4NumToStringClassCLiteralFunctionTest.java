package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un32;

public class IPv4NumToStringClassCLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.IPv4NumToStringClassC)
                .forArgs(un32(0))               .expect(s("0.0.0.xxx"))
                .forArgs(un32(401283872))       .expect(s("23.235.27.xxx"))
                .forArgs(un32("3593357463"))    .expect(s("214.46.72.xxx"))
                .forArgs(un32("3460548378"))    .expect(s("206.67.199.xxx"))
                .forArgs(un32("2605951912"))    .expect(s("155.83.171.xxx"))
                .forArgs(un32(73018031))        .expect(s("4.90.42.xxx"))
                .forArgs(un32(1375735594))      .expect(s("82.0.15.xxx"))
                .forArgs(un32("3656737208"))    .expect(s("217.245.97.xxx"))
                .forArgs(un32(800423781))       .expect(s("47.181.127.xxx"))
                .forArgs(un32(417821755))       .expect(s("24.231.116.xxx"))
                .forArgs(un32(1807078440))      .expect(s("107.181.212.xxx"))
                .build();
    }

}
