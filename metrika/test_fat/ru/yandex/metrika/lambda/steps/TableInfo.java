package ru.yandex.metrika.lambda.steps;

import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import ru.yandex.inside.yt.kosher.cypress.YPath;

class TableInfo {

    private static Pattern R = Pattern.compile("^(?<head>.+)(\\d{14})(?<tail>_\\d{14}.*)$");

    private YPath table;
    private List<String> columns;
    private List<String> groupColumns;

    public TableInfo(YPath table, List<String> columns, List<String> groupColumns) {
        this.table = table;
        this.columns = columns;
        this.groupColumns = groupColumns;
    }

    public YPath getTable() {
        return table;
    }

    public YPath getTableConstant() {
        final Matcher matcher = R.matcher(table.toString());
        if (matcher.matches()) {
            return YPath.simple(String.format("%s##############%s", matcher.group("head"), matcher.group("tail")));
        } else {
            return getTable();
        }
    }

    public List<String> getColumns() {
        return columns;
    }

    public List<String> getGroupColumns() {
        return groupColumns;
    }
}
