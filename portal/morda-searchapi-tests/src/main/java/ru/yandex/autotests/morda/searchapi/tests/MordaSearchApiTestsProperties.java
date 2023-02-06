package ru.yandex.autotests.morda.searchapi.tests;

import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

import java.net.URI;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 06/05/15
 */
@Resource.Classpath("morda-searchapi-tests.properties")
public class MordaSearchApiTestsProperties {

    public MordaSearchApiTestsProperties() {
        PropertyLoader.populate(this);
    }

    @Property("morda.searchapi.schema.blocks")
    private String mordaSearchApiSchemaBlocks;

    @Property("morda.searchapi.host")
    private URI mordaSearchApiHost;

    @Property("morda.footballapi.host")
    private URI mordaFootbalApiHost;

    public List<String> getMordaSearchApiSchemaBlocks() {
        if (mordaSearchApiSchemaBlocks != null && mordaSearchApiSchemaBlocks.length() > 0) {
            return asList(mordaSearchApiSchemaBlocks.split(",")).stream().map(String::trim)
                    .collect(Collectors.toList());
        }
        return new ArrayList<>();
    }

    public URI getMordaSearchApiHost() {
        return mordaSearchApiHost;
    }

    public URI getMordaFootbalApiHost(){
        return mordaFootbalApiHost;
    }
}
