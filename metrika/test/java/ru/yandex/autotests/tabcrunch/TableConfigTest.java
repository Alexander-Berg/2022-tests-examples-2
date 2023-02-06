package ru.yandex.autotests.tabcrunch;

import org.junit.Test;
import org.junit.Assert;
import ru.yandex.autotests.tabcrunch.config.TableConfig;
import ru.yandex.autotests.tabcrunch.util.TabCrunchException;

import java.util.Arrays;

import static java.util.Arrays.asList;
import static junit.framework.Assert.fail;

/**
 * Created by lonlylocly on 07.10.14.
 */
public class TableConfigTest {

    @Test
    public void columnNameRegexFilter() {
        final TableConfig table = new TableConfig();
        table.setColumns(asList("CounterID", "ID"));
        table.setFilterOutColumnsRegex(asList("ID"));

        Assert.assertTrue(table.columnToBeFilteredOut("ID"));

        Assert.assertFalse(table.columnToBeFilteredOut("ID1"));

    }

    @Test
    public void copyTest() {
        final TableConfig tab = new TableConfig();
        tab.setLocation("http://some.org");
        tab.setAlias("Yahoo");
        tab.setColumns(Arrays.asList("1", "2"));

        final TableConfig copy = tab.copy();

        Assert.assertEquals(tab.getLocation(), copy.getLocation());
        Assert.assertEquals(tab.getAlias(), copy.getAlias());
        Assert.assertEquals(tab.getColumns().get(0), copy.getColumns().get(0));
        Assert.assertEquals(tab.getColumns().get(1), copy.getColumns().get(1));
    }

    @Test
    public void emptyColsTest() {
        final TableConfig tab = new TableConfig();
        try {
            tab.getActualColNames();
        } catch (TabCrunchException ex) {
            return;
        }
        fail();
    }

}
