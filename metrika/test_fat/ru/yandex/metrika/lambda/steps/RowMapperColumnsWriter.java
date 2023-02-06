package ru.yandex.metrika.lambda.steps;

import java.io.IOException;
import java.io.Writer;
import java.util.function.Consumer;

import ru.yandex.inside.yt.kosher.impl.ytree.serialization.YTreeTextSerializer;
import ru.yandex.inside.yt.kosher.impl.ytree.serialization.YsonTags;
import ru.yandex.inside.yt.kosher.ytree.YTreeMapNode;

public class RowMapperColumnsWriter implements Consumer<YTreeMapNode> {
    private final Writer writer;

    public RowMapperColumnsWriter(Writer writer) {
        this.writer = writer;
    }

    @Override
    public void accept(YTreeMapNode entries) {
        try {
            writer.write(YTreeTextSerializer.serialize(entries));
            writer.write(YsonTags.ITEM_SEPARATOR);
            writer.write("\n");
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}
