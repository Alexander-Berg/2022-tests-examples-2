package ru.yandex.taxi.dmp.flink.connectors.logbroker;

import lombok.experimental.UtilityClass;

import ru.yandex.taxi.dmp.flink.connectors.logbroker.Installation.Endpoint;

@UtilityClass
public class TestInstallations {
    public static final Installation.ReadableInstallation TEST = new Installation.ReadableInstallation(
            Endpoint.of("configuration"),
            Endpoint.of("proxyBalancer")
    );
}
