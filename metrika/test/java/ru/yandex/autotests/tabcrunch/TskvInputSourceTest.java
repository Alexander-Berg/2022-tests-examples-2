package ru.yandex.autotests.tabcrunch;

import org.junit.Test;
import ru.yandex.autotests.tabcrunch.config.TableConfig;
import ru.yandex.autotests.tabcrunch.input.InputSource;
import ru.yandex.autotests.tabcrunch.input.TskvInputSource;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;

import static org.hamcrest.Matchers.*;
import static org.junit.Assert.assertEquals;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.tabcrunch.TestDataUtils.*;
import static java.util.Arrays.asList;

/**
 * Author vkusny@yandex-team.ru
 * Date 06.10.15
 */
public class TskvInputSourceTest {

    public final static String EMPTY_COL = "empty_col";

    @Test
    public void getNextRow() {
        TableConfig tableConfig = new TableConfig();
        List<String> expectedRow = ALL_VALUES;
        InputSource source = new TskvInputSource(tableConfig, createInputStream(zipTskv(ALL_COLUMNS, ALL_VALUES)));
        source.setColumnsToSelect(ALL_COLUMNS);
        source.init();
        List<String> actualRow = source.getNextRow();
        assertEquals("Полученая строка должна совпадать со строкой из потока", actualRow, expectedRow);
    }

    @Test
    public void getNextTwoRows() {
        TableConfig tableConfig = new TableConfig();
        List<String> firstRowValues = ALL_VALUES;
        List<String> secondRowValues = new ArrayList<>(ALL_VALUES);
        secondRowValues.set(secondRowValues.size() - 1, OTHER_VAL);
        assumeThat("Первая и вторая строка долждны быть различны", firstRowValues, not(equalTo(secondRowValues)));
        InputStream stream = createInputStream(zipTskv(ALL_COLUMNS, firstRowValues), zipTskv(ALL_COLUMNS, secondRowValues));
        InputSource source = new TskvInputSource(tableConfig, stream);
        source.setColumnsToSelect(ALL_COLUMNS);
        source.init();
        List<String> firstActualRow = source.getNextRow();
        List<String> secondActualRow = source.getNextRow();
        assertEquals("Полученая первая строка должна соответствовать строке из потока", firstRowValues, firstActualRow);
        assertEquals("Полученая вторая строка должна соответствовать строке из потока", secondRowValues, secondActualRow);
    }

    @Test
    public void getAllColumns() {
        TableConfig tableConfig = new TableConfig();
        InputSource source = new TskvInputSource(tableConfig, createInputStream(zipTskv(ALL_COLUMNS, ALL_VALUES)));
        source.init();
        List<String> actualColumns = source.getAllColumns();
        assertEquals("Колонки должны соответствовать ключам в TSKV-строке", asSet(ALL_COLUMNS), asSet(actualColumns));
    }

    @Test
    public void getAllColumnsFromManyRows() {
        TableConfig tableConfig = new TableConfig();
        // первая строка без последней колонки
        int from = 0;
        int to = ALL_COLUMNS.size() - 1;
        List<String> firstRow = zipTskv(ALL_COLUMNS.subList(from, to), ALL_VALUES.subList(from, to));
        // вторая строка будет без первой колонки
        from = 1;
        to = ALL_COLUMNS.size();
        List<String> secondRow = zipTskv(ALL_COLUMNS.subList(from, to), ALL_VALUES.subList(from, to));
        // третья строка - только одна колонка
        from = 3;
        to = from + 1;
        List<String> thirdRow = zipTskv(ALL_COLUMNS.subList(from, to), ALL_VALUES.subList(from, to));
        InputSource source = new TskvInputSource(tableConfig, createInputStream(firstRow, secondRow, thirdRow));
        source.init();
        List<String> actualColumns = source.getAllColumns();
        assertEquals("Колонки должны соответствовать ключам в TSKV-строке", asSet(ALL_COLUMNS), asSet(actualColumns));
    }

    @Test
    public void getPartOfColumnsFromManyRows() {
        TableConfig tableConfig = new TableConfig();
        // первая строка без последних двух колонок
        int from = 0;
        int to = ALL_COLUMNS.size() - 2;
        List<String> firstRow = zipTskv(ALL_COLUMNS.subList(from, to), ALL_VALUES.subList(from, to));
        // вторая строка будет без первой и последней колонки
        from = 1;
        to = ALL_COLUMNS.size() - 1;
        List<String> secondRow = zipTskv(ALL_COLUMNS.subList(from, to), ALL_VALUES.subList(from, to));
        from = 0;
        to = ALL_COLUMNS.size() - 1;
        List<String> expectedColumns = ALL_COLUMNS.subList(from, to);
        InputSource source = new TskvInputSource(tableConfig, createInputStream(firstRow, secondRow));
        source.init();
        List<String> actualColumns = source.getAllColumns();
        assertEquals("Колонки должны соответствоват ключам в TSKV-строке", asSet(expectedColumns), asSet(actualColumns));
    }

    @Test
    public void setColumnsToSelectWithoutLast() {
        int from = 0;
        int to = ALL_COLUMNS.size() - 1;
        List<String> partOfColumns = ALL_COLUMNS.subList(from, to);
        List<String> partOfValues = ALL_VALUES.subList(from, to);
        TableConfig tableConfig = new TableConfig();
        InputSource source = new TskvInputSource(tableConfig, createInputStream(zipTskv(ALL_COLUMNS, ALL_VALUES)));
        source.setColumnsToSelect(partOfColumns);
        source.init();
        List<String> actualRow = source.getNextRow();
        assertEquals("Не должнго быть последнего поля", partOfValues, actualRow);
    }

    @Test
    public void setColumnsToSelectWithoutMid() {
        List<String> partOfColumns = new LinkedList<>(ALL_COLUMNS);
        partOfColumns.remove(partOfColumns.size() - 2);
        List<String> partOfValues = new LinkedList<>(ALL_VALUES);
        partOfValues.remove(partOfValues.size() - 2);
        TableConfig tableConfig = new TableConfig();
        InputSource source = new TskvInputSource(tableConfig, createInputStream(zipTskv(ALL_COLUMNS, ALL_VALUES)));
        source.setColumnsToSelect(partOfColumns);
        source.init();
        List<String> actualRow = source.getNextRow();
        assertEquals("Не должнго быть среднего поля", partOfValues, actualRow);
    }

    @Test
    public void setColumnsToSelectWithoutFirst() {
        int from = 1;
        int to = ALL_COLUMNS.size();
        List<String> partOfColumns = ALL_COLUMNS.subList(from, to);
        List<String> partOfValues = ALL_VALUES.subList(from, to);
        TableConfig tableConfig = new TableConfig();
        InputSource source = new TskvInputSource(tableConfig, createInputStream(zipTskv(ALL_COLUMNS, ALL_VALUES)));
        source.setColumnsToSelect(partOfColumns);
        source.init();
        List<String> actualRow = source.getNextRow();
        assertEquals("Не должнго быть первого поля", partOfValues, actualRow);
    }

    @Test
    public void columnWithoutValue() {
        List<String> row = zipTskv(ALL_COLUMNS, ALL_VALUES);
        row.add(EMPTY_COL);  // добавляем в строку ключ, без значения
        row.addAll(zipTskv(asList(OTHER_COL), asList(OTHER_VAL)));

        List<String> columns = new ArrayList<>(ALL_COLUMNS);
        columns.addAll(asList(EMPTY_COL, OTHER_COL));

        TableConfig tableConfig = new TableConfig();
        InputSource source = new TskvInputSource(tableConfig, createInputStream(row));
        source.setColumnsToSelect(columns);
        source.init();

        List<String> expectedValues = new ArrayList<>(ALL_VALUES);
        expectedValues.add(null);
        expectedValues.add(OTHER_VAL);
        List<String> actualRow = source.getNextRow();
        assertEquals("Значение для ключа без знака '=' должно быть null", expectedValues, actualRow);
    }

    @Test
    public void columnWithEmptyValue() {
        List<String> columns = new ArrayList<>(ALL_COLUMNS);
        columns.addAll(asList(EMPTY_COL, OTHER_COL));
        List<String> values = new ArrayList<>(ALL_VALUES);
        values.addAll(asList("", OTHER_VAL));

        TableConfig tableConfig = new TableConfig();
        InputSource source = new TskvInputSource(tableConfig, createInputStream(zipTskv(columns, values)));
        source.setColumnsToSelect(columns);
        source.init();

        List<String> actualRow = source.getNextRow();
        assertEquals("Пустое значение после знака '=' должно быть пустой строкой", values, actualRow);
    }
}
