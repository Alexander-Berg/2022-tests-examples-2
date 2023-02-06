package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.toFixedString;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.unhex;

public class IPv6NumToStringLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.IPv6NumToString)
                .forArgs(toFixedString(s(""),16))    .expect(s("::"))
                .forArgs(toFixedString(s("1"),16))    .expect(s("3100::"))
                .forArgs(toFixedString(unhex("087773EC52A67AE9CB37A9A84D1BF413"),16))    .expect(s("877:73ec:52a6:7ae9:cb37:a9a8:4d1b:f413"))
                .forArgs(toFixedString(unhex("8489551C1F74534141CD9F43B09FC4B6"),16))    .expect(s("8489:551c:1f74:5341:41cd:9f43:b09f:c4b6"))
                .forArgs(toFixedString(unhex("536AC1B1A374F6BE4470E4A4237AB302"),16))    .expect(s("536a:c1b1:a374:f6be:4470:e4a4:237a:b302"))
                .forArgs(toFixedString(unhex("3836D49C0041BAF0D7E137DEADC312A2"),16))    .expect(s("3836:d49c:41:baf0:d7e1:37de:adc3:12a2"))
                .forArgs(toFixedString(unhex("A05734850BEF42D070CA1B243D3766C7"),16))    .expect(s("a057:3485:bef:42d0:70ca:1b24:3d37:66c7"))
                .forArgs(toFixedString(unhex("CDC254BF19AF9AEEA168D491D72B8486"),16))    .expect(s("cdc2:54bf:19af:9aee:a168:d491:d72b:8486"))
                .forArgs(toFixedString(unhex("A58DC3F0B200ABD9B5E58C0D50A1963F"),16))    .expect(s("a58d:c3f0:b200:abd9:b5e5:8c0d:50a1:963f"))
                .forArgs(toFixedString(unhex("E0675339543387E6AC2399E720566B61"),16))    .expect(s("e067:5339:5433:87e6:ac23:99e7:2056:6b61"))
                .forArgs(toFixedString(unhex("197E9F77B1EA30CF0DC39462094DACBC"),16))    .expect(s("197e:9f77:b1ea:30cf:dc3:9462:94d:acbc"))
                .forArgs(toFixedString(unhex("21B2A8AB8A588FD11A1BDC2898C64F77"),16))    .expect(s("21b2:a8ab:8a58:8fd1:1a1b:dc28:98c6:4f77"))
                .build();
    }

}
