package ru.yandex.autotests.tabcrunch;

import com.google.common.collect.ImmutableList;
import ru.yandex.autotests.tabcrunch.config.Config;
import ru.yandex.autotests.tabcrunch.config.TableConfig;
import ru.yandex.autotests.tabcrunch.input.InputType;

import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.util.*;

import static java.util.Arrays.asList;
import static java.util.stream.Collectors.joining;

/**
 * Набор статических членов, чтобы не создавать константы и лишние методы для получения dummy-объектов
 * в каждом классе тестов
 * Author vkusny@yandex-team.ru
 * Date 14.05.15
 */
public class TestDataUtils {

    public final static String TSKV_ZIP_DELIMITER = "=";

    public final static String ID_COL = "identification";
    public final static String ONE_COL = "one";
    public final static String TWO_COL = "two";
    public final static String THREE_COL = "tree";
    public final static String FOUR_COL = "four";

    /**
     * Не входит в список {@code ALL_COLUMNS}
     */
    public final static String OTHER_COL = "other";

    public final static String ID_VAL = "id val";
    public final static String ONE_VAL = "first value";
    public final static String TWO_VAL = "second value";
    public final static String THREE_VAL = "third value";
    public final static String FOUR_VAL = "fourth value";

    /**
     * Не входит в список {@code ALL_VALUES}
     */
    public final static String OTHER_VAL = "other value";

    public final static List<String> ALL_COLUMNS = ImmutableList.of(ID_COL, ONE_COL, TWO_COL, THREE_COL, FOUR_COL);
    public final static List<String> ALL_VALUES = ImmutableList.of(ID_VAL, ONE_VAL, TWO_VAL, THREE_VAL, FOUR_VAL);

    public static Config createDummyConfig() {
        Config config = new Config();

        TableConfig oneTable = new TableConfig();
        oneTable.setTableName("fake_base.fake_table");
        oneTable.setLocation("fake_base_test.fake_table");
        // InputType может быть всё что угодно, это не влияет на результат
        oneTable.setInputType(InputType.MYSQL);
        oneTable.setFilterOutColumnsRegex(new ArrayList<>());
        oneTable.setAlias("one");

        TableConfig otherTable = new TableConfig();
        otherTable.setTableName("fake_base.fake_table");
        otherTable.setLocation("fake_base_stable.fake_table");
        // InputType может быть всё что угодно, это не влияет на результат
        otherTable.setInputType(InputType.MYSQL);
        otherTable.setFilterOutColumnsRegex(new ArrayList<>());
        otherTable.setAlias("other");

        config.setGroupCols(asList(ID_COL));
        config.setNewTable(oneTable);
        config.setOldTable(otherTable);

        return config;
    }

    public static List<String> zipTskv(List<String> left, List<String> right) {
        return zip(left, right, TSKV_ZIP_DELIMITER);
    }

    public static <T> Set<T> asSet(Collection<T> source) {
        return new HashSet<T>(source);
    }

    public static List<String> zip(List<String> left, List<String> right, String delimiter) {
        int maxSize = Math.max(left.size(), right.size());
        List<String> result = new ArrayList<>(maxSize);
        for (int i = 0; i < maxSize; i++) {
            String leftEl = (i < left.size()) ? left.get(i) : "";
            String rightEl = (i < right.size()) ? right.get(i) : "";
            result.add(leftEl + delimiter + rightEl);
        }
        return result;
    }

    public static InputStream createInputStream(List<String>... rows) {
        StringBuilder content = new StringBuilder();
        for (List<String> row : rows) {
            content.append(row.stream().collect(joining("\t")).concat("\n"));
        }
        return createInputStream(content.toString());
    }

    private static InputStream createInputStream(String content) {
        return new ByteArrayInputStream(content.getBytes());
    }

}
