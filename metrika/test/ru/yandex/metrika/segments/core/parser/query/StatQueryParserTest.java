package ru.yandex.metrika.segments.core.parser.query;

import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.segments.core.parser.filter.FilterParserBraces2Test;


/**
 * Created by orantius on 12.05.16.
 */
@Ignore
public class StatQueryParserTest {
    StatQueryParser parser;
    @Before
    public void setUp() throws Exception {
        parser = new StatQueryParser();
        parser.setApiUtils(FilterParserBraces2Test.getApiUtils());
    }


    @Test
    public void testError() throws Exception {
        String source = "select ym:s:visits, ym:s:hits " +
                "from visits " +
                "where ym:s:regionCountry==213 group by ym:s:gender " +
                "order by -ym:s:visits ";
        for (int i = 0; i < source.length(); i++) {
            String test = source.substring(0, i);
            try {
                StatApiQuery parse = parser.parse(test);
                System.out.println("query = " + test);
            } catch (Exception e) {
                System.err.println("query = " + test);
                e.printStackTrace();
                // когда mismatched input '<EOF>' expecting IDENTIFIER - мы знаем что должно быть.
                // line 1:0 no viable alternative at input 'se' - видимо нужно follow set для всех токенов.

            }
        }
    }

    @Test
    public void testParse() throws Exception {

            StatApiQuery parsed = parser.parse("select ym:s:visits, ym:s:hits " +
                    "from visits " +
                    "where ym:s:regionCountry==213 group by ym:s:gender " +
                    "order by -ym:s:visits ");
            System.out.println("parsed = " + parsed);


    }
}
