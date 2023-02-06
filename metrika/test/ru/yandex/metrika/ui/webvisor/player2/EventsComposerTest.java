package ru.yandex.metrika.ui.webvisor.player2;

import java.util.Arrays;
import java.util.Collection;

import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.wv2.parser.Package;
import ru.yandex.metrika.wv2.parser.PackageType;

import static org.assertj.core.api.Assertions.assertThat;

@RunWith(Parameterized.class)
public class EventsComposerTest {


    @Parameterized.Parameter
    public Collection<Package> input;

    @Parameterized.Parameter(1)
    public Collection<Package> expected;


    @Parameterized.Parameters
    public static Collection<Object[]> createParameters() {
        return Arrays.asList(
                new Object[]{
                        Lists.newArrayList(
                                new Package(PackageType.chunk, 1, "1".getBytes(), 1, 1, 1, 1, false, 1),
                                new Package(PackageType.chunk, 1, "2".getBytes(), 1, 1, 2, 1, true, 1),
                                new Package(PackageType.event, 1, "3".getBytes(), 2, 1, 1, 1, true, 1)
                        ),
                        Sets.newHashSet(
                                new Package(PackageType.chunk, 1, "12".getBytes(), 1, 1, 0, 1, true, 1),
                                new Package(PackageType.event, 1, "3".getBytes(), 2, 1, 0, 1, true, 1)
                        )
                },
                new Object[]{
                        Lists.newArrayList(
                                new Package(PackageType.chunk, 1, "2".getBytes(), 1, 1, 2, 1, true, 1),
                                new Package(PackageType.chunk, 1, "1".getBytes(), 1, 1, 1, 1, false, 1),
                                new Package(PackageType.event, 1, "3".getBytes(), 2, 1, 1, 1, true, 1)
                        ),
                        Sets.newHashSet(
                                new Package(PackageType.chunk, 1, "12".getBytes(), 1, 1, 0, 1, true, 1),
                                new Package(PackageType.event, 1, "3".getBytes(), 2, 1, 0, 1, true, 1)
                        )
                },
                new Object[]{
                        Lists.newArrayList(
                                new Package(PackageType.chunk, 1, "1".getBytes(), 1, 1, 1, 1, false, 1),
                                new Package(PackageType.chunk, 1, "2".getBytes(), 1, 1, 2, 1, true, 1),
                                new Package(PackageType.event, 1, "3".getBytes(), 1, 1, 1, 1, true, 1)
                        ),
                        Sets.newHashSet(
                                new Package(PackageType.chunk, 1, "12".getBytes(), 1, 1, 0, 1, true, 1),
                                new Package(PackageType.event, 1, "3".getBytes(), 1, 1, 0, 1, true, 1)
                        )
                });
    }


    @Test
    public void compose() {
        assertThat(Sets.newHashSet(EventsComposer.compose(input))).isEqualTo(expected);
    }
}
