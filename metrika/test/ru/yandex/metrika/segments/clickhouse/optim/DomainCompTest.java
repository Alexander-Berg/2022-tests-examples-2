package ru.yandex.metrika.segments.clickhouse.optim;

import org.junit.Ignore;

import ru.yandex.metrika.segments.clickhouse.ClickHouse;
import ru.yandex.metrika.segments.clickhouse.ast.Name;
import ru.yandex.metrika.segments.clickhouse.types.TString;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;

/**
 * Created by orantius on 07.09.16.
 */
@Ignore("METRIQA-936")
public class DomainCompTest {
    public static void main(String[] args) {
        Name<TString> x = ClickHouse.name("x");
        DomainComp<TString> geabc = DomainComp.ge(x,s("abc"));
        DomainComp<TString> ledef = DomainComp.le(x,s("def"));
        Domain<TString> abcdef = ledef.intersection(geabc);
        System.out.println("abcdef = " + abcdef);
        Domain<TString> ltabc = geabc.complement();
        System.out.println("ltabc = " + ltabc);
        Domain<TString> gtdef = ledef.complement();
        System.out.println("gtdef = " + gtdef);
        Domain<TString> ltabc2 = ltabc.intersection(ledef);
        System.out.println("ltabc2 = " + ltabc2);
        Domain<TString> notabcdef = ltabc.union(gtdef);
        System.out.println("notabcdef = " + notabcdef);
        Domain<TString> empty = notabcdef.intersection(abcdef);
        System.out.println("empty = " + empty);
        Domain<TString> all = notabcdef.union(abcdef);
        System.out.println("all = " + all);
    }
}
