package ru.yandex.autotests.dictionary;

import org.junit.Test;

import static org.hamcrest.CoreMatchers.*;
import static org.hamcrest.CoreMatchers.not;
import static org.junit.Assert.assertThat;
import static ru.yandex.autotests.dictionary.Plural.*;

/**
 * User: leonsabr
 * Date: 28.11.11
 */
public class TextIDEqualsTest {
    @Test
    public void checkEquals() {
        assertThat(new TextID("1", "2", "3"), equalTo(new TextID("1", "2", "3")));
        assertThat(new TextID("1", "2", "3"), equalTo(new TextID("1", "2", "3", null)));
        assertThat(new TextID("1", "2", "3", ONE), equalTo(new TextID("1", "2", "3", ONE)));
        assertThat(new TextID("1", "2", "3", SOME), equalTo(new TextID("1", "2", "3", SOME)));
        assertThat(new TextID("1", "2", "3", MANY), equalTo(new TextID("1", "2", "3", MANY)));
        assertThat(new TextID("1", "2", "3", NONE), equalTo(new TextID("1", "2", "3", NONE)));
    }

    @Test
    public void checkTheSame() {
        TextID ids = new TextID("1", "2", "3");
        assertThat(ids, equalTo(ids));
    }

    @Test
    public void checkNotEqualToNull() {
        TextID valid = new TextID("1", "2", "3");
        TextID invalid = null;
        assertThat(valid, not(equalTo(invalid)));
    }

    @Test
    public void checkNotEqualToDifferentClass() {
        Object valid = new TextID("1", "2", "3");
        Object invalid = "1 2 3";
        assertThat(valid.equals(invalid), is(false));
    }

    @Test
    public void checkNotEquals() {
        assertThat(new TextID("1", "2", "3"), not(equalTo(new TextID("1", "2", "4"))));
        assertThat(new TextID("1", "2", "3"), not(equalTo(new TextID("1", "4", "3"))));
        assertThat(new TextID("1", "2", "3"), not(equalTo(new TextID("4", "2", "3"))));
        assertThat(new TextID("1", "2", "3"), not(equalTo(new TextID("4", "2", "4"))));
        assertThat(new TextID("1", "2", "3"), not(equalTo(new TextID("4", "4", "3"))));
        assertThat(new TextID("1", "2", "3"), not(equalTo(new TextID("3", "2", "1"))));
        assertThat(new TextID("1", "2", "3"), not(equalTo(new TextID("1", "2", "3", ONE))));
        assertThat(new TextID("1", "2", "3", ONE), not(equalTo(new TextID("1", "2", "3"))));
        assertThat(new TextID("1", "2", "3", ONE), not(equalTo(new TextID("1", "2", "3", SOME))));
        assertThat(new TextID("1", "2", "3", ONE), not(equalTo(new TextID("1", "2", "3", MANY))));
        assertThat(new TextID("1", "2", "3", ONE), not(equalTo(new TextID("1", "2", "3", NONE))));
        assertThat(new TextID("1", "2", "3", SOME), not(equalTo(new TextID("1", "2", "3", ONE))));
        assertThat(new TextID("1", "2", "3", SOME), not(equalTo(new TextID("1", "2", "3", MANY))));
        assertThat(new TextID("1", "2", "3", SOME), not(equalTo(new TextID("1", "2", "3", NONE))));
        assertThat(new TextID("1", "2", "3", MANY), not(equalTo(new TextID("1", "2", "3", ONE))));
        assertThat(new TextID("1", "2", "3", MANY), not(equalTo(new TextID("1", "2", "3", SOME))));
        assertThat(new TextID("1", "2", "3", MANY), not(equalTo(new TextID("1", "2", "3", NONE))));
        assertThat(new TextID("1", "2", "3", NONE), not(equalTo(new TextID("1", "2", "3", ONE))));
        assertThat(new TextID("1", "2", "3", NONE), not(equalTo(new TextID("1", "2", "3", SOME))));
        assertThat(new TextID("1", "2", "3", NONE), not(equalTo(new TextID("1", "2", "3", MANY))));
    }
}
