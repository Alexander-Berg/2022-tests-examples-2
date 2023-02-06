package ru.yandex.metrika.api.management.client.external.logs;

import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.junit.Ignore;

import ru.yandex.clickhouse.settings.ClickHouseProperties;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplate;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplateFactory;
import ru.yandex.metrika.dbclients.clickhouse.MetrikaClickHouseProperties;
import ru.yandex.metrika.dbclients.mysql.RowMappers;
import ru.yandex.metrika.util.collections.F;
import ru.yandex.metrika.util.locale.LocaleDictionaries;
import ru.yandex.metrika.util.route.RouteConfigSimple;

import static ru.yandex.metrika.api.management.client.external.logs.LogRequestFields.HITS_COUNT_QUERY_TEMPLATE;
import static ru.yandex.metrika.api.management.client.external.logs.LogRequestFields.HITS_LOG_QUERY_TEMPLATE;
import static ru.yandex.metrika.api.management.client.external.logs.LogRequestFields.VISITS_COUNT_QUERY_TEMPLATE;
import static ru.yandex.metrika.api.management.client.external.logs.LogRequestFields.VISITS_LOG_QUERY_TEMPLATE;
/**
 * Created by vesel4ak-u on 16.11.16.
 */
@Ignore("METRIQA-936")
public class LogRequestFieldsTest {
    private static HttpTemplate setupMtlogLayer1() {
        ClickHouseProperties properties = new MetrikaClickHouseProperties();
        properties.setSocketTimeout(100000);
        properties.setConnectionTimeout(100000);
        RouteConfigSimple route = new RouteConfigSimple("localhost", 31123);
        return new HttpTemplateFactory().getTemplate(route, properties);
    }

    private static LogRequestFields logRequestFields;

    public static void main(String[] args) throws Exception {
        logRequestFields = new LogRequestFields();
        logRequestFields.setInitHitFields(new InitHitFields());
        logRequestFields.setInitVisitFields(new InitVisitFields());
        logRequestFields.afterPropertiesSet();
        generateVisitsDocs("en");
    }

    private static void soutSpaces(int n) {
        for (int i = 0; i < n; ++i) {
            System.out.print(" ");
        }
    }

    private static void m8() throws Exception {
        String queryTemplate = "select Referer from test.visits where VisitID=7059745750720448370";
//        HttpTemplate template = setupMtlogLayer1();
        ClickHouseProperties properties = new MetrikaClickHouseProperties();
        RouteConfigSimple route = new RouteConfigSimple("localhost", 8123);
        HttpTemplate template = new HttpTemplateFactory().getTemplate(route, properties);
        List<String> rows = template.query(queryTemplate, (ResultSet rs, int rowNum) -> rs.getString(1));
        for (String row : rows) {
            System.out.println(row);
        }
    }


    private static void generateHitsDocs(String lang) throws Exception {
        LocaleDictionaries ld = new LocaleDictionaries();
        ld.afterPropertiesSet();
        for (int i = 0; i < logRequestFields.hitFieldDescriptions.size(); ++i) {
            soutSpaces(20);
            System.out.printf("<row id=\"row%d\">%n", i);
            soutSpaces(24);
            System.out.printf("<entry>%s</entry>%n", logRequestFields.hitFields.get(i));
            soutSpaces(24);
            System.out.printf("<entry>%s</entry>%n", ld.keyToLocal(lang, logRequestFields.hitFieldDescriptions.get(i)));
            soutSpaces(20);
            System.out.println("</row>");
        }
    }

    private static void generateVisitsDocs(String lang) throws Exception {
        LocaleDictionaries ld = new LocaleDictionaries();
        ld.afterPropertiesSet();
        for (int i = 0; i < logRequestFields.visitFieldDescriptions.size(); ++i) {
            soutSpaces(20);
            System.out.printf("<row id=\"row%d\">%n", i);
            soutSpaces(24);
            System.out.printf("<entry>%s</entry>%n", logRequestFields.visitFields.get(i));
            soutSpaces(24);
            System.out.printf("<entry>%s</entry>%n", ld.keyToLocal(lang, logRequestFields.visitFieldDescriptions.get(i)));
            soutSpaces(20);
            System.out.println("</row>");
        }
    }

    private static void m6() throws Exception {
        List<String> l = new ArrayList<>();
        for (int i = 0; i <= 115; ++i) {
            l.add(String.format("select %d as id, dictGetString('SearchEngine', 'value', toUInt64(%d)) as SearchEngineName from visits_layer limit 1", i, i));
        }
        String query = F.join(l, " union all ");
        System.out.println(query);

        l.clear();
        for (int i = 116; i <= 231; ++i) {
            l.add(String.format("select %d as id, dictGetString('SearchEngine', 'value', toUInt64(%d)) as SearchEngineName from visits_layer limit 1", i, i));
        }
        query = F.join(l, " union all ");
        System.out.println(query);
    }

    private static void m4() throws Exception {
        LocaleDictionaries localeDictionaries = new LocaleDictionaries();
        localeDictionaries.afterPropertiesSet();
        List<String> trafficSources = Arrays.asList("Внутренние переходы", "Прямые заходы", "Переходы по ссылкам на сайтах", "Переходы из поисковых систем", "Переходы по рекламе", "Переходы с сохранённых страниц",
                "Не определён",
                "Переходы по внешним ссылкам",
                "Переходы с почтовых рассылок",
                "Переходы из социальных сетей");
        for (String source : trafficSources) {
            System.out.println(localeDictionaries.keyToLocal("en", source));
        }
    }

    /*    .plus1("Ключевая фраза"                    , "phrase"      ,  1L)
        .plus1("Условие показа объявления"               , "retargeting" ,  2L)
        .plus1("Автоматически добавленные фразы"    , "additional"  ,  3L) // 4
        .plus1("Условие нацеливания"    , "performance"  ,  7L), // 8
        0   Не определено
        8 не определено
    */
    private static void m5() throws Exception {
        LocaleDictionaries localeDictionaries = new LocaleDictionaries();
        localeDictionaries.afterPropertiesSet();
        List<String> lastDirectConditionTypes = Arrays.asList(
                "Ключевая фраза", "Условие показа объявления", "Автоматически добавленные фразы", "Условие нацеливания", "Не определено");
        for (String type : lastDirectConditionTypes) {
            System.out.println(localeDictionaries.keyToLocal("en", type));
        }
    }



    private static void m3() {
        System.out.println(HITS_LOG_QUERY_TEMPLATE);
        System.out.println(VISITS_LOG_QUERY_TEMPLATE);

        System.out.println(HITS_COUNT_QUERY_TEMPLATE);
        System.out.println(VISITS_COUNT_QUERY_TEMPLATE);
    }

    private static void m2() {
        System.out.println(F.join(logRequestFields.visitFields, ","));
    }

    private static void m1() {
        //        String queryTemplate = "select ceil(sum(length(toString(%s))) / count()) from hits_layer where EventDate>=toDate('2016-10-01') and EventDate<=toDate('2016-10-01')";
        String queryTemplate = "select ceil(sum(length(toString(%s))) / count()) from visits_layer where StartDate>=toDate('2016-10-01') and StartDate<=toDate('2016-10-01')";

        HttpTemplate template = setupMtlogLayer1();

        for (String field : logRequestFields.visitFields) {
//        for (String field : hitFields) {
            if (logRequestFields.visitFieldLengthMap.get(field) > 0) {
//            if (hitFieldLengthMap.get(field) > 0) {
                continue;
            }
//        for (String field : new String[]{"ym:pv:browserMinorVersion"}) {
            String sql = logRequestFields.visitFieldSqlMap.get(field).asSql();
//            String sql = hitFieldSqlMap.get(field);
            int k = template.queryForInt(String.format(queryTemplate, sql));
            System.out.println(field + " " + k);
        }
    }

    private static void checkCHSqlSyntax(){
        String visitsQueryTemplate = "select toString(%s) from visits_layer where StartDate>=toDate('2016-10-01') and StartDate<=toDate('2016-10-01') and CounterID=34 limit 1";
        HttpTemplate template = setupMtlogLayer1();
        for (String field:logRequestFields.visitFields){
            String fieldSql=logRequestFields.visitFieldSqlMap.get(field).asSql();
            try{
                template.query(String.format(visitsQueryTemplate,fieldSql),RowMappers.STRING);
            }catch (Exception e){
                System.out.println("error on "+field+" "+fieldSql+e.getMessage());
            }
        }
        String hitsQueryTemplate = "select toString(%s) from hits_layer where CounterID=34 limit 1";
        for (String field:logRequestFields.hitFields){
            String fieldSql=logRequestFields.hitFieldSqlMap.get(field).asSql();
            try{
                template.query(String.format(hitsQueryTemplate,fieldSql),RowMappers.STRING);
            }catch (Exception e){
                System.out.println("error on "+field+" "+fieldSql+e.getMessage());
            }
        }
        System.out.println("syntax check is over");
    }

}
