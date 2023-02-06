package ru.yandex.quasar.glagol.impl;

import com.youview.tinydnssd.MDNSDiscover;

import org.junit.Before;
import org.junit.Test;

import java.util.HashMap;
import java.util.Map;

import ru.yandex.quasar.glagol.DeviceId;
import ru.yandex.quasar.glagol.DiscoveryResultItem;
import ru.yandex.quasar.glagol.backend.model.Device;
import ru.yandex.quasar.glagol.backend.model.GlagolConfig;
import ru.yandex.quasar.glagol.backend.model.GlagolSecurityConfig;

import static org.junit.Assert.assertEquals;

public class DiscoveryResultItemTest {
    private MDNSDiscover.Result discoverResult;
    private Map<DeviceId, Device> devices;

    @Before
    public void prepare() {
        Map<String, Object> config = new HashMap<>();
        config.put("name", "foo");
        Device device = new Device();
        device.setName("bar");
        device.setConfig(config);
        GlagolConfig glagolConfig = new GlagolConfig();
        GlagolSecurityConfig security = new GlagolSecurityConfig();
        security.setServerCertificate("abc");
        glagolConfig.setSecurity(security);
        device.setGlagol(glagolConfig);

        devices = new HashMap<>();
        devices.put(new DeviceId("a", "b"), device);

        discoverResult = new MDNSDiscover.Result();
        discoverResult.txt = new MDNSDiscover.TXT();
        discoverResult.txt.dict = new HashMap<>();
        discoverResult.txt.dict.put("deviceId", "a");
        discoverResult.txt.dict.put("platform", "b");
        discoverResult.a = new MDNSDiscover.A();
        discoverResult.a.ipaddr = "1.2.3.4";
        discoverResult.srv = new MDNSDiscover.SRV();
        discoverResult.srv.port = 1234;
    }

    @Test
    public void discoveredDeviceNameInConfig() throws Exception {
        DiscoveryResultItem item = DiscoveryResultFactory.toDiscoveryResultItem("ololo", discoverResult, devices);
        assertEquals("foo", item.getName());
    }

    @Test
    public void discoveredDeviceNoNameInConfig() throws Exception {
        devices.get(new DeviceId("a", "b")).getConfig().remove("name");
        DiscoveryResultItem item = DiscoveryResultFactory.toDiscoveryResultItem("ololo", discoverResult, devices);
        assertEquals("bar", item.getName());
    }

    @Test
    public void discoveredDeviceNoConfig() throws Exception {
        devices.get(new DeviceId("a", "b")).setConfig(null);
        DiscoveryResultItem item = DiscoveryResultFactory.toDiscoveryResultItem("ololo", discoverResult, devices);
        assertEquals("bar", item.getName());
    }
}
