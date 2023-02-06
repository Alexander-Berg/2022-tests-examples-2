package ru.yandex.autotests.tabcrunch;

import org.junit.Test;
import org.junit.Ignore;
import org.junit.runner.RunWith;
import org.powermock.core.classloader.annotations.PrepareForTest;
import org.powermock.modules.junit4.PowerMockRunner;
import ru.yandex.autotests.tabcrunch.config.Config;
import ru.yandex.autotests.tabcrunch.config.TableConfig;
import ru.yandex.autotests.tabcrunch.input.InputSource;
import ru.yandex.autotests.tabcrunch.input.InputSourceFactory;

import java.util.ArrayList;
import java.util.List;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.mockito.Matchers.any;
import static org.powermock.api.mockito.PowerMockito.*;
import static ru.yandex.autotests.tabcrunch.TestDataUtils.*;

/**
 * Тесты на реакцию tab-crunch на различные строки входных ханных
 * Author vkusny@yandex-team.ru
 * Date 08.05.15
 */
@PrepareForTest({
        InputSourceFactory.class // наблюдаем, т.к. в нём происходит создание InputSource
})
@RunWith(PowerMockRunner.class)
public class ComparisonTest {

    @Test
    @Ignore
    public void sameFieldsWithNullInTheMiddle() {
        // указываем InputSourceFactory создавать InputSource
        // который возвращает заданное число колонок
        final List<String> allColumns = ALL_COLUMNS;
        mockStatic(InputSourceFactory.class);

        // делаем 2 заглушки которые сначала возвращают строку, потом null
        List<String> row = new ArrayList<>(ALL_VALUES);
        row.set(row.size() - 2, null);
        InputSource oneInputSourceMock = mock(InputSource.class);
        when(oneInputSourceMock.getNextRow()).thenReturn(new ArrayList<>(row), null);
        InputSource otherInputSourceMock = mock(InputSource.class);
        when(otherInputSourceMock.getNextRow()).thenReturn(new ArrayList<>(row), null);
        when(InputSourceFactory.create(any(Config.class), any(TableConfig.class))).thenReturn(oneInputSourceMock, otherInputSourceMock);

        Config config = createDummyConfig();
        config.getOldTable().setColumns(allColumns);
        config.getNewTable().setColumns(allColumns);
        TabCrunch crunch = new TabCrunch(config);
        crunch.doDiff();
        assertFalse("При сравнение одинакового набора полей, среди которых есть null, " +
                "различий быть не должно", crunch.getHasDiff());
    }

    @Test
    @Ignore
    public void differentFieldsWithNullInTheMiddle() {
        // указываем InputSourceFactory создавать InputSource
        // который возвращает заданное число колонок
        final List<String> all_columns = ALL_COLUMNS;
        mockStatic(InputSourceFactory.class);
        // делаем 2 заглушки которые сначала возвращают строку, потом null
        List<String> oneRow = new ArrayList<>(ALL_VALUES);
        oneRow.set(oneRow.size() - 2, null);
        List<String> otherRow = new ArrayList<>(ALL_VALUES);
        otherRow.set(oneRow.size() - 2, null);
        otherRow.set(oneRow.size() - 1, OTHER_VAL);
        InputSource oneInputSourceMock = mock(InputSource.class);
        when(oneInputSourceMock.getNextRow()).thenReturn(oneRow, null);
        InputSource otherInputSourceMock = mock(InputSource.class);
        when(otherInputSourceMock.getNextRow()).thenReturn(otherRow, null);
        when(InputSourceFactory.create(any(Config.class), any(TableConfig.class))).thenReturn(oneInputSourceMock, otherInputSourceMock);

        Config config = createDummyConfig();
        config.getOldTable().setColumns(all_columns);
        config.getNewTable().setColumns(all_columns);
        TabCrunch crunch = new TabCrunch(config);
        crunch.doDiff();
        assertTrue("При сравнении полей с разными значениями, среди которых есть null в одинаковых полях" +
                ", должны сущуствовать различия", crunch.getHasDiff());
    }

}
