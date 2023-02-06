package ru.yandex.metrika.mobmet.profiles;

import java.util.Arrays;
import java.util.Collection;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.mobmet.profiles.model.ProfileCustomAttribute;
import ru.yandex.metrika.segments.apps.misc.profile.ProfileAttributeType;

import static org.junit.Assert.assertEquals;

@RunWith(Parameterized.class)
public class ProfileCustomAttributeTest {

    @Parameterized.Parameter
    public ProfileAttributeType type;

    @Parameterized.Parameter(1)
    public Long id;

    @Parameterized.Parameter(2)
    public String expected;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> operatingSystems() {
        return Arrays.asList(
                new Object[]{ProfileAttributeType.BOOL, 1923423L, "ym:p:customBoolAttribute1923423"},
                new Object[]{ProfileAttributeType.COUNTER, 0L, "ym:p:customCounterAttribute0"},
                new Object[]{ProfileAttributeType.STRING, 12L, "ym:p:customStringAttribute12"},
                new Object[]{ProfileAttributeType.NUBMER, 1859L, "ym:p:customNumberAttribute1859"}
        );
    }

    @Test
    public void toExternal() throws Exception {
        assertEquals(expected, ProfileCustomAttribute.buildCustomAttributeDimension(type, id));
    }
}
