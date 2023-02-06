package ru.yandex.metrika.mobmet.misc;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableSet;
import org.junit.Test;

import ru.yandex.metrika.mobmet.traffic.misc.DimensionNamesDao;
import ru.yandex.metrika.segments.apps.misc.PartnerType;
import ru.yandex.metrika.segments.apps.misc.PartnerTypes;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

/**
 * @author dancingelf
 */
public class TrackerDescriptionsTest {

    @Test
    public void testResolving() {

        final DimensionNamesDao namesDao = mock(DimensionNamesDao.class);
        when(namesDao.partnerByTracker(ImmutableSet.of("0", "2", "4")))
                .thenReturn(ImmutableMap.of(
                        "0", 0L,
                        "2", 254L
                ));

        final TrackerNames trackerNames = mock(TrackerNames.class);
        when(trackerNames.names(ImmutableSet.of("0", "2", "4")))
                .thenReturn(ImmutableMap.of(
                        "0", "Translated zero tracker",
                        "2", "Google",
                        "4", "Не определено"
                ));

        final PartnerNames partnerNames = mock(PartnerNames.class);
        when(partnerNames.names(ImmutableSet.of(0L, 254L)))
                .thenReturn(ImmutableMap.of(
                        0L, "Translated organic",
                        254L, "AdWords"
                ));

        final PartnerTypes partnerTypes = mock(PartnerTypes.class);
        when(partnerTypes.determineTypeForPartner(any())).thenReturn(PartnerType.ORDINARY);
        when(partnerTypes.determineTypeForPartner(0L)).thenReturn(PartnerType.ORGANIC);
        when(partnerTypes.determineTypeForPartner(254L)).thenReturn(PartnerType.ADWORDS);

        final TrackerDescriptions resolver = new TrackerDescriptions(trackerNames, partnerNames, partnerTypes, namesDao);

        assertThat(resolver.names(ImmutableSet.of("0", "2", "4")),
                equalTo(ImmutableMap.of(
                        "0", new TrackerDesc("0", "Translated zero tracker", "Translated organic", PartnerType.ORGANIC),
                        "2", new TrackerDesc("2", "Google", "AdWords", PartnerType.ADWORDS),
                        "4", new TrackerDesc("4", "Не определено", "Не определено", PartnerType.ORDINARY)
                )));
    }
}
