package ru.yandex.metrika.segments.clickhouse.grammar;

import java.util.Date;
import java.util.List;

import org.antlr.v4.runtime.ANTLRInputStream;
import org.antlr.v4.runtime.BailErrorStrategy;
import org.antlr.v4.runtime.CommonTokenStream;
import org.antlr.v4.runtime.RecognitionException;
import org.apache.logging.log4j.Level;
import org.joda.time.LocalDate;

import ru.yandex.metrika.dbclients.clickhouse.HttpTemplateImpl;
import ru.yandex.metrika.dbclients.mysql.RowMappers;
import ru.yandex.metrika.segments.clickhouse.meta.MetaUtils;
import ru.yandex.metrika.segments.clickhouse.parse.ClickHouseLexer;
import ru.yandex.metrika.segments.clickhouse.parse.ClickHouseParser;
import ru.yandex.metrika.util.log.Log4jSetup;
import ru.yandex.metrika.util.time.DateTimeFormatters;
import ru.yandex.metrika.util.time.DateTimeUtils;

/**
 * Created by orantius on 3/30/15.
 */
public class GWork {
    public static void main(String[] args) throws Exception {
        Log4jSetup.basicSetup(Level.DEBUG);
        //ServerMeta serverMeta = MetaUtils.getMetaUtils().buildMeta();
        //NameChecker nameChecker = new NameChecker(serverMeta);

        HttpTemplateImpl httpTemplate = MetaUtils.getHttpTemplate();
        // 10M queries/day, 5Gb size.
        List<LocalDate> days = DateTimeUtils.getDaysInInterval(new LocalDate(2015, 11, 13), new LocalDate(2015, 11, 22));
        for (LocalDate day : days) {
            String date = DateTimeFormatters.ISO_DTF.print(day);
            int count = httpTemplate.queryForObject("select count() from stats.clickhouse where EventDate = '"+date+"' ", RowMappers.INTEGER);
            for (int i = 0; i < count; i+=100000) {
                List<String> z = httpTemplate.query("select Query from stats.clickhouse where EventDate = '"+date+"' limit "+i+", "+100000, RowMappers.STRING);
                int zz = 0;
                for (String query : z) {
                    zz++;
                    if(zz % 1000==0) {
                        System.out.println(new Date()+", i = " + (zz+i)+" // "+ date);
                    }
                    ClickHouseLexer liteLexer = new ClickHouseLexer(new ANTLRInputStream(query));
                    CommonTokenStream tokens = new CommonTokenStream(liteLexer);
                    ClickHouseParser parser = new ClickHouseParser(tokens);
                    parser.setErrorHandler(new BailErrorStrategy());
                    try {
                        ClickHouseParser.ParseContext parse = parser.parse();
                    } catch (RecognitionException e) {
                        System.out.println("query = " + query);
                        e.printStackTrace();
                    }
                    //System.out.println();
                }
            }
        }
    }
}
