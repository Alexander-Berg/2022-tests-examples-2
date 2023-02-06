package ru.yandex.security.snooper;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class SnooperMaskerTest {
    private static String mask(String line) {
        NativeSnooper snooper = new NativeSnooper();
        return snooper.mask(line);
    }

    @Test
    public void TestMasker() {
        String output = mask("Authorization: OAuth AgAAAAAHYVLuAAX_m477zavGV0GMlcItT-kpRm1");
        assertEquals("Authorization: OAuth AgAAAAAHYVLuAAX_m4XXXXXXXXXXXXXXXXXXXXX", output);
    }

    @Test
    public void TestMaskerWithChiness() {
        String output = mask("坚定地用话语统治，OAuth AgAAAAAHYVLuAAX_m477zavGV0GMlcItT-kpRm1 把思想束之高阁的人是有福的。");
        assertEquals("坚定地用话语统治，OAuth AgAAAAAHYVLuAAX_m4XXXXXXXXXXXXXXXXXXXXX 把思想束之高阁的人是有福的。", output);
    }

    @Test
    public void TestMaskerUrlencodeOauth() {
        String output = mask("oken%22%3A%22Authorization%3A%20OAuth%20AgAAAAAHYVLuAAX_m477zavGV0GMlcItT-kpRm1%22%7D");
        assertEquals("oken%22%3A%22Authorization%3A%20OAuth%20AgAAAAAHYVLuAAX_m4XXXXXXXXXXXXXXXXXXXXX%22%7D", output);
    }
}
