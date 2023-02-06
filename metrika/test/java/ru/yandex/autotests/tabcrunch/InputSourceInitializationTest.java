package ru.yandex.autotests.tabcrunch;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.Ignore;
import org.junit.runner.RunWith;
import org.powermock.core.classloader.annotations.PrepareForTest;
import org.powermock.modules.junit4.PowerMockRunner;
import ru.yandex.autotests.tabcrunch.config.Config;
import ru.yandex.autotests.tabcrunch.config.TableConfig;
import ru.yandex.autotests.tabcrunch.input.*;

import java.util.ArrayList;
import java.util.List;

import static java.util.Arrays.asList;
import static org.junit.Assert.*;
import static org.mockito.Matchers.any;
import static org.powermock.api.mockito.PowerMockito.*;
import static org.mockito.Mockito.verify;
import static ru.yandex.autotests.tabcrunch.TestDataUtils.*;

/**
 * Создание источников данных
 * Author vkusny@yandex-team.ru
 * Date 27.04.15
 */
@PrepareForTest({
        InputSourceFactory.class // наблюдаем, т.к. в нём происходит создание InputSource
})
@RunWith(PowerMockRunner.class)
public class InputSourceInitializationTest {

    /**
     * Если не задано число колонок для выбора, выбирать все колонки для сравнения.<br/>
     * 1) Все InputSources инициализируем stub-ами, чтобы они возвращали одинаковый список колонок.<br/>
     * 2) Делаю конфиг, где у настроект таблиц набор колонок выставлен в null.<br/>
     * 3) Инициируем источники данных для сравнения.<br/>
     * Ожидания:<br/>
     * 1) Tab-crunch настроен так, чтобы выбирать все поля из таблиц.<br/>
     * 2) Источники данных созданы, инициализированы, для выборки используются все поля.
     * При этом был вызван метод инициализации источников данных, выбраны все поля таблицы и другого взаимодействия с источником не было.<br/>
     */
    @Test
    @Ignore
    public void columnListIsFilledAutomaticallyWhenNotSet() {
        // указываем InputSourceFactory создавать InputSource
        // который возвращает заданное число колонок
        final List<String> allColumns = ALL_COLUMNS;
        mockStatic(InputSourceFactory.class);
        when(InputSourceFactory.create(any(Config.class),any(TableConfig.class))).then(invocation -> {
            InputSource inputSourceMock = mock(InputSource.class);
            when(inputSourceMock.getAllColumns()).thenReturn(allColumns);
            return inputSourceMock;
        });

        Config config = createDummyConfig();
        config.getOldTable().setColumns(null);
        config.getNewTable().setColumns(null);
        TabCrunch crunch = new TabCrunch(config);
        assertEquals("Должны выбираться все колонки", crunch.getFieldsToSelect(), allColumns);
        InputSource leftSource = crunch.getInputLeft();
        InputSource rightSource = crunch.getInputRight();
        for (InputSource inputSource : asList(leftSource, rightSource)) {
            verify(inputSource).getAllColumns();
            verify(inputSource).init();
            verify(inputSource).setColumnsToSelect(allColumns);
            verifyNoMoreInteractions(inputSource);
        }
    }

    /**
     * Если в таблицах разный набор колонок, должны выбираться и проверятьс только общие колонки.
     * 1) InputSources инициализируем stub-ами, чтобы они возвращали разный список колонок, но с одинаковыми полями.
     * 2) Делаю конфиг, где у настроект таблиц набор колонок выставлен в null.<br/>
     * 3) Инициируем источники данных для сравнения.<br/>
     * Ожидания:<br/>
     * 1) Tab-crunch настроен так, чтобы выбирать только общие поля для сравнения.<br/>
     * 2) Источники данных созданы, инициализированы, для выборки используются олько общие поля.
     * При этом был вызван метод инициализации источников данных, выбраны все поля таблицы и другого взаимодействия с источником не было.<br/>
     */
    @Test
    @Ignore
    public void useOnlyCommonColumnsWhenNotSet() {
        // указываем InputSourceFactory создавать InputSource
        // который возвращает заданное число колонок
        final List<String> one_columns = ImmutableList.of(ID_COL, ONE_COL, TWO_COL, THREE_COL, FOUR_COL);
        final List<String> other_columns = ImmutableList.of(ID_COL, ONE_COL, TWO_COL, FOUR_COL, OTHER_COL);
        final List<String> commonColumns = ImmutableList.of(ID_COL, ONE_COL, TWO_COL, FOUR_COL);
        mockStatic(InputSourceFactory.class);
        InputSource oneInputSourceMock = mock(InputSource.class);
        when(oneInputSourceMock.getAllColumns()).thenReturn(one_columns);
        InputSource otherInputSourceMock = mock(InputSource.class);
        when(otherInputSourceMock.getAllColumns()).thenReturn(other_columns);
        when(InputSourceFactory.create(any(Config.class),any(TableConfig.class))).thenReturn(oneInputSourceMock, otherInputSourceMock);

        Config config = createDummyConfig();
        config.getOldTable().setColumns(null);
        config.getNewTable().setColumns(null);
        TabCrunch crunch = new TabCrunch(config);
        assertEquals("Должны выбираться только общие колонки", crunch.getFieldsToSelect(), commonColumns);
        InputSource leftSource = crunch.getInputLeft();
        InputSource rightSource = crunch.getInputRight();
        for (InputSource inputSource : asList(leftSource, rightSource)) {
            verify(inputSource).getAllColumns();
            verify(inputSource).init();
            verify(inputSource).setColumnsToSelect(commonColumns);
            verifyNoMoreInteractions(inputSource);
        }
    }

    /**
     * Если колонки указаны в настройках, не запрашивать из их БД
     */
    @Test
    @Ignore
    public void useColumnsFromConfigIfSet() {
        final List<String> commonColumns = ALL_COLUMNS;
        mockStatic(InputSourceFactory.class);
        when(InputSourceFactory.create(any(Config.class),any(TableConfig.class))).then(invocation -> mock(InputSource.class));

        Config config = createDummyConfig();
        config.getOldTable().setColumns(commonColumns);
        config.getNewTable().setColumns(commonColumns);
        TabCrunch crunch = new TabCrunch(config);
        assertEquals("Используются колонки из настроек таблицы", crunch.getFieldsToSelect(), commonColumns);
        InputSource leftSource = crunch.getInputLeft();
        InputSource rightSource = crunch.getInputRight();
        for (InputSource inputSource : asList(leftSource, rightSource)) {
            verify(inputSource).init();
            verify(inputSource).setColumnsToSelect(commonColumns);
            verifyNoMoreInteractions(inputSource);
        }
    }

    /**
     * Если колонки указаны в настройках и использовать только общие, не запрашивать из их БД
     */
    @Test
    @Ignore
    public void useCommonColumnsFromConfigIfSet() {
        final List<String> oneColumns = ImmutableList.of(ID_COL, ONE_COL, TWO_COL, THREE_COL, FOUR_COL);
        final List<String> otherColumns = ImmutableList.of(ID_COL, ONE_COL, TWO_COL, FOUR_COL, OTHER_COL);
        final List<String> commonColumns = ImmutableList.of(ID_COL, ONE_COL, TWO_COL, FOUR_COL);
        mockStatic(InputSourceFactory.class);
        when(InputSourceFactory.create(any(Config.class),any(TableConfig.class))).then(invocation -> mock(InputSource.class));

        Config config = createDummyConfig();
        config.getOldTable().setColumns(oneColumns);
        config.getNewTable().setColumns(otherColumns);
        TabCrunch crunch = new TabCrunch(config);
        assertEquals("Используются колонки из настроек таблицы", crunch.getFieldsToSelect(), commonColumns);
        InputSource leftSource = crunch.getInputLeft();
        InputSource rightSource = crunch.getInputRight();
        for (InputSource inputSource : asList(leftSource, rightSource)) {
            verify(inputSource).init();
            verify(inputSource).setColumnsToSelect(commonColumns);
            verifyNoMoreInteractions(inputSource);
        }
    }

    /**
     * InputSources инициализируются в конструкторе TabCrunch, если он вызыввется с объектом конфигураций
     */
    @Test
    @Ignore
    public void initInConstructorWithConfig() {
        mockStatic(InputSourceFactory.class);
        when(InputSourceFactory.create(any(Config.class),any(TableConfig.class))).then(invocation -> mock(InputSource.class));
        Config config = createDummyConfig();
        TabCrunch crunch = new TabCrunch(config);
        InputSource leftSource = crunch.getInputLeft();
        InputSource rightSource = crunch.getInputRight();
        for (InputSource inputSource : asList(leftSource, rightSource)) {
            verify(inputSource).init();
        }
    }

    /**
     * InputSources инициализируются в конструкторе TabCrunch, если он вызыввется c экземплярами InputSources
     */
    @Test
    @Ignore
    public void initInConstructorWithInputSources() {
        InputSource leftSource = mock(InputSource.class);
        when(leftSource.getConfig()).thenReturn(mock(TableConfig.class));
        InputSource rightSource= mock(InputSource.class);
        when(rightSource.getConfig()).thenReturn(mock(TableConfig.class));
        new TabCrunch(leftSource, rightSource, null, null);
        for (InputSource inputSource : asList(leftSource, rightSource)) {
            verify(inputSource).init();
        }
    }




}
