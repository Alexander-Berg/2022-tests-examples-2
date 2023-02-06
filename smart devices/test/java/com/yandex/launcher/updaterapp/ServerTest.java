package com.yandex.launcher.updaterapp;

import com.yandex.launcher.updaterapp.core.Server;

import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;

import static junit.framework.Assert.assertEquals;

public class ServerTest extends BaseRobolectricTest {

    @Rule
    public final ExpectedException thrownException = ExpectedException.none();

    @Test
    public void shouldParseUpdateStorage() {
        assertEquals(Server.Prod, Server.parseServer("alexandria"));
        assertEquals(Server.Prod, Server.parseServer("Prod"));
        assertEquals(Server.Infra, Server.parseServer("Beta"));
        assertEquals(Server.Infra, Server.parseServer("Infra"));
        assertEquals(Server.Infra, Server.parseServer("Test"));
    }

    @Test
    public void shouldNotParseEmptyUpdateStorage() {
        thrownException.expect(IllegalArgumentException.class);
        Server.parseServer("");
    }

    @Test
    public void shouldNotParseInvalidUpdateStorage() {
        thrownException.expect(IllegalArgumentException.class);
        Server.parseServer("xxx");
    }
}
