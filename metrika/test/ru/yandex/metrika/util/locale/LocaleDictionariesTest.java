package ru.yandex.metrika.util.locale;

import org.junit.Ignore;
import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;

/**
 * @author jkee
 */

@Ignore //teamcity не хватает бандлов
public class LocaleDictionariesTest {

    @Test
    public void testLocalization() throws Exception {
        LocaleDictionaries dictionaries = new LocaleDictionaries();
        dictionaries.afterPropertiesSet();
        {
            String key = "Источники трафика: поисковые системы";
            String counter = dictionaries.keyToLocal(LocaleLangs.RU, key);
            String back = dictionaries.localToKey(LocaleLangs.RU, counter);
            assertEquals(key, counter);
            assertEquals(key, back);
        }

        String key = "Источники трафика: поисковые системы";
        String counter = dictionaries.keyToLocal(LocaleLangs.EN, key);
        String back = dictionaries.localToKey(LocaleLangs.EN, counter);
        assertFalse(key.equals(counter));
        assertEquals(key, back);


    }
}
