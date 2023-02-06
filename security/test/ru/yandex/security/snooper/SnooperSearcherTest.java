package ru.yandex.security.snooper;

import org.junit.Test;

import static org.junit.Assert.assertArrayEquals;

@SuppressWarnings("LineLength")
public class SnooperSearcherTest {
    private static Secret[] search(String line) {
        NativeSnooper snooper = new NativeSnooper();
        return snooper.search(line);
    }

    @Test
    public void TestSearchValid() {
        Secret[] secrets = search("YC-token: t1.9euelZqbyZGVlM7Pjc3HiY2Wx5zPy-3rnpWalI3Pi4uQm5iai4ydkpCWnpTl8_dzEAtv-e9AMD8m_N3z9zM_CG_570AwPyb8.jjLcPfMXhc76214zDpqYQm1b8P37n7cP8PdX5iS7s1aq_C2ZLV3Lhl5JKb5JDUgR9gPIzVkWrHWq7TNEK_xiAw\nAuthorization: OAuth AgAAAAAHYVLuAAX_m477zavGV0GMlcItT-kpRm1");
        Secret[] expected = new Secret[] {
            new Secret("t1.9euelZqbyZGVlM7Pjc3HiY2Wx5zPy-3rnpWalI3Pi4uQm5iai4ydkpCWnpTl8_dzEAtv-e9AMD8m_N3z9zM_CG_570AwPyb8.jjLcPfMXhc76214zDpqYQm1b8P37n7cP8PdX5iS7s1aq_C2ZLV3Lhl5JKb5JDUgR9gPIzVkWrHWq7TNEK_xiAw", new Pos(10, 186), new Pos(110, 86)),
            new Secret("AgAAAAAHYVLuAAX_m477zavGV0GMlcItT-kpRm1", new Pos(218, 39), new Pos(236, 21))
        };

        assertArrayEquals(expected, secrets);
    }

    @Test
    public void TestSearchInvalid() {
        Secret[] secrets = search("YC-token: t1.9euelZqbyZGVlM7Pjc3HiY2Wx5zPy-3rnpWalI3Pi4uQm5iai4ydkpCWnpTl8_dzEAtv-e9AMD8m_N3z9zM_CG_570AwPyb8.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\nAuthorization: OAuth AgAAAAAHYVLuAAX_m47xxxxxxxxxxxxxxxxxxxx");
        assertArrayEquals(NativeSnooper.EMPTY_SECRETS, secrets);
    }
}
