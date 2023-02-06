package ru.yandex.metrika.util.io;

import java.util.Random;

import gnu.trove.map.hash.TIntIntHashMap;
import org.junit.Test;

/**
 * @author orantius
 * @version $Id$
 * @since 7/16/12
 */
public class StreamSplitterTest {

    @Test
    public void testPrecise() throws Exception {
        byte[] buf = new byte[10000];
        for(int i = 0; i < 10000; i++){
            buf[i] = (byte) (i % 50);
        }
        StreamSplitter target = new StreamSplitter(new FastByteArrayInputStream(buf), (byte) 50);

        ByteFragment next = null;
        TIntIntHashMap lenCount = new TIntIntHashMap();
        while((next = target.next()) != null) {
            System.out.println("next = " + next.length());
            lenCount.adjustOrPutValue(next.getLen(), 1,1);
        }
        System.out.println(lenCount);
    }

    @Test
    public void test1k128() throws Exception {
        byte[] buf = new byte[1000];
        Random r = new Random(1);
        r.nextBytes(buf);
        StreamSplitter target = new StreamSplitter(new FastByteArrayInputStream(buf), (byte) 0x13, 128);
        ByteFragment next = null;
        while((next = target.next()) != null) {
            System.out.println("next = " + next.length());

        }
        /*read 128 bytes  from stream
        double size
        read 128 bytes  from stream
        return 215 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=0, len=215}
        shift 216 bytes
        read 216 bytes  from stream
        return 102 bytes as next()
        next = ByteFragment{buf=[B@10dc6b5, start=0, len=102}
        shift 103 bytes
        read 103 bytes  from stream
        return 207 bytes as next()
        next = ByteFragment{buf=[B@170bea5, start=0, len=207}
        shift 208 bytes
        read 208 bytes  from stream
        return 95 bytes as next()
        next = ByteFragment{buf=[B@f47396, start=0, len=95}
        shift 96 bytes
        read 96 bytes  from stream
        double size
        read 121 bytes  from stream
        read -1 bytes  from stream
        return 376 bytes as next()
        next = ByteFragment{buf=[B@d0af9b, start=0, len=376}
        read -1 bytes  from stream*/
    }

    @Test
    public void test1k() throws Exception {
        byte[] buf = new byte[1000];
        Random r = new Random(1);
        r.nextBytes(buf);
        StreamSplitter target = new StreamSplitter(new FastByteArrayInputStream(buf), (byte) 0x13);
        ByteFragment next = null;
        while((next = target.next()) != null) {
            System.out.println("next = " + next.length());

        }
        /*read 1000 bytes  from stream
        return 215 bytes as next()
        next = ByteFragment{buf=[B@10dc6b5, start=0, len=215}
        return 102 bytes as next()
        next = ByteFragment{buf=[B@10dc6b5, start=216, len=102}
        return 207 bytes as next()
        next = ByteFragment{buf=[B@10dc6b5, start=319, len=207}
        return 95 bytes as next()
        next = ByteFragment{buf=[B@10dc6b5, start=527, len=95}
        read -1 bytes  from stream
        return 376 bytes as next()
        next = ByteFragment{buf=[B@10dc6b5, start=623, len=376}
        read -1 bytes  from stream*/
    }

    @Test
    public void test10k() throws Exception {
        byte[] buf = new byte[10000];
        Random r = new Random(1);
        r.nextBytes(buf);
        StreamSplitter target = new StreamSplitter(new FastByteArrayInputStream(buf), (byte) 0x13);
        ByteFragment next = null;
        while((next = target.next()) != null) {
            System.out.println("next = " + next.length());

        }
        /*read 8192 bytes  from stream
        return 215 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=0, len=215}
        return 102 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=216, len=102}
        return 207 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=319, len=207}
        return 95 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=527, len=95}
        return 704 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=623, len=704}
        return 170 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=1328, len=170}
        return 45 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=1499, len=45}
        return 16 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=1545, len=16}
        return 121 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=1562, len=121}
        return 164 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=1684, len=164}
        return 291 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=1849, len=291}
        return 279 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=2141, len=279}
        return 221 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=2421, len=221}
        return 329 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=2643, len=329}
        return 280 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=2973, len=280}
        return 604 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=3254, len=604}
        return 52 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=3859, len=52}
        return 91 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=3912, len=91}
        return 63 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=4004, len=63}
        return 847 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=4068, len=847}
        return 165 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=4916, len=165}
        return 575 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=5082, len=575}
        return 104 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=5658, len=104}
        return 81 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=5763, len=81}
        return 263 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=5845, len=263}
        return 164 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=6109, len=164}
        return 232 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=6274, len=232}
        return 617 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=6507, len=617}
        return 119 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=7125, len=119}
        return 117 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=7245, len=117}
        return 429 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=7363, len=429}
        return 268 bytes as next()
        next = ByteFragment{buf=[B@1d0fafc, start=7793, len=268}
        shift 8062 bytes
        read 1808 bytes  from stream
        return 139 bytes as next()
        next = ByteFragment{buf=[B@10dc6b5, start=0, len=139}
        return 140 bytes as next()
        next = ByteFragment{buf=[B@10dc6b5, start=140, len=140}
        return 178 bytes as next()
        next = ByteFragment{buf=[B@10dc6b5, start=281, len=178}
        return 34 bytes as next()
        next = ByteFragment{buf=[B@10dc6b5, start=460, len=34}
        return 76 bytes as next()
        next = ByteFragment{buf=[B@10dc6b5, start=495, len=76}
        return 153 bytes as next()
        next = ByteFragment{buf=[B@10dc6b5, start=572, len=153}
        return 1002 bytes as next()
        next = ByteFragment{buf=[B@10dc6b5, start=726, len=1002}
        return 162 bytes as next()
        next = ByteFragment{buf=[B@10dc6b5, start=1729, len=162}
        read -1 bytes  from stream
        return 45 bytes as next()
        next = ByteFragment{buf=[B@10dc6b5, start=1892, len=45}
        read -1 bytes  from stream*/
    }







}
