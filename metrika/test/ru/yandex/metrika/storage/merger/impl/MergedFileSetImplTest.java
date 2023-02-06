package ru.yandex.metrika.storage.merger.impl;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.EOFException;
import java.io.File;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.util.Arrays;
import java.util.Calendar;
import java.util.Comparator;
import java.util.Date;
import java.util.List;
import java.util.Random;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.function.Predicate;

import com.codahale.metrics.MetricRegistry;
import com.google.common.collect.Iterators;
import com.google.common.collect.Lists;
import com.google.common.io.Files;
import junit.framework.Assert;
import org.apache.commons.lang3.StringUtils;
import org.apache.logging.log4j.Level;
import org.jetbrains.annotations.NotNull;
import org.joda.time.LocalDate;
import org.joda.time.LocalTime;
import org.junit.Ignore;
import org.junit.Test;
import org.springframework.util.FileSystemUtils;

import ru.yandex.metrika.storage.merger.ChunkWriter;
import ru.yandex.metrika.storage.merger.DataStreamConfiguration;
import ru.yandex.metrika.storage.merger.FoldingFunction;
import ru.yandex.metrika.storage.merger.ItemBuffer;
import ru.yandex.metrika.storage.merger.ItemFilter;
import ru.yandex.metrika.storage.merger.MergedFileSet;
import ru.yandex.metrika.storage.merger.TimeExtractor;
import ru.yandex.metrika.storage.merger.ValueReader;
import ru.yandex.metrika.storage.merger.index.HashIndex;
import ru.yandex.metrika.storage.merger.index.HashIndexer;
import ru.yandex.metrika.storage.merger.index.Indexer;
import ru.yandex.metrika.storage.merger.index.SparseIndex;
import ru.yandex.metrika.storage.merger.io.Deserializer;
import ru.yandex.metrika.storage.merger.io.EndOfDataException;
import ru.yandex.metrika.storage.merger.io.Serializer;
import ru.yandex.metrika.storage.merger.iterator.ClosingIterator;
import ru.yandex.metrika.storage.merger.replica.MasterHostLocatorImpl;
import ru.yandex.metrika.storage.merger.replica.MasterReplicator;
import ru.yandex.metrika.storage.merger.replica.SlaveQuery;
import ru.yandex.metrika.storage.merger.replica.SlaveReplicator;
import ru.yandex.metrika.util.PrimitiveBytes;
import ru.yandex.metrika.util.concurrent.Pools;
import ru.yandex.metrika.util.id.IdGeneratorGeneratorSimple;
import ru.yandex.metrika.util.log.Log4jSetup;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

/** @author Arthur Suilin */
@Ignore
public class MergedFileSetImplTest {

    public static final Comparator<StoredEntity> ENTITY_COMPARATOR = Comparator.comparing(StoredEntity::getCounterId).thenComparing(StoredEntity::getVisitId);

    static class EntitySerializer implements Serializer<StoredEntity> {
        @Override
        public void serialize(StoredEntity item, DataOutputStream output) throws IOException {
            output.writeInt(item.counterId);
            output.writeLong(item.visitId);
            output.writeLong(item.time);
            output.writeUTF(item.content);
        }
    }

    static long descount;

    static class EntityDeserializer implements Deserializer<StoredEntity> {
        @Override
        public StoredEntity deserialize(DataInputStream input) throws IOException {
            try {
                descount += 1;
                return new StoredEntity(input);
            } catch (EOFException ignored) {
                throw new EndOfDataException();
            }
        }
    }



    static class EntityMerger implements FoldingFunction<StoredEntity> {
        @Override
        public StoredEntity fold(StoredEntity accumulator,
                               StoredEntity value) {
            System.out.println("fold: accumulator = " + accumulator+", value= "+value);
            String[] content = {accumulator.content, value.content};
            Arrays.sort(content);
            accumulator.content = StringUtils.join(content);
            return accumulator;
        }
    }

    static class EntityTimeExtractor implements TimeExtractor<StoredEntity> {
        @Override
        public long extractTime(StoredEntity object) {
            return object.time;
        }
    }

    static class EntityHashIndex extends HashIndex<StoredEntity, Integer> {

        EntityHashIndex() {
            super(4, "index.hash");
        }

        @Override
        protected byte[] keyToByteArray(Integer key) {
            return PrimitiveBytes.wrap(key);
        }

        @NotNull
        @Override
        public Indexer<StoredEntity> createIndexer(File directory) {
            return new EntityHashIndexer(this, directory);
        }

        @Override
        public Predicate<StoredEntity> getKeyPredicate(final Integer key) {
            return storedEntity -> storedEntity.counterId == key;
        }
    }

    static class EntityHashIndexer extends HashIndexer<StoredEntity, Integer> {
        int previousCounterId = Integer.MIN_VALUE;

        EntityHashIndexer(HashIndex<StoredEntity, Integer> parent, File directory) {
            super(parent, directory, "index.hash");
        }

        @Override
        protected Integer keyOf(StoredEntity value) {
            return value.counterId;
        }

        @Override
        protected boolean isNeedComputeKey(StoredEntity value) {
            if (value.counterId == previousCounterId) {
                return false;
            } else {
                previousCounterId = value.counterId;
                return true;
            }

        }
    }

    static class EntitySparseIndex extends SparseIndex<StoredEntity, Integer> {
        EntitySparseIndex() {
            super(4, "index", 100);
        }

        @Override
        public Integer keyOf(StoredEntity value) {
            return value.counterId;
        }

        @Override
        public byte[] keyToByteArray(Integer key) {
            return PrimitiveBytes.wrap(key);
        }

        @Override
        public Integer keyFromByteArray(byte[] key) {
            return PrimitiveBytes.getInt(key);
        }
    }

    static MergedFileSetImpl createMerger(File dir) {
        return createMerger(dir, false);
    }

    private static void deleteMerger(File dir2) {
        FileSystemUtils.deleteRecursively(dir2);
        FileSystemUtils.deleteRecursively(new File(dir2.getParentFile(), dir2.getName()+"_tr"));
    }

    static MergedFileSetImpl createMerger(File dir, boolean sparse) {
        return createMerger(dir, sparse, 2, 2);
    }

    static MergedFileSetImpl createMerger(File dir, boolean sparse, int mergeThreshold, int maxMergeLevel) {
        DataStreamConfiguration<StoredEntity, Integer> config = new DataStreamConfiguration<>();
        config.setComparator(ENTITY_COMPARATOR);
        config.setFoldingFunction(new EntityMerger());
        config.setDeSerializer(new EntityDeserializer());
        config.setEntityClass(StoredEntity.class);
        if(sparse) config.setIndex(new EntitySparseIndex());
        else config.setIndex(new EntityHashIndex());
        config.setSerializer(new EntitySerializer());
        config.setName("testEntity");
        config.setTimeExtractor(new EntityTimeExtractor());
        return new MergedFileSetImpl(new ChunkPool(1024), dir, mergeThreshold, maxMergeLevel, new DataStreamConfiguration[]{config}, "Test", new IdGeneratorGeneratorSimple(), new MetricRegistry());
    }

//    private File prepareDir(String directory) throws IOException {
//        File dir = new File(directory);
//        //Files.createTempDir()
//        dir.mkdirs();
//        Files.deleteDirectoryContents(dir);
//        return createMerger(dir);
//    }

    @Test
    public void test() throws Exception {
        Log4jSetup.basicSetup(Level.DEBUG);
        File dir = Files.createTempDir();
        MergedFileSetImpl merger = createMerger(dir);
        ChunkWriter writer = merger.createWriter(new Date());
        ItemBuffer<StoredEntity> buffer =  writer.getItemBuffer(StoredEntity.class);
        Calendar c = Calendar.getInstance();
        c.set(2011, 1, 1);
        buffer.put(new StoredEntity(1, 1, c.getTime(), "a"));
        buffer.put(new StoredEntity(1, 2, c.getTime(), "b"));
        c.set(2011, 1, 2);
        buffer.put(new StoredEntity(1, 1, c.getTime(), "c"));
        c.set(2011, 1, 1);
        buffer.put(new StoredEntity(2, 1, c.getTime(), "d"));
        writer.commit();

        ItemFilter<StoredEntity> filter = DateIntervalItemFilter.getEmptyFilter();

        ValueReader<StoredEntity, Integer> reader = merger.getReader(StoredEntity.class);
        ClosingIterator<StoredEntity> it = reader.valuesForKey(1, filter);
        Assert.assertTrue(it.hasNext());
        StoredEntity e1 = it.next();
        Assert.assertEquals(1, e1.counterId);
        Assert.assertEquals(1, e1.visitId);
        Assert.assertEquals("ac", e1.content);
        StoredEntity e2 = it.next();
        Assert.assertEquals(1, e2.counterId);
        Assert.assertEquals(2, e2.visitId);
        Assert.assertEquals("b", e2.content);
        Assert.assertFalse(it.hasNext());

        ClosingIterator<StoredEntity> it2 = reader.valuesForKey(2, filter);
        StoredEntity e3 = it2.next();
        Assert.assertEquals(2, e3.counterId);
        Assert.assertEquals(1, e3.visitId);
        Assert.assertEquals("d", e3.content);
        Assert.assertFalse(it2.hasNext());

        ClosingIterator<StoredEntity> it3 = reader.valuesForKey(3, filter);
        Assert.assertFalse(it3.hasNext());

        //Тестируем, насколько успешно отработает merge двух файлов
        ChunkWriter writer2 = merger.createWriter(new Date());
        ItemBuffer<StoredEntity> buffer2 =  writer2.getItemBuffer(StoredEntity.class);
        c.set(2011, 1, 1);
        buffer2.put(new StoredEntity(1, 1, c.getTime(), "e"));
        c.set(2011, 1, 5);
        buffer2.put(new StoredEntity(2, 1, c.getTime(), "f"));
        writer2.commit();

        testMergedFile(merger);
        merger.destroy();

        // Тестируем, что на старте успешно подцепляются файлы
        MergedFileSetImpl master = createMerger(dir);
        testMergedFile(master);
        //master.destroy();

        // Тестируем репликацию на низком уровне
        File dir2 = Files.createTempDir();
        MergedFileSetImpl slave = createMerger(dir2);
        File repData = File.createTempFile("rep", "merger");
        RandomAccessFile replica = new RandomAccessFile(repData, "rw");
        slave.buildQuery().sendQueryToMaster(replica);
        replica.seek(0);
        SlaveQuery ids = SlaveQuery.readQueryFromSlave(replica);
        replica.setLength(0);
        master.sendChunksToSlave(ids, replica);
        replica.seek(0);
        slave.syncChunksFrom(replica);
        testMergedFile(slave);
        slave.destroy();
        ru.yandex.metrika.util.io.Files.deleteDirectoryContents(dir2);
        replica.close();
        repData.delete();

        // Тестируем репликацию через сокеты
        MasterReplicator mr = new MasterReplicator();
        mr.setDb(master);
        mr.setPort(12666);
        mr.afterPropertiesSet();

        slave = createMerger(dir2);
        SlaveReplicator sr = new SlaveReplicator();
        sr.setLastReplicaTime(null);
        sr.setMasterHost(new MasterHostLocatorImpl("localhost"));
        sr.setDb(slave);
        sr.setMasterPort(12666);
        sr.afterPropertiesSet();
        // Ждем, пока приедет первая реплика
        while (sr.getLastReplicaTime() == null) {
            Thread.sleep(100);
        }
        testMergedFile(slave);
        sr.destroy();
        mr.destroy();
        master.destroy();

        deleteMerger(dir);
        deleteMerger(dir2);

    }

    @Test
    public void testSparse() throws Exception {
        Log4jSetup.basicSetup(Level.DEBUG);
        File dir = Files.createTempDir();
        MergedFileSetImpl merger = createMerger(dir, true);
        ChunkWriter writer = merger.createWriter(new Date());
        ItemBuffer<StoredEntity> buffer =  writer.getItemBuffer(StoredEntity.class);
        Calendar c = Calendar.getInstance();
        c.set(2011, 1, 1);
        buffer.put(new StoredEntity(1, 1, c.getTime(), "a"));
        buffer.put(new StoredEntity(1, 2, c.getTime(), "b"));
        c.set(2011, 1, 2);
        buffer.put(new StoredEntity(1, 1, c.getTime(), "c"));
        c.set(2011, 1, 1);
        buffer.put(new StoredEntity(2, 1, c.getTime(), "d"));
        writer.commit();

        ItemFilter<StoredEntity> filter = DateIntervalItemFilter.getEmptyFilter();

        ValueReader<StoredEntity, Integer> reader = merger.getReader(StoredEntity.class);
        ClosingIterator<StoredEntity> it = reader.valuesForKey(1, filter);
        Assert.assertTrue(it.hasNext());
        StoredEntity e1 = it.next();
        Assert.assertEquals(1, e1.counterId);
        Assert.assertEquals(1, e1.visitId);
        Assert.assertEquals("ac", e1.content);
        StoredEntity e2 = it.next();
        Assert.assertEquals(1, e2.counterId);
        Assert.assertEquals(2, e2.visitId);
        Assert.assertEquals("b", e2.content);
        Assert.assertFalse(it.hasNext());

        ClosingIterator<StoredEntity> it2 = reader.valuesForKey(2, filter);
        StoredEntity e3 = it2.next();
        Assert.assertEquals(2, e3.counterId);
        Assert.assertEquals(1, e3.visitId);
        Assert.assertEquals("d", e3.content);
        Assert.assertFalse(it2.hasNext());

        ClosingIterator<StoredEntity> it3 = reader.valuesForKey(3, filter);
        Assert.assertFalse(it3.hasNext());

        //Тестируем, насколько успешно отработает merge двух файлов
        ChunkWriter writer2 = merger.createWriter(new Date());
        ItemBuffer<StoredEntity> buffer2 =  writer2.getItemBuffer(StoredEntity.class);
        c.set(2011, 1, 1);
        buffer2.put(new StoredEntity(1, 1, c.getTime(), "e"));
        c.set(2011, 1, 5);
        buffer2.put(new StoredEntity(2, 1, c.getTime(), "f"));
        writer2.commit();

        testMergedFile(merger);
        merger.destroy();

        // Тестируем, что на старте успешно подцепляются файлы
        MergedFileSetImpl master = createMerger(dir, true);
        testMergedFile(master);
        //master.destroy();

        // Тестируем репликацию на низком уровне
        File dir2 = Files.createTempDir();
        MergedFileSetImpl slave = createMerger(dir2, true);
        File repData = File.createTempFile("rep", "merger");
        RandomAccessFile replica = new RandomAccessFile(repData, "rw");
        slave.sendQueryToMaster(replica);
        replica.seek(0);
        SlaveQuery ids = SlaveQuery.readQueryFromSlave(replica);
        replica.setLength(0);
        master.sendChunksToSlave(ids, replica);
        replica.seek(0);
        slave.syncChunksFrom(replica);
        testMergedFile(slave);
        slave.destroy();
        ru.yandex.metrika.util.io.Files.deleteDirectoryContents(dir2);
        replica.close();
        repData.delete();

        // Тестируем репликацию через сокеты
        MasterReplicator mr = new MasterReplicator();
        mr.setDb(master);
        mr.setPort(12666);
        mr.afterPropertiesSet();

        slave = createMerger(dir2, true);
        SlaveReplicator sr = new SlaveReplicator();
        sr.setLastReplicaTime(null);
        sr.setMasterHost(new MasterHostLocatorImpl("localhost"));
        sr.setDb(slave);
        sr.setMasterPort(12666);
        sr.afterPropertiesSet();
        // Ждем, пока приедет первая реплика
        while (sr.getLastReplicaTime() == null) {
            Thread.sleep(100);
        }
        testMergedFile(slave);
        sr.destroy();
        mr.destroy();
        master.destroy();

        deleteMerger(dir);
        deleteMerger(dir2);

    }

    private static Date makeDateFromYMD(int year,int month, int date) {
        LocalDate localDate = new LocalDate(year, month, date);
        return localDate.toDateTime(LocalTime.MIDNIGHT).toLocalDateTime().toDate();
    }

    private static void writeChunkRandomFull(MergedFileSet set) {
        Random rand = new Random();
        Date date_ = makeDateFromYMD(2011, 1, rand.nextInt(25) + 1);
        ChunkWriter writer = set.createWriter(date_);
        ItemBuffer<StoredEntity> buffer =  writer.getItemBuffer(StoredEntity.class);
        buffer.put(new StoredEntity(rand.nextInt(100) + 1, rand.nextInt(100) + 1, date_, Integer.toString(rand.nextInt(100))));
        writer.commit();
    }

    private static void writeChunk(MergedFileSet set, int counterId, int visitId) {
        Date date_ = makeDateFromYMD(2011, 1, 1);
        ChunkWriter writer = set.createWriter(date_);
        ItemBuffer<StoredEntity> buffer =  writer.getItemBuffer(StoredEntity.class);
        buffer.put(new StoredEntity(counterId, visitId, date_, "ololo"));
        writer.commit();
    }

    private static void writeChunk(MergedFileSet set, int counterId, int visitIdStart, int visitIdEnd) {
        Date date_ = makeDateFromYMD(2011, 1, 1);
        ChunkWriter writer = set.createWriter(date_);
        ItemBuffer<StoredEntity> buffer =  writer.getItemBuffer(StoredEntity.class);
        for (int i = visitIdStart; i <= visitIdEnd; i++) {
            buffer.put(new StoredEntity(counterId, i, date_, "ololo"));
        }
        writer.commit();
    }

    @Test
    public void testIteratorMerge() {
        Log4jSetup.basicSetup(Level.DEBUG);
        File dir = Files.createTempDir();

        MergedFileSet dsmfsi = createMerger(dir);

        for (int i = 0; i < 1000; i++) {
            writeChunkRandomFull(dsmfsi);
        }

        ItemFilter<StoredEntity> filter = DateIntervalItemFilter.getEmptyFilter();

        ValueReader<StoredEntity, Integer> reader = dsmfsi.getReader(StoredEntity.class);

        ClosingIterator<StoredEntity> it = reader.allValues(filter);

        StoredEntity last;
        assertTrue(it.hasNext());
        assertNotNull(last = it.next());
        while (it.hasNext()) {
            StoredEntity current = it.next();
            assertTrue(ENTITY_COMPARATOR.compare(last, current) <= 0);
        }

        deleteMerger(dir);
    }

    @Test
    public void testMultithreadedWrite() throws Exception {
        Log4jSetup.basicSetup(Level.DEBUG);
        File dir = Files.createTempDir();

        final MergedFileSet dsmfsi = createMerger(dir, false, 2, 2);
        final int counters = 12;
        final int visits = 100;

        ThreadPoolExecutor executor = Pools.newNamedFixedThreadPool(8, "pool");
        for (int i = 1; i <= counters; i++) {
            final int j = i;
            executor.submit(new Runnable() {
                @Override
                public void run() {
                    for (int i = 1; i <= visits; i++) {
                        writeChunk(dsmfsi, j, i);
                    }
                }
            });
        }
        executor.shutdown();
        executor.awaitTermination(1000, TimeUnit.DAYS);
        ClosingIterator<StoredEntity> iterator = dsmfsi.getReader(StoredEntity.class).allValues(ItemFilter.EMPTY);
        int c = 1;
        int v = 1;
        while(iterator.hasNext()) {
            if (v > visits) {
                c += 1;
                v = 1;
            }
            StoredEntity storedEntity = iterator.next();
            assertEquals(storedEntity.toString(), c, storedEntity.counterId);
            assertEquals(storedEntity.toString(), v, storedEntity.visitId);
            v += 1;
        }
        assertEquals(counters, c);
        assertEquals(visits + 1, v);

        deleteMerger(dir);

    }

    @Test
    public void testMultipleReaders() throws Exception {
        Log4jSetup.basicSetup();
        File dir = Files.createTempDir();

        final MergedFileSetImpl dsmfsi = createMerger(dir);
        final int counters = 8;
        final int visits = 100;

        ThreadPoolExecutor executor = Pools.newNamedFixedThreadPool(8, "pool");
        for (int i = 1; i <= counters; i++) {
            final int j = i;
            executor.submit(new Runnable() {
                @Override
                public void run() {
                    for (int i = 1; i <= visits; i++) {
                        writeChunk(dsmfsi, j, i);
                    }
                }
            });
        }
        executor.shutdown();
        executor.awaitTermination(1000, TimeUnit.DAYS);

        dsmfsi.mergeForced();

        ThreadPoolExecutor executorp = Pools.newNamedFixedThreadPool(8, "pecker");
        ThreadPoolExecutor executorg = Pools.newNamedFixedThreadPool(8, "grabber");

        executorp.submit(new Runnable() {
            @Override
            public void run() {
                for (int k = 0; k < 1000; k++) {
                    ClosingIterator<StoredEntity> iterator = dsmfsi.getReader(StoredEntity.class).allValues(ItemFilter.EMPTY);
                    int c = 1;
                    int v = 1;
                    while (iterator.hasNext()) {
                        if (v > visits) {
                            c += 1;
                            v = 1;
                        }
                        StoredEntity storedEntity = iterator.next();
                        assertEquals(storedEntity.toString(), c, storedEntity.counterId);
                        assertEquals(storedEntity.toString(), v, storedEntity.visitId);
                        v += 1;
                    }
                    assertEquals(counters, c);
                    assertEquals(visits + 1, v);
                    try {
                        iterator.close();
                    } catch (IOException e) {
                        e.printStackTrace();  //To change body of catch statement use File | Settings | File Templates.
                    }
                    System.out.println("pecker:" + k);
                }
            }
        });
        Thread.sleep(100);

        executorg.submit(new Runnable() {
            @Override
            public void run() {
                List<ClosingIterator<StoredEntity>> iterators = Lists.newArrayList();
                for (int k = 0; k < 1024/*chunk pool size*/; k++) {
                    ClosingIterator<StoredEntity> iterator = dsmfsi.getReader(StoredEntity.class).allValues(ItemFilter.EMPTY);
                    iterators.add(iterator);
                    System.out.println("grabber:" + k);
                }
                System.out.println("iterators grabbed");
                for (ClosingIterator<StoredEntity> iterator : iterators) {
                    int c = 1;
                    int v = 1;
                    while (iterator.hasNext()) {
                        if (v > visits) {
                            c += 1;
                            v = 1;
                        }
                        StoredEntity storedEntity = iterator.next();
                        assertEquals(storedEntity.toString(), c, storedEntity.counterId);
                        assertEquals(storedEntity.toString(), v, storedEntity.visitId);
                        v += 1;
                    }
                    assertEquals(counters, c);
                    assertEquals(visits + 1, v);
                }
            }
        });
        executorp.shutdown();
        executorg.shutdown();
        assertTrue(executorp.awaitTermination(1, TimeUnit.MINUTES));
        assertTrue(executorg.awaitTermination(1, TimeUnit.MINUTES));

        deleteMerger(dir);
    }

    @Test
    public void testHashing() throws Exception {
        Log4jSetup.basicSetup(Level.DEBUG);
        File dir = Files.createTempDir();

        MergedFileSet mergedFileSet = createMerger(dir);
        ChunkWriter writer = mergedFileSet.createWriter(new Date());
        ItemBuffer<StoredEntity> buffer = writer.getItemBuffer(StoredEntity.class);
        Calendar c = Calendar.getInstance();
        c.set(2011, 1, 1);
        buffer.put(new StoredEntity(2, 1, c.getTime(), "d"));
        buffer.put(new StoredEntity(1, 1, c.getTime(), "a"));
        buffer.put(new StoredEntity(1, 2, c.getTime(), "c"));
        buffer.put(new StoredEntity(1, 1, c.getTime(), "b"));
        writer.commit();
        ClosingIterator<StoredEntity> it =
                mergedFileSet.getReader(StoredEntity.class).allValues(new ItemFilter.EmptyItemFilter<>());
        int index = 0;
        while(it.hasNext()) {
            StoredEntity entity = it.next();
            switch(index) {
                case 0: assertEquals("ab", entity.content); break;
                case 1: assertEquals("c", entity.content); break;
                case 2: assertEquals("d", entity.content); break;
            }
            index += 1;
        }
        it.close();

        deleteMerger(dir);
    }

    @Test
    public void testMergeForced() {
        Log4jSetup.basicSetup(Level.DEBUG);
        File dir = Files.createTempDir();
        MergedFileSetImpl merger = createMerger(dir, true);
        ChunkWriter writer = merger.createWriter(new Date());
        ItemBuffer<StoredEntity> buffer =  writer.getItemBuffer(StoredEntity.class);
        Calendar c = Calendar.getInstance();
        c.set(2011, 1, 1);
        buffer.put(new StoredEntity(1, 1, c.getTime(), "a"));
        buffer.put(new StoredEntity(1, 2, c.getTime(), "b"));
        c.set(2011, 1, 2);
        buffer.put(new StoredEntity(1, 1, c.getTime(), "c"));
        c.set(2011, 1, 1);
        buffer.put(new StoredEntity(2, 1, c.getTime(), "d"));
        c.set(2011, 1, 7);
        buffer.put(new StoredEntity(2, 1, c.getTime(), "d"));
        writer.commit();

        writer = merger.createWriter(new Date());
        buffer =  writer.getItemBuffer(StoredEntity.class);
        c.set(2012, 1, 1);
        buffer.put(new StoredEntity(1, 1, c.getTime(), "a"));
        buffer.put(new StoredEntity(1, 2, c.getTime(), "b"));
        c.set(2012, 1, 2);
        buffer.put(new StoredEntity(1, 1, c.getTime(), "c"));
        c.set(2012, 1, 1);
        buffer.put(new StoredEntity(4, 1, c.getTime(), "d"));
        c.set(2012, 1, 7);
        buffer.put(new StoredEntity(4, 1, c.getTime(), "d"));
        writer.commit();

        try {
            merger.mergeForced();
        } catch (IOException e) {
            Assert.fail();
        }

        Assert.assertEquals(1, merger.getAllChunks().size());
        Assert.assertEquals(2, Iterators.size(
                merger.getReader(StoredEntity.class).valuesForKey(1, ItemFilter.EmptyItemFilter.<StoredEntity>getInstance())
        ));
        Assert.assertEquals(1, Iterators.size(
                merger.getReader(StoredEntity.class).valuesForKey(2, ItemFilter.EmptyItemFilter.<StoredEntity>getInstance())
        ));
        Assert.assertEquals(1, Iterators.size(
                merger.getReader(StoredEntity.class).valuesForKey(4, ItemFilter.EmptyItemFilter.<StoredEntity>getInstance())
        ));

        deleteMerger(dir);
    }

    private static void testMergedFile(MergedFileSetImpl merger) {
        ItemFilter<StoredEntity> filter = DateIntervalItemFilter.getEmptyFilter();
        ValueReader<StoredEntity, Integer>  reader = merger.getReader(StoredEntity.class);
        ClosingIterator<StoredEntity> it4 = reader.valuesForKey(1, filter);
        StoredEntity e4 = it4.next();
        Assert.assertEquals(1, e4.counterId);
        Assert.assertEquals(1, e4.visitId);
        Assert.assertEquals("ace", e4.content);

        StoredEntity e5 = it4.next();
        Assert.assertEquals(1, e5.counterId);
        Assert.assertEquals(2, e5.visitId);
        Assert.assertEquals("b", e5.content);
        Assert.assertFalse(it4.hasNext());


        ClosingIterator<StoredEntity> it5 = reader.valuesForKey(2, filter);
        StoredEntity e6 = it5.next();
        Assert.assertEquals(2, e6.counterId);
        Assert.assertEquals(1, e6.visitId);
        Assert.assertEquals("df", e6.content);
        Assert.assertFalse(it5.hasNext());
    }

}
