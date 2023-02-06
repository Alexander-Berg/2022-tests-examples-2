package ru.yandex.metrika.locale;

import java.util.Arrays;
import java.util.Collections;

import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.tool.AllDatabases;
import ru.yandex.metrika.util.locale.LocaleDictionaries;
import ru.yandex.metrika.util.locale.LocaleLangs;
import ru.yandex.metrika.util.log.Log4jSetup;

/**
 * @author jkee
 */

@Ignore
public class LocaleDecoderSimpleTest {

    LocaleDecoderSimple decoderSimple;

    @Before
    public void setUp() throws Exception {

        decoderSimple = new LocaleDecoderSimple();
        LocaleDictionaries dictionaries = new LocaleDictionaries();
        dictionaries.afterPropertiesSet();
        decoderSimple.setLocaleDictionaries(dictionaries);

        Log4jSetup.basicSetup();
        MySqlJdbcTemplate template = AllDatabases.getTemplate("localhost", 3308, "root", "qwerty", "conv_main");
        decoderSimple.setTableName("TraficSources");
        decoderSimple.setDescriptionColumnName("TraficSource");
        decoderSimple.setTemplate(template);
        decoderSimple.afterPropertiesSet();

    }

    @Test
    public void testIt() throws Exception {
        System.out.println(Arrays.toString(decoderSimple.eq(Collections.singletonList("Переходы по рекламе"), LocaleLangs.RU, null)));

    }
}
