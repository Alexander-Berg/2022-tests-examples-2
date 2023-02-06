package ru.yandex.autotests.dictionary;

import org.junit.Test;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.junit.Assert.assertThat;

/**
 * User: leonsabr
 * Date: 27.07.12
 */
public class TextIdToStringTest {
    @Test
    public void nonPlural() {
        assertThat(new TextID("1", "2", "3").toString(), equalTo("1>>2>>3"));
    }

    @Test
    public void pluralOne() {
        assertThat(new TextID("1", "2", "3", Plural.ONE).toString(), equalTo("1>>2>>3>>ONE"));
    }

    @Test
    public void pluralSome() {
        assertThat(new TextID("1", "2", "3", Plural.SOME).toString(), equalTo("1>>2>>3>>SOME"));
    }

    @Test
    public void pluralMany() {
        assertThat(new TextID("1", "2", "3", Plural.MANY).toString(), equalTo("1>>2>>3>>MANY"));
    }

    @Test
    public void pluralNone() {
        assertThat(new TextID("1", "2", "3", Plural.NONE).toString(), equalTo("1>>2>>3>>NONE"));
    }
}
