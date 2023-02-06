package ru.yandex.metrika.mobmet.push.common.model;

import java.util.Collection;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import static org.junit.Assert.assertEquals;


@RunWith(Parameterized.class)
public class IdTypeTest {
    @Parameter
    public IdType deviceIdType;

    @Parameter(1)
    public String deviceId;

    @Parameter(2)
    public boolean expected;

    @Parameters(name = "{0} = \"{1}\"")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                new Object[]{IdType.DEVICE_ID_HASH, "72548762549", true},
                new Object[]{IdType.DEVICE_ID_HASH, null, false},
                new Object[]{IdType.DEVICE_ID_HASH, "", false},
                new Object[]{IdType.DEVICE_ID_HASH, "  ", false},
                new Object[]{IdType.DEVICE_ID_HASH, "\t", false},
                new Object[]{IdType.DEVICE_ID_HASH, "38400000-8cf0-11bd-b23e-10b96e40000d", false},
                new Object[]{IdType.DEVICE_ID_HASH, "38400000-8CF0-11BD-B23E-10B96E40000D", false},
                new Object[]{IdType.DEVICE_ID_HASH, "abc", false},

                new Object[]{IdType.IOS_IFA, "72548762549", false},
                new Object[]{IdType.IOS_IFA, null, false},
                new Object[]{IdType.IOS_IFA, "", false},
                new Object[]{IdType.IOS_IFA, "  ", false},
                new Object[]{IdType.IOS_IFA, "\t", false},
                new Object[]{IdType.IOS_IFA, "38400000-8cf0-11bd-b23e-10b96e40000d", true},
                new Object[]{IdType.IOS_IFA, "38400000-8CF0-11BD-B23E-10B96E40000D", true},
                new Object[]{IdType.IOS_IFA, "abc", false},

                new Object[]{IdType.IOS_IFV, "72548762549", false},
                new Object[]{IdType.IOS_IFV, null, false},
                new Object[]{IdType.IOS_IFV, "", false},
                new Object[]{IdType.IOS_IFV, "  ", false},
                new Object[]{IdType.IOS_IFV, "\t", false},
                new Object[]{IdType.IOS_IFV, "38400000-8cf0-11bd-b23e-10b96e40000d", true},
                new Object[]{IdType.IOS_IFV, "38400000-8CF0-11BD-B23E-10B96E40000D", true},
                new Object[]{IdType.IOS_IFV, "abc", false},

                new Object[]{IdType.GOOGLE_AID, "72548762549", false},
                new Object[]{IdType.GOOGLE_AID, null, false},
                new Object[]{IdType.GOOGLE_AID, "", false},
                new Object[]{IdType.GOOGLE_AID, "  ", false},
                new Object[]{IdType.GOOGLE_AID, "\t", false},
                new Object[]{IdType.GOOGLE_AID, "38400000-8cf0-11bd-b23e-10b96e40000d", true},
                new Object[]{IdType.GOOGLE_AID, "38400000-8CF0-11BD-B23E-10B96E40000D", true},
                new Object[]{IdType.GOOGLE_AID, "abc", false},

                new Object[]{IdType.HUAWEI_OAID, "72548762549", false},
                new Object[]{IdType.HUAWEI_OAID, null, false},
                new Object[]{IdType.HUAWEI_OAID, "", false},
                new Object[]{IdType.HUAWEI_OAID, "  ", false},
                new Object[]{IdType.HUAWEI_OAID, "\t", false},
                new Object[]{IdType.HUAWEI_OAID, "38400000-8cf0-11bd-b23e-10b96e40000d", true},
                new Object[]{IdType.HUAWEI_OAID, "38400000-8CF0-11BD-B23E-10B96E40000D", true},
                new Object[]{IdType.HUAWEI_OAID, "abc", false},

                new Object[]{IdType.IOS_PUSH_TOKEN, "72548762549", true},
                new Object[]{IdType.IOS_PUSH_TOKEN, null, false},
                new Object[]{IdType.IOS_PUSH_TOKEN, "", false},
                new Object[]{IdType.IOS_PUSH_TOKEN, "  ", false},
                new Object[]{IdType.IOS_PUSH_TOKEN, "\t", false},
                new Object[]{IdType.IOS_PUSH_TOKEN, "38400000-8cf0-11bd-b23e-10b96e40000d", true},
                new Object[]{IdType.IOS_PUSH_TOKEN, "38400000-8CF0-11BD-B23E-10B96E40000D", true},
                new Object[]{IdType.IOS_PUSH_TOKEN, "abc", true},
                new Object[]{IdType.IOS_PUSH_TOKEN, "ab c", true},

                new Object[]{IdType.ANDROID_PUSH_TOKEN, "72548762549", true},
                new Object[]{IdType.ANDROID_PUSH_TOKEN, null, false},
                new Object[]{IdType.ANDROID_PUSH_TOKEN, "", false},
                new Object[]{IdType.ANDROID_PUSH_TOKEN, "  ", false},
                new Object[]{IdType.ANDROID_PUSH_TOKEN, "\t", false},
                new Object[]{IdType.ANDROID_PUSH_TOKEN, "38400000-8cf0-11bd-b23e-10b96e40000d", true},
                new Object[]{IdType.ANDROID_PUSH_TOKEN, "38400000-8CF0-11BD-B23E-10B96E40000D", true},
                new Object[]{IdType.ANDROID_PUSH_TOKEN, "abc", true},
                new Object[]{IdType.ANDROID_PUSH_TOKEN, "ab c", true},

                new Object[]{IdType.HUAWEI_PUSH_TOKEN, "72548762549", true},
                new Object[]{IdType.HUAWEI_PUSH_TOKEN, null, false},
                new Object[]{IdType.HUAWEI_PUSH_TOKEN, "", false},
                new Object[]{IdType.HUAWEI_PUSH_TOKEN, "  ", false},
                new Object[]{IdType.HUAWEI_PUSH_TOKEN, "\t", false},
                new Object[]{IdType.HUAWEI_PUSH_TOKEN, "38400000-8cf0-11bd-b23e-10b96e40000d", true},
                new Object[]{IdType.HUAWEI_PUSH_TOKEN, "38400000-8CF0-11BD-B23E-10B96E40000D", true},
                new Object[]{IdType.HUAWEI_PUSH_TOKEN, "abc", true},
                new Object[]{IdType.HUAWEI_PUSH_TOKEN, "ab c", true}
        );
    }

    @Test
    public void isValid() throws Exception {
        assertEquals(expected, deviceIdType.isValid(deviceId));
    }

}
