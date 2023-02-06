package ru.yandex.metrika.storage.merger.impl;

import java.io.File;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.util.Date;

import com.codahale.metrics.MetricRegistry;
import com.google.common.io.Files;
import org.apache.logging.log4j.Level;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.springframework.util.FileSystemUtils;

import ru.yandex.metrika.storage.merger.ChunkWriter;
import ru.yandex.metrika.storage.merger.DataStreamConfiguration;
import ru.yandex.metrika.storage.merger.ItemBuffer;
import ru.yandex.metrika.storage.merger.replica.ReplicableDB;
import ru.yandex.metrika.util.id.IdGeneratorGeneratorAffine;
import ru.yandex.metrika.util.log.Log4jSetup;

/**
 * Created by orantius on 4/12/14.
 */
public class Repl2Test {

    private MergedFileSetTr master;
    private MergedFileSetTr replica;

    static MergedFileSetTr createMerger(File dir, int mod, String name) {
        return createMerger(dir, false, mod, name);
    }

    static MergedFileSetTr createMerger(File dir, boolean sparse, int mod, String name) {
        return createMerger(dir, sparse, 2, 2, mod, name);
    }

    static MergedFileSetTr createMerger(File dir, boolean sparse, int mergeThreshold, int maxMergeLevel, int mod, String name) {
        DataStreamConfiguration<StoredEntity, Integer> config = new DataStreamConfiguration<>();
        config.setComparator(MergedFileSetImplTest.ENTITY_COMPARATOR);
        config.setFoldingFunction(new MergedFileSetImplTest.EntityMerger());
        config.setDeSerializer(new MergedFileSetImplTest.EntityDeserializer());
        config.setEntityClass(StoredEntity.class);
        if(sparse) config.setIndex(new MergedFileSetImplTest.EntitySparseIndex());
        else config.setIndex(new MergedFileSetImplTest.EntityHashIndex());
        config.setSerializer(new MergedFileSetImplTest.EntitySerializer());
        config.setName("testEntity");
        config.setTimeExtractor(new MergedFileSetImplTest.EntityTimeExtractor());
        return new MergedFileSetTr(new ChunkPool(1024), dir, mergeThreshold, maxMergeLevel, new DataStreamConfiguration[]{config}, name, new IdGeneratorGeneratorAffine(2, mod), new MetricRegistry());
    }

    @Before
    public void setUp() throws Exception {
        Log4jSetup.basicSetup(Level.DEBUG);
        File masterDir = Files.createTempDir();
        master = createMerger(masterDir, 0, "master");

        File replDir = Files.createTempDir();
        replica = createMerger(replDir, 1, "slave");

    }

    /**
     * file-based round of replication MFS
     * @param master
     * @param slave
     * @throws Exception
     */
    public static void copyFromTo(ReplicableDB master, ReplicableDB slave) throws Exception {
        File reqData = File.createTempFile("req", "tmp");
        File resData = File.createTempFile("res", "tmp");
        RandomAccessFile reqFile = new RandomAccessFile(reqData, "rw");
        RandomAccessFile resFile = new RandomAccessFile(resData, "rw");
        slave.sendQueryToMaster(reqFile);
        reqFile.seek(0);
        master.handleSlaveRequest(reqFile, resFile);
        reqFile.setLength(0);
        resFile.seek(0);
        slave.syncChunksFrom(resFile);
        reqFile.setLength(0);
        reqFile.close();
        resFile.close();
        reqData.delete();
        resData.delete();
    }

    @After
    public void tearDown() throws Exception {
        master.destroy();
        replica.destroy();
        deleteMerger(master.dataDir);
        deleteMerger(replica.dataDir);
    }

    private static void deleteMerger(File dir2) throws IOException {
        FileSystemUtils.deleteRecursively(dir2);
        FileSystemUtils.deleteRecursively(new File(dir2.getParentFile(), dir2.getName() + "_tr"));
    }

    @Test
    public void smoke() throws Exception {
        Date date = new Date();
        {
            ChunkWriter writer = master.createWriter(date);
            ItemBuffer<StoredEntity> buffer = writer.getItemBuffer(StoredEntity.class);
            buffer.put(new StoredEntity(50 + 1, 50 + 1, date, Integer.toString(50)));
            writer.commit();
        }
        copyFromTo(master, replica);
        {
            ChunkWriter writer = replica.createWriter(date);
            ItemBuffer<StoredEntity> buffer = writer.getItemBuffer(StoredEntity.class);
            buffer.put(new StoredEntity(51 + 1, 51 + 1, date, Integer.toString(51)));
            writer.commit();
        }
        copyFromTo(replica, master);


    }
}
