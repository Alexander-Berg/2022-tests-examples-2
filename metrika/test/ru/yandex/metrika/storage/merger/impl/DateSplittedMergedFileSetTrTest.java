package ru.yandex.metrika.storage.merger.impl;

import java.io.BufferedInputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileFilter;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.PipedInputStream;
import java.io.PipedOutputStream;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Date;
import java.util.HashSet;
import java.util.List;
import java.util.Properties;
import java.util.Random;
import java.util.Set;
import java.util.function.Predicate;

import com.codahale.metrics.MetricRegistry;
import com.google.common.collect.Lists;
import com.google.common.io.Files;
import junit.framework.Assert;
import org.apache.logging.log4j.Level;
import org.joda.time.LocalDate;
import org.joda.time.LocalTime;
import org.junit.Ignore;
import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.util.FileSystemUtils;

import ru.yandex.metrika.storage.merger.ChunkWriter;
import ru.yandex.metrika.storage.merger.DataStreamConfiguration;
import ru.yandex.metrika.storage.merger.ItemBuffer;
import ru.yandex.metrika.storage.merger.ItemFilter;
import ru.yandex.metrika.storage.merger.MergedFileSet;
import ru.yandex.metrika.storage.merger.ValueReader;
import ru.yandex.metrika.storage.merger.iterator.ClosingIterator;
import ru.yandex.metrika.storage.merger.replica.ReplicableDB;
import ru.yandex.metrika.util.id.IdGeneratorGeneratorSimple;
import ru.yandex.metrika.util.log.Log4jSetup;
import ru.yandex.metrika.util.time.DateSplittedUtils;
import ru.yandex.metrika.util.time.DayNumber;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;
import static ru.yandex.metrika.storage.merger.impl.Constants.MAX_DATE_PROPERTY;
import static ru.yandex.metrika.storage.merger.impl.Constants.MIN_DATE_PROPERTY;
import static ru.yandex.metrika.storage.merger.impl.Constants.dateFormat;

/**
 * Created by orantius on 4/16/14.
 */
@Ignore
public class DateSplittedMergedFileSetTrTest {
    private static final Logger log = LoggerFactory.getLogger(DateSplittedMergedFileSetTrTest.class);

    public static DateSplittedMergedFileSetTr createDSMFSI(File dir) {
        DataStreamConfiguration<StoredEntity, Integer> config = new DataStreamConfiguration<>();
        config.setComparator(MergedFileSetImplTest.ENTITY_COMPARATOR);
        config.setFoldingFunction(new MergedFileSetImplTest.EntityMerger());
        config.setDeSerializer(new MergedFileSetImplTest.EntityDeserializer());
        config.setEntityClass(StoredEntity.class);
        config.setIndex(new MergedFileSetImplTest.EntityHashIndex());
        config.setSerializer(new MergedFileSetImplTest.EntitySerializer());
        config.setName("testEntity");
        config.setTimeExtractor(new MergedFileSetImplTest.EntityTimeExtractor());
        return new DateSplittedMergedFileSetTr(1024, dir, 100, 100, new DataStreamConfiguration[]{config}, new IdGeneratorGeneratorSimple(), new MetricRegistry());
    }

    public static DateSplittedMergedFileSetTr createDSMFSI(File dir, int mergeThreshold) {
        DataStreamConfiguration<StoredEntity, Integer> config = new DataStreamConfiguration<>();
        config.setComparator(MergedFileSetImplTest.ENTITY_COMPARATOR);
        config.setFoldingFunction(new MergedFileSetImplTest.EntityMerger());
        config.setDeSerializer(new MergedFileSetImplTest.EntityDeserializer());
        config.setEntityClass(StoredEntity.class);
        config.setIndex(new MergedFileSetImplTest.EntityHashIndex());
        config.setSerializer(new MergedFileSetImplTest.EntitySerializer());
        config.setName("testEntity");
        config.setTimeExtractor(new MergedFileSetImplTest.EntityTimeExtractor());
        return new DateSplittedMergedFileSetTr(1024, dir, mergeThreshold, 2, new DataStreamConfiguration[]{config}, new IdGeneratorGeneratorSimple(), new MetricRegistry());
    }


    public static Date makeDateFromYMD(int year, int month, int date) {
        LocalDate localDate = new LocalDate(year, month, date);
        return localDate.toDateTime(LocalTime.MIDNIGHT).toLocalDateTime().toDate();
    }

    public static boolean dbByDateIsCreated(File root, Date date) {
        File dbFolder = new File(root, DateSplittedUtils.generateNameFromDate(date));
        return dbFolder.exists();
    }

    public static void dbByDateCompareToList(File root, Date[] dates) {
        File[] files = root.listFiles(new FileFilter() {
            @Override
            public boolean accept(File pathname) {
                if(pathname.getName().endsWith("_tr")) return false;
                File[] files = pathname.listFiles();
                if (files == null) {
                    return false;
                }
                for (File file : files) {
                    if (!file.getName().matches(".{8}\\.del") && !"frozen".equals(file.getName())) {
                        return true;
                    }
                }
                return false;
            }
        });
        assertEquals(dates.length, files.length);
        out:
        for (File file : files) {
            Date fileDate = DateSplittedUtils.generateDateFromString(file.getName());
            for (Date date : dates) {
                if (date.equals(fileDate)) {
                    continue out;
                }
            }
            fail();
        }
    }

    public static void writeChunkRandomFull(MergedFileSet set) {
        Random rand = new Random(5345);
        Date date_ = makeDateFromYMD(2011, 1, rand.nextInt(25) + 1);
        ChunkWriter writer = set.createWriter(date_);
        ItemBuffer<StoredEntity> buffer = writer.getItemBuffer(StoredEntity.class);
        buffer.put(new StoredEntity(rand.nextInt(100) + 1, rand.nextInt(100) + 1, date_, Integer.toString(rand.nextInt(100))));
        writer.commit();
    }

    public static void writeChunkRandom(MergedFileSet set, int year, int month, int date, int seed) {
        Random rand = new Random(seed);
        Date date_ = makeDateFromYMD(year, month, date);
        ChunkWriter writer = set.createWriter(date_);
        ItemBuffer<StoredEntity> buffer = writer.getItemBuffer(StoredEntity.class);
        buffer.put(new StoredEntity(rand.nextInt(100) + 1, rand.nextInt(100) + 1, date_, Integer.toString(rand.nextInt(100))));
        writer.commit();
    }

    public static void writeChunkRandomHuge(MergedFileSet set, int year, int month, int date) {
        Random rand = new Random();
        Date date_ = makeDateFromYMD(year, month, date);
        ChunkWriter writer = set.createWriter(date_);
        ItemBuffer<StoredEntity> buffer = writer.getItemBuffer(StoredEntity.class);
        for (int i = 1; i < 100001; i++) {
            buffer.put(new StoredEntity(i, rand.nextInt(100) + 1, date_, Integer.toString(rand.nextInt(100))));
        }
        writer.commit();
    }


    @Test
    public void testForcedMerge() {
        Log4jSetup.basicSetup(Level.INFO);
        File dir = Files.createTempDir();

        DateSplittedMergedFileSetImpl dsmfsi = createDSMFSI(dir, 500);
        dsmfsi.setNeedExpire(true);

        for (int i = 2; i <= 30; i++) {
            writeChunkRandom(dsmfsi, 2011, 1, i, 42424242);
        }
        /*writeChunkRandomHuge(dsmfsi, 2011, 1, 1);
        ItemFilter<TestEntity> filter = DateIntervalItemFilter.getEmptyFilter();

        ValueReader<TestEntity, Integer> reader = dsmfsi.getReaderForDate(TestEntity.class, DayNumber.generateDayFromString("2011_01_01"));
        ClosingIterator<TestEntity> iterator = reader.allValues(filter);*/

        /*for (int i = 0; i < 10000; i++) {
            iterator.next();
        }
        Date[] dates = new Date[16];
        for (int i = 30; i > 15; i--) {
            dates[i - 16] = makeDateFromYMD(2011, 1, i);
        }
        dates[15] = makeDateFromYMD(2011, 1, 1);
        dbByDateCompareToList(dir, dates);*/

        /*for (int i = 10000; i < 100000; i++) {
            iterator.next();
        }
        try {
            iterator.close();
        } catch (IOException e) {
            e.printStackTrace();  //To change body of catch statement use File | Settings | File Templates.
        }
        dsmfsi.expire();*/


        Date[] dates2 = new Date[15];
        for (int i = 30; i > 15; i--) {
            dates2[i - 16] = makeDateFromYMD(2011, 1, i);
        }
        dbByDateCompareToList(dir, dates2);

        FileSystemUtils.deleteRecursively(dir);
    }

    @Test
    public void testDateBordersTest() {
        Log4jSetup.basicSetup(Level.INFO);
        File dir = Files.createTempDir();

        MergedFileSet dsmfsi = createDSMFSI(dir);
        Date date = makeDateFromYMD(2011, 1, 2);
        ChunkWriter writer = dsmfsi.createWriter(date);
        ItemBuffer<StoredEntity> buffer = writer.getItemBuffer(StoredEntity.class);
        buffer.put(new StoredEntity(1, 1, date, "a"));
        buffer.put(new StoredEntity(1, 2, date, "b"));
        writer.commit();

        Date oneLeft = new Date(date.getTime() - 1);
        writer = dsmfsi.createWriter(oneLeft);
        buffer = writer.getItemBuffer(StoredEntity.class);
        buffer.put(new StoredEntity(1, 1, oneLeft, "a"));
        buffer.put(new StoredEntity(1, 2, oneLeft, "b"));
        writer.commit();

        dbByDateCompareToList(dir, new Date[]{makeDateFromYMD(2011, 1, 1), makeDateFromYMD(2011, 1, 2)});

        FileSystemUtils.deleteRecursively(dir);
    }

    @Test
    public void testMFSICreationTest() {
        Log4jSetup.basicSetup(Level.INFO);
        File dir = Files.createTempDir();

        MergedFileSet dsmfsi = createDSMFSI(dir);
        ChunkWriter writer = dsmfsi.createWriter(makeDateFromYMD(2011, 1, 1));
        ItemBuffer<StoredEntity> buffer = writer.getItemBuffer(StoredEntity.class);
        buffer.put(new StoredEntity(1, 1, makeDateFromYMD(2011, 1, 1), "a"));
        buffer.put(new StoredEntity(1, 2, makeDateFromYMD(2011, 1, 1), "b"));
        writer.commit();

        writer = dsmfsi.createWriter(makeDateFromYMD(2011, 1, 2));
        buffer = writer.getItemBuffer(StoredEntity.class);
        buffer.put(new StoredEntity(1, 1, makeDateFromYMD(2011, 1, 2), "c"));
        buffer.put(new StoredEntity(2, 1, makeDateFromYMD(2011, 1, 2), "d"));
        writer.commit();

        assertTrue(dbByDateIsCreated(dir, makeDateFromYMD(2011, 1, 1)));
        assertTrue(dbByDateIsCreated(dir, makeDateFromYMD(2011, 1, 2)));
        dbByDateCompareToList(dir, new Date[]{makeDateFromYMD(2011, 1, 1), makeDateFromYMD(2011, 1, 2)});


        ItemFilter<StoredEntity> filter = DateIntervalItemFilter.getEmptyFilter();

        ValueReader<StoredEntity, Integer> reader = dsmfsi.getReader(StoredEntity.class);
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

        FileSystemUtils.deleteRecursively(dir);
    }

    @Test
    public void testDotDel() {
        for (int z = 434343; z < 434344; z++) {

            Log4jSetup.basicSetup(Level.INFO);
            File dir = Files.createTempDir();

            DateSplittedMergedFileSetImpl dsmfsi = createDSMFSI(dir);
            dsmfsi.setNeedExpire(true);

            for (int i = 1; i < 16; i++) {
                for (int j = 0; j < 10; j++) {
                    writeChunkRandom(dsmfsi, 2011, 1, i, z);
                }
            }
            //writeChunkRandom(dsmfsi, 2011, 1, 16);
            ItemFilter<StoredEntity> filter = DateIntervalItemFilter.getEmptyFilter();

            ValueReader<StoredEntity, Integer> reader = dsmfsi.getReader(StoredEntity.class);
            ClosingIterator<StoredEntity> it = reader.allValues(filter);

            while (it.hasNext() && it.next().time != makeDateFromYMD(2011, 1, 1).getTime()) {
                // do nothing
            }

            writeChunkRandom(dsmfsi, 2011, 1, 16, z);

            for (int j = 0; j < 9; j++) {
                while (it.hasNext() && it.next().time != makeDateFromYMD(2011, 1, 1).getTime()) {
                    assertTrue(it.hasNext());
                }
            }
            while (it.hasNext()) {
                assertTrue(it.next().time != makeDateFromYMD(2011, 1, 1).getTime());
            }
            while (it.hasNext()) {
                it.next();
            }

            log.info(":::::::::::::::::::::::::::::::{}::::::::::::::::::::::", z);

            FileSystemUtils.deleteRecursively(dir);
        }

    }

    @Test
    public void testIteratorMerge() {
        Log4jSetup.basicSetup(Level.INFO);
        File dir = Files.createTempDir();

        MergedFileSet dsmfsi = createDSMFSI(dir);

        for (int i = 0; i < 1000; i++) {
            writeChunkRandomFull(dsmfsi);
        }

        ItemFilter<StoredEntity> filter = DateIntervalItemFilter.getEmptyFilter();

        ValueReader<StoredEntity, Integer> reader = dsmfsi.getReader(StoredEntity.class);

        ClosingIterator<StoredEntity> it = reader.allValues(filter);

        Comparator<StoredEntity> comparator = MergedFileSetImplTest.ENTITY_COMPARATOR;
        StoredEntity last;
        assertTrue(it.hasNext());
        assertNotNull(last = it.next());
        while (it.hasNext()) {
            StoredEntity current = it.next();
            assertTrue(comparator.compare(last, current) <= 0);
        }

        FileSystemUtils.deleteRecursively(dir);

    }

    private void compareDS(DateSplittedMergedFileSetImpl d1, DateSplittedMergedFileSetImpl d2) {
        ItemFilter<StoredEntity> filter = DateIntervalItemFilter.getEmptyFilter();
        ValueReader<StoredEntity, Integer> reader = d1.getReader(StoredEntity.class);
        ClosingIterator<StoredEntity> it1 = reader.allValues(filter);

        ItemFilter<StoredEntity> filter2 = DateIntervalItemFilter.getEmptyFilter();
        ValueReader<StoredEntity, Integer> reader2 = d2.getReader(StoredEntity.class);
        ClosingIterator<StoredEntity> it2 = reader2.allValues(filter2);

        Comparator<StoredEntity> comparator = MergedFileSetImplTest.ENTITY_COMPARATOR;
        ArrayList<StoredEntity> storedEntities1 = Lists.newArrayList(it1);
        ArrayList<StoredEntity> storedEntities2 = Lists.newArrayList(it2);

        assertEquals(storedEntities1.size(), storedEntities2.size());
        while (it1.hasNext()) {
            assertTrue(it2.hasNext());
            assertEquals(0, comparator.compare(it1.next(), it2.next()));
        }
        assertFalse(it2.hasNext());
    }


    @Test
    public void dumpTest() throws Exception {
        Log4jSetup.basicSetup(Level.INFO);
        File dir = Files.createTempDir();

        File d1 = new File(dir, "d1");
        d1.mkdir();
        DateSplittedMergedFileSetImpl dsmfsi = createDSMFSI(d1);

        final Set<Integer> counters = new HashSet<>();
        for (int i = 0; i < 1000; i++) {
            Random rand = new Random(6465546);
            Date date_ = makeDateFromYMD(2011, 1, rand.nextInt(25) + 1);
            ChunkWriter writer = dsmfsi.createWriter(date_);
            ItemBuffer<StoredEntity> buffer = writer.getItemBuffer(StoredEntity.class);
            int counterId = rand.nextInt(100) + 1;
            counters.add(counterId);
            buffer.put(new StoredEntity(counterId, rand.nextInt(100) + 1, date_, Integer.toString(rand.nextInt(100))));
            writer.commit();
        }
        Predicate<StoredEntity> predicate = hitInfo -> counters.contains(hitInfo.counterId);

        File dumpFile = new File(dir, "dump");
        assertTrue(dumpFile.mkdir());

        Set<Short> setNames = dsmfsi.getSetsMapReadCopy().keySet();
        for (Short name : setNames) {
            MinMaxTime times = new MinMaxTime();
            File setFile = new File(dumpFile, DateSplittedUtils.getDateString(name));
            assertTrue(setFile.mkdir());
            ValueReader<StoredEntity, Integer> reader = dsmfsi.getSetsMapReadCopy().get(name).getReader(StoredEntity.class);
            reader.dumpTo(new File(setFile, "dump.dump"), predicate, times);
            Properties props = new Properties();
            props.setProperty(MIN_DATE_PROPERTY, dateFormat.print(times.getMinTime()));
            props.setProperty(MAX_DATE_PROPERTY, dateFormat.print(times.getMaxTime()));
            FileOutputStream propOut = new FileOutputStream(new File(setFile, "chunk.properties"));
            try {
                props.store(propOut, "");
            } finally {
                propOut.close();
            }
        }

        File d2 = new File(dir, "d2");
        d2.mkdir();
        DateSplittedMergedFileSetImpl dsmfsi2 = createDSMFSI(d2);

        File[] files = dumpFile.listFiles();
        for (File dbRoot : files) {
            InputStream[] streams = new InputStream[1];
            streams[0] = new BufferedInputStream(new FileInputStream(new File(dbRoot, "dump.dump")), 1024 * 64);
            try {
                Properties props = Chunk.loadChunkProperties(dbRoot);
                Date minTime = dateFormat.parseDateTime(props.getProperty(MIN_DATE_PROPERTY)).toDate();
                Date maxTime = dateFormat.parseDateTime(props.getProperty(MAX_DATE_PROPERTY)).toDate();
                dsmfsi2.createWriter(maxTime).loadDump(new Class[]{StoredEntity.class}, streams, minTime, maxTime);
            } finally {
                streams[0].close();
            }
        }

        compareDS(dsmfsi, dsmfsi2);

        FileSystemUtils.deleteRecursively(dir);

    }


    @Test
    public void testReplicationMove() throws Exception {
        Log4jSetup.basicSetup(Level.INFO);
        File dir1 = Files.createTempDir();

        DateSplittedMergedFileSetImpl set1 = createDSMFSI(dir1);

        for (int i = 0; i < 100; i++) {
            writeChunkRandomFull(set1);
        }

        File dir2 = Files.createTempDir();

        DateSplittedMergedFileSetImpl set2 = createDSMFSI(dir2);

        ReplicableDB rep1 = set1;
        ReplicableDB rep2 = set2;

        PipedOutputStream pipedStream = new PipedOutputStream();
        DataOutputStream outputStream = new DataOutputStream(pipedStream);
        DataInputStream inputStream = new DataInputStream(new PipedInputStream(pipedStream, 1000000));

        PipedOutputStream pipedStream2 = new PipedOutputStream();
        DataOutputStream outputStream2 = new DataOutputStream(pipedStream2);
        DataInputStream inputStream2 = new DataInputStream(new PipedInputStream(pipedStream2, 1000000));

        rep2.sendQueryToMaster(outputStream);
        outputStream.close();
        rep1.handleSlaveRequest(inputStream, outputStream2);
        outputStream2.close();
        rep2.syncChunksFrom(inputStream2);

        compareDS(set1, set2);

        FileSystemUtils.deleteRecursively(dir1);
        FileSystemUtils.deleteRecursively(dir2);
    }

    /**
     * тут проверяется, что если на реплике есть данные, которых нет на мастере, то они никуда не денутся после отработки раунда репликации.
     * @throws Exception
     */
    @Test
    public void testReplicationDelete() throws Exception {
        Log4jSetup.basicSetup(Level.INFO);
        File dir1 = Files.createTempDir();

        DateSplittedMergedFileSetImpl set1 = createDSMFSI(dir1);

        File dir2 = Files.createTempDir();

        DateSplittedMergedFileSetImpl set2 = createDSMFSI(dir2);

        for (int i = 0; i < 100; i++) {
            writeChunkRandomFull(set2);
        }

        ReplicableDB rep1 = set1;
        ReplicableDB rep2 = set2;

        PipedOutputStream pipedStream = new PipedOutputStream();
        DataOutputStream outputStream = new DataOutputStream(pipedStream);
        DataInputStream inputStream = new DataInputStream(new PipedInputStream(pipedStream, 1000000));

        PipedOutputStream pipedStream2 = new PipedOutputStream();
        DataOutputStream outputStream2 = new DataOutputStream(pipedStream2);
        DataInputStream inputStream2 = new DataInputStream(new PipedInputStream(pipedStream2, 1000000));

        rep2.sendQueryToMaster(outputStream);
        outputStream.close();
        rep1.handleSlaveRequest(inputStream, outputStream2);
        outputStream2.close();
        rep2.syncChunksFrom(inputStream2);

        List<StoredEntity> list1 = Lists.newArrayList(set1.getReader(StoredEntity.class).allValues(ItemFilter.EMPTY));
        List<StoredEntity> list2 = Lists.newArrayList(set2.getReader(StoredEntity.class).allValues(ItemFilter.EMPTY));
        assertEquals(0, list1.size());
        assertEquals(1, list2.size());
        //compareDS(set1, set2);

        ItemFilter<StoredEntity> filter = DateIntervalItemFilter.getEmptyFilter();
        ValueReader<StoredEntity, Integer> reader = set1.getReader(StoredEntity.class);
        ClosingIterator<StoredEntity> it1 = reader.allValues(filter);

        assertFalse(it1.hasNext());

        assertEquals(1, set2.getSetsMapReadCopy().size());
        assertEquals(0, set1.getSetsMapReadCopy().size());

        FileSystemUtils.deleteRecursively(dir1);
        FileSystemUtils.deleteRecursively(dir2);
    }

    @Test
    public void testGenerators() throws Exception {
        Date date = makeDateFromYMD(2012, 1, 2);
        assertEquals("2012_01_02", DateSplittedUtils.generateNameFromDate(date));
        assertEquals(date, DateSplittedUtils.generateDateFromString(DateSplittedUtils.generateNameFromDate(date)));
        assertEquals(date, DateSplittedUtils.generateDateFromString("2012_01_02"));
        assertEquals(DateSplittedUtils.getDateString(DayNumber.calcDayForDate(date.getTime())), DateSplittedUtils.generateNameFromDate(date));
        //System.out.println(DayNumber.calcDayForDate(date.getTime()));
    }

}
