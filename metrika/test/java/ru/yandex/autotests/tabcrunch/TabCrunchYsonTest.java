package ru.yandex.autotests.tabcrunch;

import java.io.BufferedInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.List;

import com.google.common.collect.ImmutableList;
import org.junit.Assert;
import org.junit.Test;

import ru.yandex.autotests.tabcrunch.config.TableConfig;
import ru.yandex.autotests.tabcrunch.input.YsonInputSource;

public class TabCrunchYsonTest {

    private static List<String> getColumns() {
        return ImmutableList.of(
                "LastSignificantTraficSourceClickTargetType",
                "Adfox_CampaignID",
                "PublisherEvents_MessengerID",
                "CounterID");
    }

    private static List<String> getGroupColumns() {
        return ImmutableList.of(
                "LastSignificantTraficSourceClickTargetType",
                "Adfox_CampaignID",
                "PublisherEvents_MessengerID",
                "CounterID");
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


    @Test
    public void testCompareMultiLine() {
        TabCrunch tabCrunch = new TabCrunch(
                new YsonInputSource(getTableConfigLeft(), getClass().getResourceAsStream("/actual.yson")),
                new YsonInputSource(getTableConfigRight(), getClass().getResourceAsStream("/expected.yson")),
                getColumns(),
                getGroupColumns());

        final boolean noDiff = tabCrunch.doDiff();

        Assert.assertTrue(noDiff);
        tabCrunch.getReport();
    }
}
