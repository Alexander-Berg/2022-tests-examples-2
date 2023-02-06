package ru.yandex.metrika.lambda.steps;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Consumer;
import java.util.function.Function;

import ru.yandex.inside.yt.kosher.impl.ytree.serialization.YTreeTextSerializer;
import ru.yandex.inside.yt.kosher.ytree.YTreeMapNode;
import ru.yandex.inside.yt.kosher.ytree.YTreeNode;

import static java.util.stream.Collectors.toMap;

public class RowMapperColumnsExtractor implements Consumer<YTreeMapNode> {

    private List<Map<String, String>> data = new ArrayList<>();

    public RowMapperColumnsExtractor() {
    }

    @Override
    public void accept(YTreeMapNode entries) {
        data.add(entries.keys().stream().collect(toMap(Function.identity(), k -> convert(entries.get(k)))));
    }

    private String convert(Optional<YTreeNode> node) {
        return node.isPresent() ? YTreeTextSerializer.serialize(node.get()) : "";
    }

    public List<Map<String, String>> getData() {
        return data;
    }
}
