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
public class PartnerNamesTest {

    @Test
    public void testResolving() {
        final TranslationHelper helper = mock(TranslationHelper.class);
        when(helper.localizeMessage("Не определено")).thenReturn("Undefined");
        when(helper.localizeMessage("Органика")).thenReturn("Translated organic");

        final DimensionNamesDao names = mock(DimensionNamesDao.class);
        when(names.partnerNames(ImmutableSet.of(0L, 254L, 5566L)))
                .thenReturn(ImmutableMap.of(
                        0L, "Органика",
                        254L, "Portal"
                ));

        final PartnerNames resolver = new PartnerNames(names, helper);

        assertThat(resolver.names(ImmutableSet.of(0L, 254L, 5566L)),
                equalTo(ImmutableMap.of(
                        0L, "Translated organic",
                        254L, "Portal",
                        5566L, "Undefined"
                )));
    }

}
