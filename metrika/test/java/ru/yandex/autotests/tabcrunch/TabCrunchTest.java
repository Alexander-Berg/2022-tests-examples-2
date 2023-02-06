package ru.yandex.autotests.tabcrunch;

import org.junit.Assert;
import org.junit.Test;
import ru.yandex.autotests.tabcrunch.config.TableConfig;
import ru.yandex.autotests.tabcrunch.input.StringInputSource;
import ru.yandex.autotests.tabcrunch.report.TabCrunchReport;

import java.io.IOException;
import java.util.Arrays;
import java.util.Collections;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.iterableWithSize;

/**
 * Created with IntelliJ IDEA.
 * User: lonlylocly
 * Date: 18.11.13
 * Time: 21:22
 * To change this template use File | Settings | File Templates.
 */
public class TabCrunchTest {

    TableConfig table = new TableConfig();

    @Test
    public void hasDiff() {
        final String line1 = "a\nc";
        final String line2 = "b\nc";

        table.setColumns(Arrays.asList("one"));
        final TabCrunch tabCrunch = new TabCrunch(
                StringInputSource.make(table, line1),
                StringInputSource.make(table, line2),
                Arrays.asList("one"),
                Arrays.asList("one")
        );
        final boolean noDiff = tabCrunch.doDiff();
        Assert.assertFalse(noDiff);
    }

    @Test
    public void hasDiff2() throws IOException {
        final String line1 = "a\ta\nc\tc";
        final String line2 = "a\ta\nc\tb";

        table.setColumns(Arrays.asList("one", "two"));
        final TabCrunch tabCrunch = new TabCrunch(
                StringInputSource.make(table, line1),
                StringInputSource.make(table, line2),
                Arrays.asList("one", "two"),
                Arrays.asList("one")
        );
        final boolean noDiff = tabCrunch.doDiff();
        Assert.assertFalse(noDiff);
    }

    @Test
    public void noDiff() {
        final String sameLine = "a";

        table.setColumns(Arrays.asList("one", "two"));
        final TabCrunch tabCrunch = new TabCrunch(
                StringInputSource.make(table, sameLine),
                StringInputSource.make(table, sameLine),
                Arrays.asList("one"),
                Arrays.asList("one")
        );
        final boolean noDiff = tabCrunch.doDiff();
        Assert.assertTrue(noDiff);
        tabCrunch.getReport();
    }

    @Test
    public void TwoLinesDiff() {
        final String line1 = "a\tb\nc\td\ne\tf";
        final String line2 = "e\tf";

        table.setColumns(Arrays.asList("one", "two"));
        final TabCrunch tabCrunch = new TabCrunch(
                StringInputSource.make(table, line1),
                StringInputSource.make(table, line2),
                Arrays.asList("one", "two"),
                Arrays.asList("one")
        );
        final boolean noDiff = tabCrunch.doDiff();
        Assert.assertFalse(noDiff);

        TabCrunchReport report = tabCrunch.getReport();
        assertThat(report.getDiffLines(), iterableWithSize(2));
    }

    @Test
    public void emptyTestSource() {
        final String line1 = "";
        final String line2 = "b\nc";

        table.setColumns(Arrays.asList("one"));
        final TabCrunch tabCrunch = new TabCrunch(
                StringInputSource.make(table, line1),
                StringInputSource.make(table, line2),
                Arrays.asList("one"),
                Arrays.asList("one")
        );
        final boolean noDiff = tabCrunch.doDiff();
        Assert.assertFalse(noDiff);
        Assert.assertFalse(tabCrunch.getReport().areSourcesEmpty());
    }

    @Test
    public void emptyStableSource() {
        final String line1 = "a\nc";
        final String line2 = "";

        table.setColumns(Arrays.asList("one"));
        final TabCrunch tabCrunch = new TabCrunch(
                StringInputSource.make(table, line1),
                StringInputSource.make(table, line2),
                Arrays.asList("one"),
                Arrays.asList("one")
        );
        final boolean noDiff = tabCrunch.doDiff();
        Assert.assertFalse(noDiff);
        Assert.assertFalse(tabCrunch.getReport().areSourcesEmpty());
    }

    @Test
    public void emptyBothSources() {
        final String line1 = "";
        final String line2 = "";

        table.setColumns(Arrays.asList("one"));
        final TabCrunch tabCrunch = new TabCrunch(
                StringInputSource.make(table, line1),
                StringInputSource.make(table, line2),
                Arrays.asList("one"),
                Arrays.asList("one")
        );
        final boolean noDiff = tabCrunch.doDiff();
        Assert.assertTrue(noDiff);
        Assert.assertTrue(tabCrunch.getReport().areSourcesEmpty());
    }

}
