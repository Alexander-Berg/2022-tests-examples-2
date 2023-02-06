package ru.yandex.autotests.mainmorda.utils;

/**
 * User: ivannik
 * Date: 17.10.13
 * Time: 13:09
 */
public class WidgetProperties {
    public String idName;
    public int idNum;
    public int usrCh;
    public WidgetCoordinates coord;

    public WidgetProperties(String idName, int idNum, WidgetCoordinates coord, int usrCh) {
        this.idName = idName;
        this.idNum = idNum;
        this.usrCh = usrCh;
        this.coord = coord;
    }

    public String getWidgetId() {
        return idName + "-" + idNum;
    }

    public String getName() {
        return idName;
    }

    public WidgetCoordinates getCoord() {
        return coord;
    }

    @Override
    public String toString() {
        return String.format("%s(%s;usrCh:%s)", getWidgetId(), coord, usrCh);
    }

    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof WidgetProperties)) {
            return false;
        }
        WidgetProperties prop = (WidgetProperties) obj;
        return isFieldsEquals(prop);
    }

    private boolean isFieldsEquals(WidgetProperties prop) {
        return this.getWidgetId().equals(prop.getWidgetId()) &&
                this.usrCh == prop.usrCh &&
                this.coord.hasCoordinates(prop.coord);
    }

    @Override
    public int hashCode() {
        return idName.hashCode() + idNum + usrCh + coord.getRow() + coord.getColumn();
    }
}
