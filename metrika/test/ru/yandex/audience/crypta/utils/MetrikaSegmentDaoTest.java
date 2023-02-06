package ru.yandex.audience.crypta.utils;

import java.util.List;

import org.apache.logging.log4j.Level;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.dbclients.mysql.RowMappers;
import ru.yandex.metrika.segments.ApiUtilsTests;
import ru.yandex.metrika.segments.core.ApiUtils;
import ru.yandex.metrika.segments.core.parser.filter.FBFilter;
import ru.yandex.metrika.segments.core.parser.filter.FBFilterTransformers;
import ru.yandex.metrika.segments.core.parser.filter.FilterParserBraces2;
import ru.yandex.metrika.segments.core.schema.TableEntity;
import ru.yandex.metrika.segments.site.schema.TableSchemaSite;
import ru.yandex.metrika.tool.AllDatabases;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;
import ru.yandex.metrika.util.log.Log4jSetup;

import static org.junit.Assert.assertEquals;

/**
 * Created by orantius on 29.10.16.
 */
@Ignore("METRIQA-936")
public class MetrikaSegmentDaoTest {

    private MySqlJdbcTemplate template;
    private ApiUtils apiUtils;

    @Before
    public void setUp() throws Exception {
        Log4jSetup.basicSetup(Level.INFO);
        template = AllDatabases.getTemplate("localhost", 3311, "metrika", XmlPropertyConfigurer.getTextFromFile("~/.mysql/pass_old"), "conv_main");
        ApiUtilsTests.setUp();
        apiUtils = ApiUtilsTests.apiUtils;

    }

    @Test
    public void wrap() {
        List<String> query = template.query("select expression from segments", RowMappers.STRING);
        TableEntity visits = new TableEntity(TableSchemaSite.VISITS);
        FilterParserBraces2 filterParser = (FilterParserBraces2) apiUtils.getFilterParser();
        for (String arg : query) {
            if(arg!=null) {
                FBFilter parsed = filterParser.buildSimpleAST(arg, TableSchemaSite.VISITS);
                String res = FBFilterTransformers.wrapForTable(parsed, visits).toString();
                System.out.println(res +" <- "+arg);
            }
        }
    }

    @Test
    public void wrapSpecific(){
        String filter = "(ym:pv:URL=*'https://metrika.yandex.ru/list') and (ym:s:goal12544996IsReached=='Yes') " +
                "and (ym:el:externalLink=*'sdfsdf') and (ym:pv:title=*'sdfsdfsfsdfsdf') and (ym:s:pageViews>34)";
        TableEntity visits = new TableEntity(TableSchemaSite.VISITS);
        FilterParserBraces2 filterParser = (FilterParserBraces2) apiUtils.getFilterParser();
        FBFilter parsed = filterParser.buildSimpleAST(filter, TableSchemaSite.VISITS);
        String res = FBFilterTransformers.wrapForTable(parsed, visits).toString();
        assertEquals("wrong wrapping filter",
                "((ym:pv:title =* 'sdfsdfsfsdfsdf') AND (ym:el:externalLink =* 'sdfsdf') " +
                        "AND (ym:pv:URL =* 'https://metrika.yandex.ru/list')) " +
                        "AND (EXISTS (ym:s:pageViews > '34' AND ym:s:goal12544996IsReached == 'Yes'))",
                res);

    }
}
