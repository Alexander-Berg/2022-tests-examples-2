package ru.yandex.metrika.segments.clickhouse.optim;

import java.util.Arrays;

import org.junit.Test;

import ru.yandex.metrika.segments.clickhouse.ast.Condition;
import ru.yandex.metrika.segments.clickhouse.ast.FunctionCall;
import ru.yandex.metrika.segments.clickhouse.parse.PrintQuery;
import ru.yandex.metrika.segments.clickhouse.types.TInt8;
import ru.yandex.metrika.segments.clickhouse.types.TTuple2;
import ru.yandex.metrika.segments.clickhouse.types.TTuple3;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.tuple;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;
import static ru.yandex.metrika.segments.site.schema.MtLog.ClickStorage.ContextType;
import static ru.yandex.metrika.segments.site.schema.MtLog.ClickStorage.PhraseID;

/**
 * Created by orantius on 28.08.16.
 */
public class PrintQueryTest {
    @Test
    public void print() throws Exception {

        FunctionCall<TTuple3<TTuple2<TInt8, TInt8>, TTuple2<TInt8, TInt8>, TTuple2<TInt8, TInt8>>> t3 = tuple(tuple(n8(1), n8(1)),
                tuple(n8(1), n8(1)),
                tuple(n8(1), n8(1)));

        FunctionCall<TTuple2<TTuple2<TInt8, TInt8>, TTuple2<TInt8, TInt8>>> t2 = tuple(tuple(n8(1), n8(1)),
                tuple(n8(1), n8(1)));

        Condition in = tuple(ContextType, PhraseID).in(Arrays.asList(
                tuple(un8(1),un64(723312559)),tuple(un8(2),un64(256473)),
                tuple(un8(2),un64(256475)),tuple(un8(2),un64(255339)),tuple(un8(2),un64(256470)),tuple(un8(1),un64(723312546)),tuple(un8(1),un64(130738857))));



        System.out.println("print = " + PrintQuery.print(t3));
        System.out.println("print = " + PrintQuery.print(t2));
        System.out.println("print = " + PrintQuery.print(in));
    }

}
