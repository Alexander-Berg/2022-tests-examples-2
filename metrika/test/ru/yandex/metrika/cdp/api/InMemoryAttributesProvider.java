package ru.yandex.metrika.cdp.api;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

import org.apache.commons.lang3.tuple.Triple;

import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.dto.schema.EntityNamespace;
import ru.yandex.metrika.cdp.services.AttributesProvider;

public class InMemoryAttributesProvider implements AttributesProvider {

    private final Map<Triple<Integer, EntityNamespace, String>, Attribute> state = new HashMap<>();

    public void add(int counterId, EntityNamespace ns, Attribute attribute) {
        state.put(Triple.of(counterId, ns, attribute.getName()), attribute);
    }

    @Override
    public Optional<Attribute> getByName(int counterId, EntityNamespace ns, String name) {
        return Optional.ofNullable(state.get(Triple.of(counterId, ns, name)));
    }

    @Override
    public Optional<Attribute> getByNameCached(int counterId, EntityNamespace ns, String name) {
        return getByName(counterId, ns, name);
    }

    public void clear() {
        state.clear();
    }
}
