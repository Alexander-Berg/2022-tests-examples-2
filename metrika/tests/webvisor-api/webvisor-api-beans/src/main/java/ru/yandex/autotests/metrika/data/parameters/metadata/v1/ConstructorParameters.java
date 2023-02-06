package ru.yandex.autotests.metrika.data.parameters.metadata.v1;

import com.google.gson.Gson;
import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;

/**
 * Created by konkov on 05.08.2014.
 * Параметры вызова API метаданных
 */
public class ConstructorParameters extends AbstractFormParameters {

    @FormParameter("table")
    private TableEnum table;

    @FormParameter("sorted")
    private String sorted = "true";

    public String getSorted() {
        return sorted;
    }

    public void setSorted(String sorted) {
        this.sorted = sorted;
    }

    public ConstructorParameters withSorted(String sorted) {
        this.sorted = sorted;
        return this;
    }

    public ConstructorParameters withTable(TableEnum table) {
        setTable(table);
        return this;
    }

    public TableEnum getTable() {
        return table;
    }

    public void setTable(TableEnum table) {
        this.table = table;
    }

    @Override
    public String toString() {
        return (new Gson()).toJson(this);
    }
}
