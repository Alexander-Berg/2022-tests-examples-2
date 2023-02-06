package ru.yandex.metrika.storage.merger.index;

import java.io.File;
import java.io.IOException;
import java.util.function.Predicate;

import com.google.common.io.Files;
import junit.framework.Assert;
import org.jetbrains.annotations.NotNull;
import org.junit.Test;
import org.springframework.util.FileSystemUtils;

import ru.yandex.metrika.util.PrimitiveBytes;


/** @author Arthur Suilin */
public class HashIndexTest {
    class HashIndexImpl extends HashIndex<String, Integer> {

        HashIndexImpl() {
            super(4, "index.hash");
        }

        @Override
        protected byte[] keyToByteArray(Integer key) {
            return PrimitiveBytes.wrap(key);
        }

        @NotNull
        @Override
        public Indexer<String> createIndexer(File directory) {
            return new HashIndexer<String, Integer>(this, directory, "index.hash") {
                private int lastLen = -1;

                @Override
                protected Integer keyOf(String value) {
                    return value.length();
                }

                @Override
                protected boolean isNeedComputeKey(String value) {
                    int len = value.length();
                    if (len == lastLen) {
                        return false;
                    } else {
                        lastLen = len;
                        return true;
                    }
                }
            };
        }

        @Override
        public Predicate<String> getKeyPredicate(final Integer key) {
            return s -> s.length() == key;
        }
    }

    @Test
    public void test() throws IOException {

        final File f = Files.createTempDir();
        HashIndexImpl index = new HashIndexImpl();
        Indexer<String> indexer = index.createIndexer(f);
        indexer.onItem("a", 1);
        indexer.onItem("b", 1);
        indexer.onItem("aa", 2);
        indexer.onItem("bbb", 3);
        indexer.onItem("bbb", 4);


        indexer.finish();
        //Assert.assertEquals(-1, index.getFileOffset(file, 0));
        Assert.assertEquals(1, index.getFileOffset(f, 1));
        Assert.assertEquals(2, index.getFileOffset(f, 2));
        Assert.assertEquals(3, index.getFileOffset(f, 3));
        Assert.assertEquals(-1, index.getFileOffset(f, 4));
        ru.yandex.metrika.util.io.Files.deleteRecursively(f);


        FileSystemUtils.deleteRecursively(f);
    }

}
