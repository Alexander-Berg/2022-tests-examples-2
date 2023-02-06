package ru.yandex.metrika.mobmet.misc;

import java.util.Map;
import java.util.Set;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableSet;
import org.hamcrest.MatcherAssert;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.spring.TranslationHelper;

import static org.hamcrest.Matchers.equalTo;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static ru.yandex.metrika.segments.apps.bundles.common.MobmetUrlParams.internalNull;

/**
 * Created by graev on 14/04/2017.
 */
public class UrlParamNamesTest {

    private static final Set<String> internalIds = ImmutableSet.of(internalNull(), "foo");

    private static final Map<String, UrlParamDesc> expected = ImmutableMap.of(
            internalNull(), new UrlParamDesc("specialDefaultNull", "Not set"),
            "foo", new UrlParamDesc("foo", "foo")
    );

    private UrlParamNames names;

    @Before
    public void setup() {
        final TranslationHelper translationHelper = mock(TranslationHelper.class);
        when(translationHelper.localizeMessage("Не задан")).thenReturn("Not set");
        when(translationHelper.localizeMessage("foo")).thenReturn("localized foo");

        names = new UrlParamNames(translationHelper);
    }

    @Test
    public void testNames() {
        MatcherAssert.assertThat(names.names(internalIds), equalTo(expected));
    }
}
