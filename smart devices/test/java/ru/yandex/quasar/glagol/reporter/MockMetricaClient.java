package ru.yandex.quasar.glagol.reporter;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import org.jetbrains.annotations.NotNull;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

public class MockMetricaClient implements MetricaClient {
    private final List<Event> eventLog = new ArrayList<>();

    @Override
    public void reportEvent(@NonNull String s) {
    }

    @Override
    public void reportEvent(@NonNull @NotNull String s, @NonNull @NotNull JsonObject obj) {
        final HashMap<String, Object> map = new HashMap<>();
        for (Map.Entry<String, JsonElement> entry : obj.entrySet()) {
            map.put(entry.getKey(), entry.getValue());
        }
        eventLog.add(new Event(GlagolMetrics.EVENT_PREFIX + s, map));
    }

    @Override
    public void reportError(@NonNull String s, @Nullable Throwable throwable) {
    }

    @Override
    public void setVariable(@NonNull String key, Object value) {
    }

    public List<Event> getEventLog() {
        return eventLog;
    }

    public static final class Event {
        String s;
        Map<String, Object> map;

        public Event(String s, Map<String, Object> map) {
            this.s = s;
            this.map = map;
        }

        public String getName() {
            return s;
        }

        public Object getParam(Object s) {
            return map.get(s);
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            Event event = (Event) o;
            return Objects.equals(s, event.s) &&
                    map.equals(event.map);
        }

        @Override
        public int hashCode() {
            return Objects.hash(s, map);
        }

        @Override
        public String toString() {
            return "Event{" +
                    "s='" + s + '\'' +
                    ", map=" +
                        Arrays.toString(map.entrySet().toArray())
                    +
                    '}';
        }
    }
}
