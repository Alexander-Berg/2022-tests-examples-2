package ru.yandex.autotests.tabcrunch;

import com.google.common.collect.ImmutableList;
import org.junit.Assert;
import org.junit.Test;
import ru.yandex.autotests.metrika.commons.beans.BeanUtils;
import ru.yandex.autotests.metrika.commons.beans.Serialization;
import ru.yandex.autotests.tabcrunch.config.TableConfig;
import ru.yandex.autotests.tabcrunch.input.TskvInputSource2;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import static java.util.stream.Collectors.toMap;
import static ru.yandex.autotests.metrika.commons.beans.BeanUtils.extractColumns;

public class TabCrunchTskv2Test {

    private List<String> getColumns() {
        return extractColumns(TestTskvObject.class).stream()
                .map(c -> c.getColumnName())
                .collect(Collectors.toList());
    }

    private List<String> getGroupColumns() {
        return ImmutableList.of("Int8Value");
    }

    private TableConfig getTableConfigLeft() {
        TableConfig tableConfig = new TableConfig();
        tableConfig.setColumns(getColumns());
        tableConfig.setTableName("left");
        return tableConfig;
    }

    private TableConfig getTableConfigRight() {
        TableConfig tableConfig = new TableConfig();
        tableConfig.setColumns(getColumns());
        tableConfig.setTableName("right");
        return tableConfig;
    }

    private Map<String, String> getDefaultRow(Class<?> beanType) {
        return BeanUtils.extractColumns(beanType).stream()
                .collect(toMap(c -> c.getColumnName(), c -> Serialization.toDefaultString(c.getType(), c.getColumnType())));
    }

    @Test
    public void testCompareSingleLine() {
        TabCrunch tabCrunch = new TabCrunch(
                TskvInputSource2.builder()
                        .withStream(getClass().getResourceAsStream("/EmptySingleLine.tskv"))
                        .withDefaultRow(getDefaultRow(TestTskvObject.class))
                        .withTableConfig(getTableConfigLeft())
                        .build(),
                TskvInputSource2.builder()
                        .withStream(getClass().getResourceAsStream("/SingleLine.tskv"))
                        .withTableConfig(getTableConfigRight())
                        .build(),
                getColumns(),
                getGroupColumns());

        final boolean noDiff = tabCrunch.doDiff();

        Assert.assertTrue(noDiff);
        tabCrunch.getReport();
    }

    @Test
    public void testCompareMultiLine() {
        TabCrunch tabCrunch = new TabCrunch(
                TskvInputSource2.builder()
                        .withStream(getClass().getResourceAsStream("/EmptyMultiLine.tskv"))
                        .withDefaultRow(getDefaultRow(TestTskvObject.class))
                        .withTableConfig(getTableConfigLeft())
                        .build(),
                TskvInputSource2.builder()
                        .withStream(getClass().getResourceAsStream("/MultiLine.tskv"))
                        .withTableConfig(getTableConfigRight())
                        .build(),
                getColumns(),
                getGroupColumns());

        final boolean noDiff = tabCrunch.doDiff();

        Assert.assertTrue(noDiff);
        tabCrunch.getReport();
    }
}
