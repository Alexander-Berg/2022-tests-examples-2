package ru.yandex.metrika.api.management.tests.util;

import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import ru.yandex.metrika.api.Feature;
import ru.yandex.metrika.api.constructor.contr.FeatureService;

public class FeatureServiceMock implements FeatureService {

    private Map<Integer, Set<Feature>> features = new HashMap<>();

    @Override
    public Set<Feature> getFeatures(int id) {
        return features.getOrDefault(id, Collections.emptySet());
    }

    @Override
    public Map<Integer, Set<Feature>> getFeatures(Iterable<? extends Integer> ids) {
        HashMap<Integer, Set<Feature>> result = new HashMap<>();
        ids.forEach(id -> result.put(id, features.getOrDefault(id, Collections.emptySet())));
        return result;
    }

    @Override
    public int addFeatures(int id, Set<Feature> features) {
        int added = 0;
        for (Feature f : features) {
            added += addFeature(id, f);
        }
        return added;
    }

    @Override
    public int addFeatures(List<Integer> ids, Feature feature) {
        int added = 0;
        for (Integer id : ids) {
            added += addFeature(id, feature);
        }
        return added;
    }

    @Override
    public int addFeature(int id, Feature feature) {
        if (features.computeIfAbsent(id, k -> new HashSet<>()).contains(feature)) {
            return 0;
        }
        features.get(id).add(feature);
        return 1;
    }

    @Override
    public void addDefaultFeatures(int id) {

    }

    public void clear() {
        features.clear();
    }
}
