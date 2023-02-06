package ru.yandex.metrika.segments.core.query;

import org.junit.Test;

import ru.yandex.metrika.segments.core.parser.AbstractTest;
import ru.yandex.metrika.segments.core.parser.QueryParams;
import ru.yandex.metrika.util.Issue;


/**
 * TODO: добавить более вменяемые тесты
 * Добавим их в будущем. Сейчас этот класс проверяет про при рендеренге таких запросов мы хотя бы не кидаем исключения
 * И плюс их можно прямо тут в тесте напечатать, запихать в кликхаус и посмотреть что всё +- работает как надо.
 * Это далеко не лучшее применение для тестов, но жить оно точно не мешает, а будущем будет расширено
 */
@Issue(key = "METR-33587")
public class ArrayJoinBuilderTest extends AbstractTest {


    @Test
    public void buildArrayJoinTest() {
        QueryParams queryParams = builder()
                .metrics("ym:s:visits[ym:s:adfoxLoad!='0'],ym:s:adfoxLoads,ym:s:sumAdfoxPuidKey")
                .dimensions("ym:s:trafficSourceID,ym:s:adfoxBannerID,ym:s:adfoxPuidKey")
                .filtersBraces2("ym:s:trafficSourceID==1 and ym:s:adfoxBannerID==2017219 and ym:s:adfoxPuidKey>0")
                .startDate("2019-06-01")
                .endDate("2019-06-05")
                .counterId(153166)
                .limit(100);

        Query query = apiUtils.parseQuery(queryParams);
        var sql = query.buildSql();
        System.out.println(sql);
    }

    @Test
    public void buildArrayJoinTest2() {
        QueryParams queryParams = builder()
                .metrics("ym:s:visits,ym:s:users,ym:s:adfoxLoads")
                .dimensions("ym:s:adfoxPuidKeyName,ym:s:adfoxPuidValueName")
                .filtersBraces2("ym:s:adfoxPuidKey!n and ym:s:adfoxPuidValue!n")
                .startDate("2019-06-01")
                .endDate("2019-06-05")
                .counterId(153166)
                .limit(100);

        Query query = apiUtils.parseQuery(queryParams);
        var sql = query.buildSql();
        System.out.println(sql);
    }

    @Test
    public void buildArrayJoinTest3() {
        QueryParams queryParams = builder()
                .metrics("ym:s:visits,ym:s:users,ym:s:adfoxLoads")
                .dimensions("ym:s:adfoxPuidKeyName,ym:s:adfoxPuidValueName")
                .filtersBraces2("exists(ym:s:adfoxBannerID=='2017219')")
                .startDate("2019-06-01")
                .endDate("2019-06-05")
                .counterId(153166)
                .limit(100);

        Query query = apiUtils.parseQuery(queryParams);
        var sql = query.buildSql();
        System.out.println(sql);
    }

    @Test
    public void buildArrayJoinTest4() {
        QueryParams queryParams = builder()
                .metrics("ym:s:visits,ym:s:users,ym:s:adfoxLoads")
                .dimensions("ym:s:adfoxPuidKeyName,ym:s:adfoxPuidValueName")
                .filtersBraces2("ym:s:trafficSourceID==1 and ym:s:adfoxPuidKeyName=='Издание+Рубрика+Тема'")
                .startDate("2019-06-01")
                .endDate("2019-06-05")
                .counterId(153166)
                .limit(100);

        Query query = apiUtils.parseQuery(queryParams);
        var sql = query.buildSql();
        System.out.println(sql);
    }
}
