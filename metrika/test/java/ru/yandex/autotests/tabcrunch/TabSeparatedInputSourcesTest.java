package ru.yandex.autotests.tabcrunch;

import org.apache.commons.io.IOUtils;
import org.junit.Test;
import ru.yandex.autotests.tabcrunch.config.TableConfig;
import ru.yandex.autotests.tabcrunch.input.InputSource;
import ru.yandex.autotests.tabcrunch.input.TabSeparatedInputSource;

import java.util.*;

import static org.junit.Assert.*;
import static org.junit.Assume.*;

import static ru.yandex.autotests.tabcrunch.TestDataUtils.*;

import static org.hamcrest.Matchers.*;

/**
 * Author vkusny@yandex-team.ru
 * Date 13.05.15
 */
public class TabSeparatedInputSourcesTest {

    @Test
    public void getNextRow() {
        TableConfig tableConfig = new TableConfig();
        List<String> expectedRow = ALL_VALUES;
        InputSource source = new TabSeparatedInputSource(tableConfig, createInputStream(expectedRow));
        source.init();
        List<String> actualRow = source.getNextRow();
        assertEquals("Полученая строка должна соответствовать строке из потока", actualRow, expectedRow);
    }

    @Test
    public void getNextTwoRows() {
        TableConfig tableConfig = new TableConfig();
        List<String> firstRow = ALL_VALUES;
        List<String> secondRow = new ArrayList<>(ALL_VALUES);
        secondRow.set(secondRow.size() - 1, OTHER_VAL);
        assumeThat("первая и вторая строка долждны быть различны", firstRow, not(equalTo(secondRow)));
        InputSource source = new TabSeparatedInputSource(tableConfig, createInputStream(firstRow, secondRow));
        source.init();
        List<String> firstActualRow = source.getNextRow();
        List<String> secondActualRow = source.getNextRow();
        assertEquals("Полученая первая должна соответствовать строке из потока", firstRow, firstActualRow);
        assertEquals("Полученая вторая должна соответствовать строке из потока", secondRow, secondActualRow);
    }

    @Test
    public void getAllColumns() {
        TableConfig tableConfig = new TableConfig();
        List<String> expectedRow = ALL_VALUES;
        InputSource source = new TabSeparatedInputSource(tableConfig, createInputStream(expectedRow));
        source.init();
        List<String> actualColumns = source.getAllColumns();
        assertThat("Длинна списка колонок должна быть равна числу полей строки",
                actualColumns, hasSize(expectedRow.size()));
    }

    @Test
    public void setColumnsToSelectWithoutLast() {
        List<String> allColumns = ALL_COLUMNS;
        List<String> partOfColumns = allColumns.subList(0, allColumns.size() - 1);
        List<String> allValues = ALL_VALUES;
        List<String> partOfValues = allValues.subList(0, allValues.size() - 1);
        TableConfig tableConfig = new TableConfig();
        tableConfig.setColumns(allColumns);
        InputSource source = new TabSeparatedInputSource(tableConfig, createInputStream(allValues));
        source.setColumnsToSelect(partOfColumns);
        source.init();
        List<String> actualRow = source.getNextRow();
        assertEquals("Не должно быть последнего поля", partOfValues, actualRow);
    }

    @Test
    public void setColumnsToSelectWithoutMid() {
        List<String> allColumns = ALL_COLUMNS;
        List<String> partOfColumns = new LinkedList<>(allColumns);
        partOfColumns.remove(partOfColumns.size() - 2);
        List<String> allValues = ALL_VALUES;
        List<String> partOfValues = new LinkedList<>(allValues);
        partOfValues.remove(partOfValues.size() - 2);
        TableConfig tableConfig = new TableConfig();
        tableConfig.setColumns(allColumns);
        InputSource source = new TabSeparatedInputSource(tableConfig, createInputStream(allValues));
        source.setColumnsToSelect(partOfColumns);
        source.init();
        List<String> actualRow = source.getNextRow();
        assertEquals("Не должно быть среднего поля", partOfValues, actualRow);
    }

    @Test
    public void setColumnsToSelectWithoutFirst() {
        List<String> allColumns = ALL_COLUMNS;
        List<String> partOfColumns = allColumns.subList(1, allColumns.size() - 1);
        List<String> allValues = ALL_VALUES;
        List<String> partOfValues = allValues.subList(1, allValues.size() - 1);
        TableConfig tableConfig = new TableConfig();
        tableConfig.setColumns(allColumns);
        InputSource source = new TabSeparatedInputSource(tableConfig, createInputStream(allValues));
        source.setColumnsToSelect(partOfColumns);
        source.init();
        List<String> actualRow = source.getNextRow();
        assertEquals("Не должно быть первого поля", partOfValues, actualRow);
    }

    @Test
    public void emptySource() {
        TableConfig tableConfig = new TableConfig();
        InputSource source = new TabSeparatedInputSource(tableConfig, IOUtils.toInputStream(""));
        source.init();
        List<String> actualRow = source.getNextRow();
        assertEquals("Полученая строка должна соответствовать строке из потока", actualRow, null);
    }

}
