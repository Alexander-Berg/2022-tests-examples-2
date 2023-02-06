package ru.yandex.autotests.metrika.data.report.v1.annotations;

/**
 * Чтобы не использовать HtmlElements @Name и не подключать эту зависимость
 * создаем свою аннотацию для описания наименования методов
 *
 * Created by proxeter (Nikolay Mulyar - proxeter@yandex-team.ru) on 23.06.2014.
 */
public @interface Name {

    String value();

}
