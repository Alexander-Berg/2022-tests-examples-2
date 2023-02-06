package ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.mapping;

import java.util.LinkedHashSet;

import com.google.common.collect.Sets;
import org.junit.Test;

import ru.yandex.metrika.mobmet.crash.deobfuscation.fork.FrameRemapper.MethodInfo;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.MethodInfoKey;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.ProguardMethodInfoSerializer;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.ProguardMethodMapping;

import static java.util.Arrays.asList;
import static org.junit.Assert.assertEquals;
import static ru.yandex.metrika.mobmet.crash.symbols.SymbolsYdbTableType.COMPRESSED;

public class ProguardMethodInfoSerializerTest {

    private final MethodInfoKey key = new MethodInfoKey(
            18,
            COMPRESSED.getProguardMembersMapTable(),
            "android.support.v4.media.MediaBrowserCompat$CallbackHandler",
            "handleMessage"
    );

    private final LinkedHashSet<ProguardMethodMapping> methodInfos = Sets.newLinkedHashSet(asList(
            new ProguardMethodMapping(
                    new MethodInfo(2086, 2086, "android.support.v4.media.MediaBrowserCompat$CallbackHandler",
                            2138, 2138, "void", "handleMessage", "android.os.Message")),
            new ProguardMethodMapping(
                    new MethodInfo(3928, 3931, "android.support.v4.media.session.MediaSessionCompat",
                            928, 931, "int", "ensureClassLoader", "android.os.Bundle")),
            new ProguardMethodMapping(
                    new MethodInfo(3928, 3928, "android.support.v4.media.MediaBrowserCompat$CallbackHandler",
                            2098, 2098, "void", "handleMessage", null)),
            new ProguardMethodMapping(
                    new MethodInfo(4928, 4931, "android.support.v4.media.session.MediaSessionCompat",
                            928, 931, "void", "ensureClassLoader", "android.os.Bundle")),
            new ProguardMethodMapping(
                    new MethodInfo(5928, 5931, "android.support.v4.media.MediaBrowserCompat$CallbackHandler",
                            2116, 2116, "void", "handleMessage", "android.os.Message"))
    ));

    private final String serialized = "" +
            "2086;;;2138;;;handleMessage;android.os.Message\n" +
            "3928;3931;android.support.v4.media.session.MediaSessionCompat;928;931;int;ensureClassLoader;android.os.Bundle\n" +
            "3928;;;2098;;;handleMessage;\n" +
            "4928;4931;android.support.v4.media.session.MediaSessionCompat;928;931;;ensureClassLoader;android.os.Bundle\n" +
            "5928;5931;;2116;;;handleMessage;android.os.Message\n";

    private final ProguardMethodInfoSerializer serializer = new ProguardMethodInfoSerializer();

    @Test
    public void serialize() {
        assertEquals(serialized, serializer.serialize(key, methodInfos));
    }

    @Test
    public void deserialize() {
        assertEquals(methodInfos, serializer.deserialize(key, serialized));
    }
}
