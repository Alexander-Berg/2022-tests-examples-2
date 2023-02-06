package ru.yandex.metrika.mobmet.misc;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableSet;
import org.junit.Test;

import ru.yandex.metrika.mobmet.traffic.misc.DimensionNamesDao;
import ru.yandex.metrika.spring.TranslationHelper;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

/**
 * Created by graev on 30/03/2017.
 */
public class TrackerNamesTest {
    @Test
    public void testResolving() {
        final TranslationHelper helper = mock(TranslationHelper.class);
        when(helper.localizeMessage("Не определено (трекер)")).thenReturn("Translated zero tracker");
        when(helper.localizeMessage("Не определено")).thenReturn("Undefined");

        final DimensionNamesDao names = mock(DimensionNamesDao.class);
        when(names.trackerNames(ImmutableSet.of("0", "2", "4")))
                .thenReturn(ImmutableMap.of(
                        "2", "Google"
                ));

        final TrackerNames resolver = new TrackerNames(names, helper);

        assertThat(resolver.names(ImmutableSet.of("0", "2", "4")),
                equalTo(ImmutableMap.of(
                        "0", "Translated zero tracker",
                        "2", "Google",
                        "4", "Undefined"
                )));
    }
}
