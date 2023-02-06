package ru.yandex.autotests.dictionary;

import org.junit.Test;
import ru.yandex.autotests.dictionary.cleaners.HomeCleaner;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.not;
import static org.junit.Assert.assertThat;
import static org.junit.Assume.assumeThat;

/**
 * User: leonsabr
 * Date: 27.07.12
 */
public class SafelyGetTest {
    private static final Tanker TANKER = new Tanker(SafelyGetTest.class.getClassLoader().getResource("home.xml"));
    private static final Tanker TANKER_CLEAN = new Tanker(new HomeCleaner(),
            SafelyGetTest.class.getClassLoader().getResource("home.xml"));

    @Test
    public void getSafelyTextIdCleanerOff() {
        TextID missingWord = new TextID("home", "allServices", "personalBlock.mail.desc");
        assumeThat(TANKER.get(missingWord, "hy"), equalTo(""));
        assumeThat(TANKER.get(missingWord, "ru"), not(equalTo("")));
        assertThat(TANKER.getSafely(missingWord, "hy"), equalTo(TANKER.get(missingWord, "ru")));
    }

    @Test
    public void getSafelyTextIdCleanerOn() {
        TextID missingWord = new TextID("home", "allServices", "personalBlock.mail.desc");
        assumeThat(TANKER_CLEAN.get(missingWord, "hy"), equalTo(""));
        assumeThat(TANKER_CLEAN.get(missingWord, "ru"), not(equalTo("")));
        assertThat(TANKER_CLEAN.getSafely(missingWord, "hy"), equalTo(TANKER_CLEAN.get(missingWord, "ru")));
    }

    @Test
    public void getSafelyCleanerOff() {
        assumeThat(TANKER.get("home", "fotki", "photoTitleK", "hy"), equalTo(""));
        assumeThat(TANKER.get("home", "fotki", "photoTitleK", "ru"), not(equalTo("")));
        assertThat(TANKER.getSafely("home", "fotki", "photoTitleK", "hy"),
                equalTo(TANKER.get("home", "fotki", "photoTitleK", "ru")));
    }

    @Test
    public void getSafelyCleanerOn() {
        assumeThat(TANKER_CLEAN.get("home", "fotki", "photoTitleK", "hy"), equalTo(""));
        assumeThat(TANKER_CLEAN.get("home", "fotki", "photoTitleK", "ru"), not(equalTo("")));
        assertThat(TANKER_CLEAN.getSafely("home", "fotki", "photoTitleK", "hy"),
                equalTo(TANKER_CLEAN.get("home", "fotki", "photoTitleK", "ru")));
    }

    @Test
    public void getSafelyPluralCleanerOff() {
        assumeThat(TANKER.get("home", "mail", "num.file", Plural.ONE, "hy"), equalTo(""));
        assumeThat(TANKER.get("home", "mail", "num.file", Plural.ONE, "ru"), not(equalTo("")));
        assertThat(TANKER.getSafely("home", "mail", "num.file", Plural.ONE, "hy"),
                equalTo(TANKER.get("home", "mail", "num.file", Plural.ONE, "ru")));
    }

    @Test
    public void getSafelyPluralCleanerOn() {
        assumeThat(TANKER_CLEAN.get("home", "mail", "num.file", Plural.ONE, "hy"), equalTo(""));
        assumeThat(TANKER_CLEAN.get("home", "mail", "num.file", Plural.ONE, "ru"), not(equalTo("")));
        assertThat(TANKER_CLEAN.getSafely("home", "mail", "num.file", Plural.ONE, "hy"),
                equalTo(TANKER_CLEAN.get("home", "mail", "num.file", Plural.ONE, "ru")));
    }
}
