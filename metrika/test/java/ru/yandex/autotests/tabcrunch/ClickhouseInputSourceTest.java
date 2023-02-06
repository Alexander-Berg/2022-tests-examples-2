package ru.yandex.autotests.tabcrunch;

import org.junit.Assert;
import org.junit.Test;
import ru.yandex.autotests.tabcrunch.config.TableConfig;
import ru.yandex.autotests.tabcrunch.input.ClickhouseInputSource;

import java.util.Arrays;
import java.util.List;

import static org.hamcrest.core.Is.is;

/**
 * Created by lonlylocly on 20/01/15.
 */
public class ClickhouseInputSourceTest {

    @Test
    public void diffColNamesList() {
        List<String> colNamePatterns = Arrays.asList(".*");

        TableConfig t1 = new TableConfig();
        t1.setLocation("http://some.org");
        t1.setColumns(Arrays.asList("Erich", "Maria", "Remark"));

        TableConfig t2 = new TableConfig();
        t2.setLocation("http://some.org");
        t2.setColumns(Arrays.asList("Erich", "Remark"));

        final ClickhouseInputSource s1 = new ClickhouseInputSource(t1);

        s1.setColumnsToSelect(t1.getColumnsMatchingPatternsAndCommonWith(t2, colNamePatterns));

        s1.setColumnsToSelectWithVirtual();
        Assert.assertThat(t1.getColumns().toString(), is("[Erich, Remark]"));

    }

    @Test
    public void virtualColsList() {
        TableConfig t1 = new TableConfig();
        t1.setLocation("http://some.org");
        t1.setColumns(Arrays.asList("Erich", "Remark"));
        t1.setVirtualColumns(Arrays.asList("_table"));

        final ClickhouseInputSource s1 = new ClickhouseInputSource(t1);

        s1.setColumnsToSelectWithVirtual();

        Assert.assertThat(t1.getColumns().toString(), is("[Erich, Remark, _table]"));

    }
}
