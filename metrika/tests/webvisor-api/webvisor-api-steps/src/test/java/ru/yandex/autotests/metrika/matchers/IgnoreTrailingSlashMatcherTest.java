package ru.yandex.autotests.metrika.matchers;

import org.junit.Test;

import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.metrika.matchers.IgnoreTrailingSlashMatcher.equalToIgnoringTrailingSlash;

/**
 * Created by konkov on 26.05.2015.
 */
public class IgnoreTrailingSlashMatcherTest {

    @Test
    public void noSlashes() {
        assertThat("http://yandex.ru", equalToIgnoringTrailingSlash("http://yandex.ru"));
    }

    @Test
    public void slashNoSlash() {
        assertThat("http://yandex.ru/", equalToIgnoringTrailingSlash("http://yandex.ru"));
    }

    @Test
    public void noSlashSlash() {
        assertThat("http://yandex.ru", equalToIgnoringTrailingSlash("http://yandex.ru/"));
    }

    @Test
    public void slashes() {
        assertThat("http://yandex.ru/", equalToIgnoringTrailingSlash("http://yandex.ru/"));
    }

    @Test(expected = AssertionError.class)
    public void noEqual() {
        assertThat("http://yandex.ru", equalToIgnoringTrailingSlash("http://google.com"));
    }
}
