package ru.yandex.autotests.metrika.data.parameters.management.v1;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.data.management.v1.counters.enums.CounterStatusEnum;
import ru.yandex.autotests.metrika.data.management.v1.counters.enums.CounterTypeEnum;
import ru.yandex.autotests.metrika.data.management.v1.counters.enums.CounterSortEnum;
import ru.yandex.autotests.metrika.data.report.v1.annotations.Name;

/**
 * Список доступных счетчиков
 * <p>
 * Created by proxeter on 24.07.2014.
 */
public class AvailableCountersParameters extends AbstractFormParameters {

    @Name("Функция обратного вызова, которая обрабатывает ответ API")
    @FormParameter("callback")
    private String callback;

    @Name("Фильтр по счетчикам, которые были добавлены в Избранные")
    @FormParameter("favorite")
    private Boolean favorite;

    @Name("Один или несколько дополнительных параметров возвращаемого объекта")
    @FormParameter("field")
    private String field;

    @Name("Порядковый номер счетчика, с которого начнется выдача списка счетчиков")
    @FormParameter("offset")
    private Integer offset;

    @Name("Количество счетчиков, которые вы хотите получить")
    @FormParameter("per_page")
    private Integer perPage;

    @Name("Фильтр по уровню доступа к счетчику")
    @FormParameter("permission")
    private String permission;

    @Name("Будут показаны счетчики, идентификатор, имя, сайт или зеркала которых содержат заданную подстроку")
    @FormParameter("search_string")
    private String search_string;

    @Name("Фильтр по статусу счетчика")
    @FormParameter("status")
    private CounterStatusEnum status;

    @Name("Фильтр по типу счетчика")
    @FormParameter("type")
    private CounterTypeEnum type;

    @FormParameter("sort")
    private CounterSortEnum sort;

    @FormParameter("reverse")
    private Boolean reverse;

    public String getCallback() {
        return callback;
    }

    public void setCallback(String callback) {
        this.callback = callback;
    }

    public Boolean getFavorite() {
        return favorite;
    }

    public void setFavorite(Boolean favorite) {
        this.favorite = favorite;
    }

    public String getField() {
        return field;
    }

    public void setField(String field) {
        this.field = field;
    }

    public Integer getOffset() {
        return offset;
    }

    public void setOffset(Integer offset) {
        this.offset = offset;
    }

    public Integer getPerPage() {
        return perPage;
    }

    public void setPerPage(Integer perPage) {
        this.perPage = perPage;
    }

    public String getPermission() {
        return permission;
    }

    public void setPermission(String permission) {
        this.permission = permission;
    }

    public String getSearch_string() {
        return search_string;
    }

    public void setSearchString(String search_string) {
        this.search_string = search_string;
    }

    public CounterStatusEnum getStatus() {
        return status;
    }

    public void setStatus(CounterStatusEnum status) {
        this.status = status;
    }

    public CounterTypeEnum getType() {
        return type;
    }

    public void setType(CounterTypeEnum type) {
        this.type = type;
    }

    public CounterSortEnum getSort() {
        return sort;
    }

    public void setSort(CounterSortEnum sort) {
        this.sort = sort;
    }

    public Boolean getReverse() {
        return reverse;
    }

    public void setReverse(Boolean reverse) {
        this.reverse = reverse;
    }

    public AvailableCountersParameters withType(CounterTypeEnum type) {
        this.type = type;
        return this;
    }

    public AvailableCountersParameters withCallback(String callback) {
        this.callback = callback;
        return this;
    }

    public AvailableCountersParameters withFavorite(Boolean favorite) {
        this.favorite = favorite;
        return this;
    }

    public AvailableCountersParameters withField(String field) {
        this.field = field;
        return this;
    }

    public AvailableCountersParameters withOffset(Integer offset) {
        this.offset = offset;
        return this;
    }

    public AvailableCountersParameters withPerPage(Integer perPage) {
        this.perPage = perPage;
        return this;
    }

    public AvailableCountersParameters withPermission(String permission) {
        this.permission = permission;
        return this;
    }

    public AvailableCountersParameters withSearchString(String search_string) {
        this.search_string = search_string;
        return this;
    }

    public AvailableCountersParameters withStatus(CounterStatusEnum status) {
        this.status = status;
        return this;
    }

    public AvailableCountersParameters withSort(CounterSortEnum sort) {
        this.sort = sort;
        return this;
    }

    public AvailableCountersParameters withReverse(Boolean reverse) {
        this.reverse = reverse;
        return this;
    }


}
