package ru.yandex.metrika.segments.clickhouse.optim;

import dk.brics.automaton.RegExp;
import org.junit.Test;

import ru.yandex.metrika.segments.clickhouse.ClickHouse;
import ru.yandex.metrika.segments.clickhouse.ast.Field;
import ru.yandex.metrika.segments.clickhouse.ast.Name;
import ru.yandex.metrika.segments.clickhouse.types.TInt8;
import ru.yandex.metrika.segments.clickhouse.types.TString;
import ru.yandex.metrika.segments.site.schema.MtLog;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Int8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.ToString;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.concat;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;

/**
 * Created by orantius on 30.10.16.
 */
public class DomainRegexTest {
    Name<TString> a = n("a");
    Name<TString> b = n("b");
    Field<TInt8> id = ClickHouse.field(MtLog.visits, "id",Int8());

    @Test
    public void buildRegExp() throws Exception {
        RegExp abc = DomainRegex.buildRegExp(s("abc"));
        System.out.println("ab = " + DomainRegex.print(abc));
        RegExp ab = DomainRegex.buildRegExp(concat(s("a"), s("b")));
        System.out.println("ab = " + DomainRegex.print(ab));

        RegExp aXb = DomainRegex.buildRegExp(concat(s("a"), n("X"), s("b")));
        System.out.println("aXb = " + DomainRegex.print(aXb));

        RegExp like = DomainRegex.like("%");
        System.out.println("like = " + DomainRegex.print(like));

        RegExp like2 = DomainRegex.like("_");
        System.out.println("like2 = " + DomainRegex.print(like2));

        RegExp like3 = DomainRegex.like("\\_");
        System.out.println("like3 = " + DomainRegex.print(like3));

        RegExp aIDb = DomainRegex.buildRegExp(concat(s("a"), ToString(id), s("b")));
        System.out.println("aIDb = " + DomainRegex.print(aIDb));

    }



}
