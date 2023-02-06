package ru.yandex.metrika.util.bloom.exthitid;

import java.io.File;
import java.io.FileInputStream;
import java.io.RandomAccessFile;

/**
 *
 scp orantius@mtfilter02g:/opt/yandex/filterd/10/written-hitQueue/ehit.journal ~/ehit.journal.10
 scp orantius@mtfilter02g:/opt/yandex/filterd/11/written-hitQueue/ehit.journal ~/ehit.journal.11
 scp orantius@mtfilter02g:/opt/yandex/filterd/12/written-hitQueue/ehit.journal ~/ehit.journal.12
 scp orantius@mtfilter02g:/opt/yandex/filterd/13/written-hitQueue/ehit.journal ~/ehit.journal.13
 scp orantius@mtfilter02g:/opt/yandex/filterd/14/written-hitQueue/ehit.journal ~/ehit.journal.14
 scp orantius@mtfilter02g:/opt/yandex/filterd/15/written-hitQueue/ehit.journal ~/ehit.journal.15
 scp orantius@mtfilter02g:/opt/yandex/filterd/16/written-hitQueue/ehit.journal ~/ehit.journal.16
 scp orantius@mtfilter02g:/opt/yandex/filterd/17/written-hitQueue/ehit.journal ~/ehit.journal.17
 scp orantius@mtfilter02g:/opt/yandex/filterd/18/written-hitQueue/ehit.journal ~/ehit.journal.18
 scp orantius@mtfilter02g:/opt/yandex/filterd/1/written-hitQueue/ehit.journal ~/ehit.journal.1
 scp orantius@mtfilter02g:/opt/yandex/filterd/20/written-hitQueue/ehit.journal ~/ehit.journal.20
 scp orantius@mtfilter02g:/opt/yandex/filterd/21/written-hitQueue/ehit.journal ~/ehit.journal.21
 scp orantius@mtfilter02g:/opt/yandex/filterd/22/written-hitQueue/ehit.journal ~/ehit.journal.22
 scp orantius@mtfilter02g:/opt/yandex/filterd/25/written-hitQueue/ehit.journal ~/ehit.journal.25
 scp orantius@mtfilter02g:/opt/yandex/filterd/28/written-hitQueue/ehit.journal ~/ehit.journal.28
 scp orantius@mtfilter02g:/opt/yandex/filterd/5/written-hitQueue/ehit.journal ~/ehit.journal.5
 scp orantius@mtfilter02g:/opt/yandex/filterd/27/written-hitQueue/ehit.journal ~/ehit.journal.27

 offset = 175296512 maxNonZeroByte = 175293143 last zeros = 3369
 offset = 1601536 maxNonZeroByte = 1599383 last zeros = 2153
 offset = 173305856 maxNonZeroByte = 173302103 last zeros = 3753
 offset = 11661312 maxNonZeroByte = 11660663 last zeros = 649
 offset = 49950720 maxNonZeroByte = 49947383 last zeros = 3337
 offset = 78483456 maxNonZeroByte = 78482903 last zeros = 553
 offset = 194396160 maxNonZeroByte = 194395703 last zeros = 457
 offset = 1814528 maxNonZeroByte = 1811543 last zeros = 2985
 offset = 40574976 maxNonZeroByte = 40571543 last zeros = 3433
 offset = 454041600 maxNonZeroByte = 454038743 last zeros = 2857
 offset = 87339008 maxNonZeroByte = 87336503 last zeros = 2505
 offset = 296316928 maxNonZeroByte = 296314103 last zeros = 2825
 offset = 73760768 maxNonZeroByte = 73758263 last zeros = 2505
 offset = 128831488 maxNonZeroByte = 128830103 last zeros = 1385
 offset = 27910144 maxNonZeroByte = 27907223 last zeros = 2921
 offset = 323276800 maxNonZeroByte = 323274743 last zeros = 2057

 scp ~/ehit.journal.10 orantius@mtfilter02g:~
 scp ~/ehit.journal.11 orantius@mtfilter02g:~
 scp ~/ehit.journal.12 orantius@mtfilter02g:~
 scp ~/ehit.journal.13 orantius@mtfilter02g:~
 scp ~/ehit.journal.14 orantius@mtfilter02g:~
 scp ~/ehit.journal.15 orantius@mtfilter02g:~
 scp ~/ehit.journal.16 orantius@mtfilter02g:~
 scp ~/ehit.journal.17 orantius@mtfilter02g:~
 scp ~/ehit.journal.18 orantius@mtfilter02g:~
 scp ~/ehit.journal.1 orantius@mtfilter02g:~
 scp ~/ehit.journal.20 orantius@mtfilter02g:~
 scp ~/ehit.journal.21 orantius@mtfilter02g:~
 scp ~/ehit.journal.22 orantius@mtfilter02g:~
 scp ~/ehit.journal.25 orantius@mtfilter02g:~
 scp ~/ehit.journal.28 orantius@mtfilter02g:~
 scp ~/ehit.journal.5 orantius@mtfilter02g:~
 scp ~/ehit.journal.27 orantius@mtfilter02g:~

 sudo cp ~/ehit.journal.10 /opt/yandex/filterd/10/written-hitQueue/ehit.journal
 sudo cp ~/ehit.journal.11 /opt/yandex/filterd/11/written-hitQueue/ehit.journal
 sudo cp ~/ehit.journal.12 /opt/yandex/filterd/12/written-hitQueue/ehit.journal
 sudo cp ~/ehit.journal.13 /opt/yandex/filterd/13/written-hitQueue/ehit.journal
 sudo cp ~/ehit.journal.14 /opt/yandex/filterd/14/written-hitQueue/ehit.journal
 sudo cp ~/ehit.journal.15 /opt/yandex/filterd/15/written-hitQueue/ehit.journal
 sudo cp ~/ehit.journal.16 /opt/yandex/filterd/16/written-hitQueue/ehit.journal
 sudo cp ~/ehit.journal.17 /opt/yandex/filterd/17/written-hitQueue/ehit.journal
 sudo cp ~/ehit.journal.18 /opt/yandex/filterd/18/written-hitQueue/ehit.journal
 sudo cp ~/ehit.journal.1 /opt/yandex/filterd/1/written-hitQueue/ehit.journal
 sudo cp ~/ehit.journal.20 /opt/yandex/filterd/20/written-hitQueue/ehit.journal
 sudo cp ~/ehit.journal.21 /opt/yandex/filterd/21/written-hitQueue/ehit.journal
 sudo cp ~/ehit.journal.22 /opt/yandex/filterd/22/written-hitQueue/ehit.journal
 sudo cp ~/ehit.journal.25 /opt/yandex/filterd/25/written-hitQueue/ehit.journal
 sudo cp ~/ehit.journal.28 /opt/yandex/filterd/28/written-hitQueue/ehit.journal
 sudo cp ~/ehit.journal.5 /opt/yandex/filterd/5/written-hitQueue/ehit.journal
 sudo cp ~/ehit.journal.27 /opt/yandex/filterd/27/written-hitQueue/ehit.journal
 * @author orantius
 * @version $Id$
 * @since 2/14/14
 */
public class HitJournalFix {
    public static void main(String[] args) {
        //int[] js = new int[] {10, 11, 12,13,14,15,16,17,18,1,20,21,22,25,28,5};
        int[] js = {27};
        for (int j : js) {
            try {
                FileInputStream fis = new FileInputStream(new File("/home/orantius/ehit.journal."+j));
                byte[] buffer = new byte[1000000];

                int offset = 0;
                int maxNonZeroByte = -1;
                int read;
                while((read = fis.read(buffer)) >=0) {
                    for (int i = 0; i < read; i++) {
                        byte b = buffer[i];
                        if(b != 0 ) {
                            maxNonZeroByte = i + offset;
                        }
                    }
                    offset += read;
                }
                System.out.println("offset = " + offset+ " maxNonZeroByte = "+maxNonZeroByte+" last zeros = "+(offset - maxNonZeroByte));
                fis.close();
                RandomAccessFile raf = new RandomAccessFile("/home/orantius/ehit.journal."+j, "rw");
                raf.setLength(maxNonZeroByte+1);
                raf.close();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        /*try {
            Log4jSetup.basicSetup(Level.DEBUG);
            MPMSettings settings = new MPMSettings();
            settings.setDataRoot(new File("/home"));
            settings.setDirName("orantius");
            settings.afterPropertiesSet();
            HitIdTableModified table = new HitIdTableModified(settings, new MaxSeenTime());
            int z = 42;
        } catch (Exception e) {
            e.printStackTrace();
        }*/
    }
}
