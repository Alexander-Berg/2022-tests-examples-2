package ru.yandex.autotests.mainmorda.utils;

/**
 * User: ivannik
 * Date: 17.10.13
 * Time: 13:09
 */
public class WidgetCoordinates {
    private int column;
    private int row;

    public WidgetCoordinates(int column, int row) {
        this.column = column;
        this.row = row;
    }

    public void setRow(int row) {
        this.row = row;
    }

    public boolean hasCoordinates(int column, int row) {
        return this.column == column && this.row == row;
    }

    public boolean hasCoordinates(WidgetCoordinates coordinates) {
        return hasCoordinates(coordinates.getColumn(), coordinates.getRow());
    }

    public int getColumn() {
        return column;
    }

    public int getRow() {
        return row;
    }

    @Override
    public String toString() {
        return String.format("%d:%d", column, row);
    }
}
