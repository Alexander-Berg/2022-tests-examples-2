package ru.yandex.metrika.topsites;

import java.io.IOException;
import java.util.Collection;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import ru.yandex.qe.hitman.comrade.script.model.Storage;

public class StubStorage implements Storage {

    private final ObjectMapper objectMapper = new ObjectMapper();
    private final Map<String, String> internalStorage;

    public StubStorage(Map<String, Object> storage) {
        this.internalStorage = storage.keySet().stream()
                .collect(Collectors.toMap(Function.identity(), key -> {
                    try {
                        return objectMapper.writeValueAsString(storage.get(key));
                    } catch (JsonProcessingException e) {
                        throw new RuntimeException(e);
                    }
                }));
    }

    @Override
    public int size() {
        return internalStorage.size();
    }

    @Override
    public boolean isEmpty() {
        return internalStorage.isEmpty();
    }

    @Override
    public Optional<Object> get(String s) {
        return get(s, Object.class);
    }

    @Override
    public void put(String key, Object value) {
        try {
            internalStorage.put(key, objectMapper.writeValueAsString(value));
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public void remove(String key) {
        internalStorage.remove(key);
    }

    @Override
    public <T> T getOrDefault(String key, T defaultValue) {
        //noinspection unchecked
        return (T) get(key).orElse(defaultValue);
    }

    @Override
    public Optional<String> getRaw(String key) {
        return Optional.ofNullable(internalStorage.get(key));
    }

    @Override
    public <T> Optional<T> get(String key, Class<T> aClass) {
        return getRaw(key).map(valueStr -> {
            try {
                return objectMapper.readValue(valueStr, aClass);
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        });
    }

    @Override
    public Set<String> missingKeys(Collection<String> collection) {
        return collection
                .stream()
                .filter(key -> !internalStorage.containsKey(key))
                .collect(Collectors.toSet());
    }

    @Override
    public void put(Map<String, Object> map) {
        map.forEach(this::put);
    }

    @Override
    public <T> Optional<T> get(String key, TypeReference<T> typeReference) {
        return getRaw(key).map(valueStr -> {
            try {
                return objectMapper.readValue(valueStr, typeReference);
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        });
    }
}
