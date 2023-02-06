package ru.yandex.autotests.mainmorda.utils;

import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static ch.lambdaj.Lambda.*;
import static ru.yandex.autotests.mainmorda.utils.WidgetPatternParameter.COLUMNSCOUNT;
import static ru.yandex.autotests.mainmorda.utils.WidgetPatternParameter.LAYOUTTYPE;
import static ru.yandex.autotests.mainmorda.utils.WidgetPatternParameter.REMOVED;

/**
 * User: ivannik
 * Date: 03.07.13
 * Time: 16:22
 */
public class WidgetPattern {

    public static final int DEFAULT_ADD_USR_CH = 1;
    public static final int DEFAULT_ADD_MIN_NUM_ID = 2;
    public static final int MIN_ADD_COLUMN = 3;
    public static final String FAKE_ETRAINS_WIDGET_ID = "_etrains-1";
    public static final List<String> DEFAULT_ROW_LAYOUT_WIDGETS =
            Arrays.asList("_geo", "_weather", "_afisha", "_services", "_tv", "_traffic");

    private Map<WidgetPatternParameter, String> parameters;
    private Map<String, WidgetProperties> widgets;
    private int[] columnSizes;

    private WidgetPattern() {
    }

    public static WidgetPattern createPatternFromString(String pattern) {
        WidgetPattern widgetPattern = new WidgetPattern();
        widgetPattern.parseParameters(pattern);
        widgetPattern.parseWidgetData(pattern);
        return widgetPattern;
    }

    public static WidgetPattern createPatternFromMap(Map<WidgetPatternParameter, String> parameters,
                                                     Map<String, WidgetProperties> widgets) {
        WidgetPattern widgetPattern = new WidgetPattern();
        widgetPattern.parameters = parameters;
        widgetPattern.widgets = widgets;
        int columnsCount = Integer.parseInt(parameters.get(COLUMNSCOUNT));
        widgetPattern.columnSizes = new int[columnsCount + 1];
        Arrays.fill(widgetPattern.columnSizes, 0);
        for (WidgetProperties prop : widgets.values()) {
            widgetPattern.columnSizes[prop.getCoord().getColumn()]++;
        }
        return widgetPattern;
    }

    private WidgetProperties findWidget(int column, int row) {
        return selectFirst(widgets.values(), having(on(WidgetProperties.class).getCoord().hasCoordinates(column, row)));
    }

    public static String getParameterValue(String fullPattern, WidgetPatternParameter parameter) {
        String parameterRegex = "(?<=\\Q" + parameter.name + "\\E=)[^&]*(?=(?:$|&))";
        Matcher parameterFinder = Pattern.compile(parameterRegex).matcher(fullPattern);
        if (parameterFinder.find()) {
            return parameterFinder.group();
        }
        System.out.println(parameterFinder.pattern().pattern());
        throw new AssertionError("Не найден параметр " + parameter);
    }

    private void parseParameters(String fullPattern) {
        String parameterRegex = "(?<=(?:^|&))(?!(?:widget=|coord=|usrCh=))([^&]+)=([^&]*)(?=(?:$|&))";
        Matcher parameterFinder = Pattern.compile(parameterRegex).matcher(fullPattern);
        parameters = new HashMap<WidgetPatternParameter, String>();
        while (parameterFinder.find()) {
            if (!parameterFinder.group(1).equals("yu")) {
                parameters.put(WidgetPatternParameter.getParameter(parameterFinder.group(1)), parameterFinder.group(2));
            }
        }
    }

    private void parseWidgetData(String fullPattern) {
        int columnsCount = Integer.parseInt(parameters.get(COLUMNSCOUNT));
        columnSizes = new int[columnsCount + 1];
        Arrays.fill(columnSizes, 0);
        String widgetRegex = "widget=((\\w*)-(\\d*))&coord=(\\d*):(\\d*)&usrCh=(\\d*)";
        Matcher widgetFinder = Pattern.compile(widgetRegex).matcher(fullPattern);
        widgets = new HashMap<String, WidgetProperties>();
        while (widgetFinder.find()) {
            String widgetFullId = widgetFinder.group(1);
            String widgetName = widgetFinder.group(2);
            int widgetNumId = Integer.parseInt(widgetFinder.group(3));
            int column = Integer.parseInt(widgetFinder.group(4));
            int row = Integer.parseInt(widgetFinder.group(5));
            int usrCh = Integer.parseInt(widgetFinder.group(6));
            if (!widgetFullId.equals(FAKE_ETRAINS_WIDGET_ID)) {
                columnSizes[column]++;
            }
            widgets.put(widgetFullId, new WidgetProperties(
                    widgetName,
                    widgetNumId,
                    new WidgetCoordinates(column, row),
                    usrCh
            ));
        }
    }

    public String addWidget(String widgetName) {
        int minColumn = MIN_ADD_COLUMN;
        int minRow = columnSizes[MIN_ADD_COLUMN];
        int columnsCount = columnSizes.length - 1;
        for (int col = MIN_ADD_COLUMN; col <= columnsCount; col++) {
            if (columnSizes[col] < minRow) {
                minColumn = col;
                minRow = columnSizes[col];
            }
        }
        WidgetCoordinates coordinates = new WidgetCoordinates(minColumn, minRow + 1);
        return addWidget(widgetName, coordinates);
    }

    public String addWidget(String widgetName, WidgetCoordinates coordinates) {
        int widgetNumId = DEFAULT_ADD_MIN_NUM_ID;
        while (widgets.containsKey(widgetName + Integer.toString(widgetNumId))) {
            widgetNumId++;
        }
        String widgetId = widgetName + "-" + Integer.toString(widgetNumId);
        widgets.put(widgetId, new WidgetProperties(
                widgetName,
                widgetNumId,
                coordinates,
                DEFAULT_ADD_USR_CH
        ));
        columnSizes[coordinates.getColumn()]++;
        if (widgets.containsKey(FAKE_ETRAINS_WIDGET_ID) && coordinates.getColumn() == MIN_ADD_COLUMN) {
            widgets.get(FAKE_ETRAINS_WIDGET_ID).getCoord().setRow(
                    widgets.get(FAKE_ETRAINS_WIDGET_ID).getCoord().getRow() + 1
            );
        }
        checkLayout();
        return widgetId;
    }

    public void deleteWidget(String widgetId) {
        WidgetProperties removedWidget = widgets.remove(widgetId);
        WidgetCoordinates removedCoordinates = removedWidget.getCoord();
        int column = removedCoordinates.getColumn();
        int columnSize = columnSizes[column];
        for (int row = removedWidget.getCoord().getRow() + 1; row <= columnSize; row++) {
            findWidget(column, row).getCoord().setRow(row - 1);
        }
        columnSizes[column]--;
        addToRemoveParametr(widgetId);
        if (widgets.containsKey(FAKE_ETRAINS_WIDGET_ID) && removedCoordinates.getColumn() == MIN_ADD_COLUMN) {
            widgets.get(FAKE_ETRAINS_WIDGET_ID).getCoord().setRow(
                    widgets.get(FAKE_ETRAINS_WIDGET_ID).getCoord().getRow() - 1
            );
        }
        checkLayout();
    }

    private void addToRemoveParametr(String widgetId) {
        if (parameters.get(REMOVED).length() > 0) {
            parameters.put(REMOVED, parameters.get(REMOVED) + "," + widgetId);
        } else {
            parameters.put(REMOVED, widgetId);
        }
    }

    public void moveWidget(String widgetId, WidgetCoordinates coordinates) {
        deleteWidget(widgetId);
        int col = coordinates.getColumn();
        int row = coordinates.getRow();
        WidgetProperties shiftWidget;
        while ((shiftWidget = findWidget(col, row)) != null) {
            shiftWidget.getCoord().setRow(++row);
        }
        widgets.get(widgetId).coord = coordinates;
        columnSizes[col]++;
        checkLayout();
    }

    public void checkLayout() {
        for (WidgetProperties wp : widgets.values()) {
            if (!DEFAULT_ROW_LAYOUT_WIDGETS.contains(wp.getName()) &&
                    !FAKE_ETRAINS_WIDGET_ID.equals(wp.getWidgetId()) &&
                    !isInLastRow(wp)) {
                System.out.println(wp);
                parameters.put(LAYOUTTYPE, "columns");
                return;
            }
        }
        parameters.put(LAYOUTTYPE, "rows");
    }

    private boolean isInLastRow(WidgetProperties wp) {
        int[] colSizeWithFake = Arrays.copyOf(columnSizes, columnSizes.length);
        int maxRowsCount = 0;
        for (int i = 3; i <= 5; i++) {
            if (maxRowsCount < colSizeWithFake[i]) {
                maxRowsCount = colSizeWithFake[i];
            }
        }
        return wp.getCoord().getColumn() <= 2 || maxRowsCount == wp.getCoord().getRow();
    }

    private int[] getColumnSizesWithFake() {
        int[] colSizeWithFake = Arrays.copyOf(columnSizes, columnSizes.length);
        if (widgets.containsKey(FAKE_ETRAINS_WIDGET_ID)) {
            colSizeWithFake[widgets.get(FAKE_ETRAINS_WIDGET_ID).getCoord().getColumn()]++;
        }
        return colSizeWithFake;
    }

    public void resetUsrShParameter(String widgetId) {
        WidgetProperties widget = widgets.get(widgetId);
        widget.usrCh = 0;
    }

    public void setEditWidget(String widgetId) {
        WidgetProperties widget = widgets.get(widgetId);
        System.out.println(widgetId);
        System.out.println(widgets);
        widget.usrCh = widget.usrCh | 2;
    }

    public void setMovedWidget(String widgetId) {
        WidgetProperties widget = widgets.get(widgetId);
        widget.usrCh = widget.usrCh | 1;
    }

    public void clearRemoved() {
        parameters.put(REMOVED, "");
    }

    public Map<String, WidgetProperties> getWidgets() {
        return widgets;
    }

    public Map<WidgetPatternParameter, String> getParameters() {
        return parameters;
    }

    @Override
    public String toString() {
        StringBuilder ret = new StringBuilder();
        ret.append("Pattern:{");
        for (Map.Entry<String, WidgetProperties> each : widgets.entrySet()) {
            ret.append(each.getKey()).append("(")
                    .append(each.getValue().getCoord())
                    .append(") ");
        }
        ret.append("}");
        return ret.toString();
    }
}
