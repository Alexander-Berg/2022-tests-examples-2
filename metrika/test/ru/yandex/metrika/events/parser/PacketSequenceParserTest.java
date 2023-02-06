package ru.yandex.metrika.events.parser;

import java.io.File;
import java.util.Arrays;
import java.util.List;

import com.google.common.collect.Lists;
import com.google.common.io.Files;
import gnu.trove.list.array.TByteArrayList;
import org.junit.Test;

import ru.yandex.metrika.events.Event;
import ru.yandex.metrika.util.Base64;

import static org.junit.Assert.assertEquals;

/**
 * @author Arthur Suilin
 */
public class PacketSequenceParserTest  {

    @Test
    public void testFoo() {
        //byte[] dd = {65,81,70,109,65,67,115,65,65,78,77,74,118,119,107,67,65,71,111,65,99,119,65,66,65,107,52,66,68,81,65,66,65,48,52,67,71,103,73,117,83,103,69,69,84,103,77,97,65,117,111,80,65,81,86,71,66,66,111,65,65,78,77,74,74,119,76,54,114,65,69,71,82,103,85,97,52,103,69,65,42,103,85,104,65,105,117,51,65,81,100,71,66,107,45,105,65,81,68,104,65,120,89,67,98,107,89,66,67,69,52,72,85,65,75,115,73,119,69,74,84,103,104,88,65,113,119,106,65,81,112,71,67,86,72,118,65,119,65,122,70,103,73,76,75,103,73,80,67,105,89,69,65,103,56,71,113,119,73,103,65,81,116,71,66,66,111,65,74,57,77,74,50,103,103,67,102,72,119,66,68,69,89,76,71,103,66,111,48,119,109,90,67,65,73,119,86,65,69,78,82,103,119,97,65,67,45,84,67,101,119,70,65,103,45,97,65,81,53,71,68,82,114,99,65,83,45,51,66,42,119,70,65,115,117,72,65,81,57,71,68,104,114,105,65,83,45,120,66,120,48,67,88,73,99,66,69,70,89,80,65,99,69,68,76,50,73,101,118,68,77,67,71,110,89,67,68,120,66,68,70,81,69,82,82,103,52,97,52,103,70,77,56,81,99,49,65,111,88,108,65,82,74,79,69,82,111,67,114,98,119,66,69,48,89,83,71,117,73,66,84,79,89,70,78,103,75,48,88,103,69,85,82,104,77,66,121,81,78,77,79,122,81,67,117,86,119,67,69,66,81,49,72,103,69,86,82,103,52,97,52,103,71,66,65,102,69,72,109,81,85,67,48,88,85,66,70,107,52,86,71,103,75,100,69,119,69,88,84,104,89,97,65,106,66,121,65,82,104,79,70,120,111,67,117,70,119,66,71,85,52,89,71,103,73,78,122,103,69,97,82,104,107,97,52,103,71,66,65,102,69,72,71,103,76,77,111,103,73,81,71,112,77,67,68,81,69,98,82,104,107,97,52,103,71,99,65,102,69,72,119,65,81,67,76,112,77,66,72,69,89,98,71,117,73,66,110,65,72,120,66,120,48,67,53,103,89,66,72,85,89,99,71,117,73,66,110,81,72,120,66,120,119,67,76,74,119,66,72,107,52,100,83,81,73,52,89,103,73,81,72,111,52,67,65,103,69,102,82,104,115,97,52,103,71,53,65,102,69,72,72,81,76,103,100,81,69,103,82,104,56,97,52,103,71,54,65,102,69,72,72,65,73,115,110,65,69,104,84,105,66,74,65,106,104,105,65,104,65,104,103,119,73,66,65,83,74,87,73,85,109,69,65,114,115,66,50,103,69,90,71,68,56,67,122,90,77,67,69,83,76,89,65,82,103,66,73,48,89,98,71,117,73,66,49,103,72,120,66,120,48,67,53,102,119,66,74,69,89,106,71,117,73,66,49,119,72,120,66,120,119,67,76,74,119,66,74,85,52,107,83,81,73,52,89,103,69,109,86,105,86,74,104,65,76,89,65,100,111,66,71,85,50,53,65,115,50,84,65,104,69,109,122,103,69,76,65,104,69,109,119,81,69,88,65,83,100,71,71,120,114,105,65,102,77,66,56,81,99,100,65,117,68,68,65,83,104,71,74,120,114,105,65,102,81,66,56,81,99,99,65,105,121,99,65,83,108,79,75,69,107,67,79,71,73,66,75,108,89,112,83,89,81,67,57,81,72,97,65,82,109,88,104,103,76,78,107,119,73,83,75,114,73,66,65,81,73,83,75,113,99,66,66,81,73,84,75,112,52,66,66,119,73,84,75,112,119,66,66,65,73,84,75,112,115,66,65,65,73,85,74,112,107,66,65,119,73,85,73,112,52,66,65,103,69,114,86,104,53,74,104,65,75,102,65,100,111,66,71,85,50,53,65,115,50,84,65,104,81,114,115,65,69,65};
        /*{
                1,1,102,0,  43,0,0,-45,9,-65,9,2,0,106,0,115,0,
                1,2,78,1,   13,0,
                1,3,78,2,   26,2,46,74,
                1,4,78,3,   26,2,-22,15,
                1,5,70,4,   26,0,0,-45,9,39,2,-6,-84,
                1,6,70,5,   26,-30,1,0,-6,5,33,2,43,-73,
                1,7,70,6,   79,-30,1,0,-31,3,22,2,110,70,
                1,8,78,7,   80,2,-84,35,
                1,9,78,8,   87,2,-84,35,
                1,10,70,9,  81,-17,3,0,51,22,2,11,42,

                2,15,10,38,4,
                2,15,6,-85,2,32,

                1,11,70,4,  26,0,39,-45,9,-38,8,2,124,124,
                1,12,70,11, 26,0,104,-45,9,-103,8,2,48,84,
                1,13,70,12, 26,0,47,-45,9,-20,5,2,15,-38,
                1,14,70,13, 26,-36,1,47,-9,7,-20,5,2,-53,-121,
                1,15,70,14, 26,-30,1,47,-15,7,29,2,92,-121,
                1,16,86,15, 1,-63,3,47,98,30,-68,51,2,26,118,

                2,15,16,67,21,

                1,17,70,14, 26,-30,1,76,-15,7,53,2,-123,-27,
                1,18,78,17, 26,2,-83,-68,
                1,19,70,18, 26,-30,1,76,-26,5,54,2,-76,94,
                1,20,70,19, 1,-55,3,76,59,52,2,-71,92,

                2,16,20,53,30,

                1,21,70,14, 26,-30,1,-127,1,-15,7,-103,5,2,-47,117,
                1,22,78,21, 26,2,-99,19,
                1,23,78,22, 26,2,48,114,
                1,24,78,23, 26,2,-72,92,
                1,25,78,24, 26,2,13,-50,
                1,26,70,25, 26,-30,1,-127,1,-15,7,26,2,-52,-94,

                2,16,26,-109,2,13,

                1,27,70,25, 26,-30,1,-100,1,-15,7,-64,4,2,46,-109,
                1,28,70,27, 26,-30,1,-100,1,-15,7,29,2,-26,6,
                1,29,70,28, 26,-30,1,-99,1,-15,7,28,2,44,-100,
                1,30,78,29, 73,2,56,98,2,16,30,-114,2,2,
                1,31,70,27, 26,-30,1,-71,1,-15,7,29,2,-32,117,
                1,32,70,31, 26,-30,1,-70,1,-15,7,28,2,44,-100,
                1,33,78,32, 73,2,56,98,2,16,33,-125,2,1,
                1,34,86,33, 73,-124,2,-69,1,-38,1,25,24,63,2,-51,-109,

                2,17,34,-40,1,24,

                1,35,70,27, 26,-30,1,-42,1,-15,7,29,2,-27,-4,
                1,36,70,35, 26,-30,1,-41,1,-15,7,28,2,44,-100,
                1,37,78,36, 73,2,56,98,
                1,38,86,37, 73,-124,2,-40,1,-38,1,25,77,-71,2,-51,-109,

                2,17,38,-50,1,11,
                2,17,38,-63,1,23,

                1,39,70,27, 26,-30,1,-13,1,-15,7,29,2,-32,-61,
                1,40,70,39, 26,-30,1,-12,1,-15,7,28,2,44,-100,
                1,41,78,40, 73,2,56,98,
                1,42,86,41, 73,-124,2,-11,1,-38,1,25,-105,-122,2,-51,-109,

                2,18,42,-78,1,1,
                2,18,42,-89,1,5,
                2,19,42,-98,1,7,
                2,19,42,-100,1,4,
                2,19,42,-101,1,0,
                2,20,38,-103,1,3,
                2,20,34,-98,1,2,

                1,43,86,30, 73,-124,2,-97,1,-38,1,25,77,-71,2,-51,-109,

                2,20,43,-80,1,0}*/
        // настоящие гуру парсят бинарный поток на глазок.
        byte[] decoded = {
                1,1,100,0,  43,0,0,-45,9,-65,9,2,0,106,0,115,0,
                1,2,76,1,   13,0,
                1,3,76,2,   26,2,46,74,
                1,4,76,3,   26,2,-22,15,
                1,5,68,4,   26,0,0,-45,9,39,2,-6,-84,
                1,6,68,5,   26,-30,1,0,-6,5,33,2,43,-73,
                1,7,68,6,   79,-30,1,0,-31,3,22,2,110,70,
                1,8,76,7,   80,2,-84,35,
                1,9,76,8,   87,2,-84,35,
                1,10,68,9,  81,-17,3,0,51,22,2,11,42,

                2,15,10,38,4,
                2,15,6,-85,2,32,

                1,11,68,4,  26,0,39,-45,9,-38,8,2,124,124,
                1,12,68,11, 26,0,104,-45,9,-103,8,2,48,84,
                1,13,68,12, 26,0,47,-45,9,-20,5,2,15,-38,
                1,14,68,13, 26,-36,1,47,-9,7,-20,5,2,-53,-121,
                1,15,68,14, 26,-30,1,47,-15,7,29,2,92,-121,
                1,16,84,15, 1,-63,3,47,98,30,-68,51,2,26,118,

                2,15,16,67,21,

                1,17,68,14, 26,-30,1,76,-15,7,53,2,-123,-27,
                1,18,76,17, 26,2,-83,-68,
                1,19,68,18, 26,-30,1,76,-26,5,54,2,-76,94,
                1,20,68,19, 1,-55,3,76,59,52,2,-71,92,

                2,16,20,53,30,

                1,21,68,14, 26,-30,1,-127,1,-15,7,-103,5,2,-47,117,
                1,22,76,21, 26,2,-99,19,
                1,23,76,22, 26,2,48,114,
                1,24,76,23, 26,2,-72,92,
                1,25,76,24, 26,2,13,-50,
                1,26,68,25, 26,-30,1,-127,1,-15,7,26,2,-52,-94,

                2,16,26,-109,2,13,

                1,27,68,25, 26,-30,1,-100,1,-15,7,-64,4,2,46,-109,
                1,28,68,27, 26,-30,1,-100,1,-15,7,29,2,-26,6,
                1,29,68,28, 26,-30,1,-99,1,-15,7,28,2,44,-100,
                1,30,76,29, 73,2,56,98,2,16,30,-114,2,2,
                1,31,68,27, 26,-30,1,-71,1,-15,7,29,2,-32,117,
                1,32,68,31, 26,-30,1,-70,1,-15,7,28,2,44,-100,
                1,33,76,32, 73,2,56,98,2,16,33,-125,2,1,
                1,34,84,33, 73,-124,2,-69,1,-38,1,25,24,63,2,-51,-109,

                2,17,34,-40,1,24,

                1,35,68,27, 26,-30,1,-42,1,-15,7,29,2,-27,-4,
                1,36,68,35, 26,-30,1,-41,1,-15,7,28,2,44,-100,
                1,37,76,36, 73,2,56,98,
                1,38,84,37, 73,-124,2,-40,1,-38,1,25,77,-71,2,-51,-109,

                2,17,38,-50,1,11,
                2,17,38,-63,1,23,

                1,39,68,27, 26,-30,1,-13,1,-15,7,29,2,-32,-61,
                1,40,68,39, 26,-30,1,-12,1,-15,7,28,2,44,-100,
                1,41,76,40, 73,2,56,98,
                1,42,84,41, 73,-124,2,-11,1,-38,1,25,-105,-122,2,-51,-109,

                2,18,42,-78,1,1,
                2,18,42,-89,1,5,
                2,19,42,-98,1,7,
                2,19,42,-100,1,4,
                2,19,42,-101,1,0,
                2,20,38,-103,1,3,
                2,20,34,-98,1,2,

                1,43,84,30, 73,-124,2,-97,1,-38,1,25,77,-71,2,-51,-109,

                2,20,43,-80,1,0};
        //public EventLog(int seqNumber, byte[] data, int counterId, long visitorId, int clientHitId, long clientTime) {
        //EventLog eventLog = new EventLog(1, decoded, 1143050, 2509716311292408523L, 563527404, 1296043892000L);
        int activityScore = PacketSequenceParser.parse(decoded).calcActivityScore();
        assertEquals(26, activityScore);
    }

    public static void main(String[] args) throws Exception {
        printFromPost();
    }

        //чтение из файла после SELECT dayNumber, eventData, counterId FROM WV_7.events WHERE dayNumber=2018 LIMIT 100 INTO OUTFILE '/opt/mysql/out2.tsv' FIELDS TERMINATED BY '\t' ESCAPED BY '\\' LINES TERMINATED BY '\n'
    public static void printFromTSV() throws Exception {
        byte[] packet = Files.toByteArray(new File("/home/jkee/out6.tsv"));
        List<byte[]> rows = byteSplit(packet, '\n');
        for (byte[] row : rows) {
            List<byte[]> columns = byteSplit(row, '\t');
            byte[] unescape = unescape(columns.get(1));
            StateFull stateFull = PacketSequenceParser.parseFull(unescape);
            for (Event event : stateFull.getObjects()) {
                System.out.println(event);
            }
        }
    }

    public static void printFromPost() {
        String post = "HACxDPsEsQzmCQEBRAArAACxDOYJAAECTQEN5vgAAQNgAhoCpQHlAegJjQcHAHcAcgBhAHAAcABlAHIAAQRkAxq5AeUBwAmNBwkAYwBvAG4AdABhAGkAbgBlAHICP4kBBWQEGtEB9gGQCcIGBwBjAG8AbgB0AGUAbgB0AAEGZAUa0QH2Ad0GwgYEAHQAZQB4AHQAAQdFBiDRAY4D3QaqBXMpAAEITQcacykC6sYBCUUIGvUBoQO4BliAzQKfDQEKRQla9QGhA7gGToDNAAIBCqcCTQICCt4CRwELUQo1AvUB1QO4BhC547njAAIKC9MDAwEMUQo1AfUBuwO4BhB8wHzAAAIMDPIEDx8MDOcGygMAAAEDDAA1AQ1FCE-1AfkDuAasBPK9AAEOTQ1Q8r0AAQ9FDlf1AfkDuAYovIwAARBBD1EBlQT5A5gEKAAAAB8NEOcG-wMAAAEDDQBqARFBDlcB9QGhBLgGKN83AAESQRFRAZUEoQSYBCgAAAAfDRLnBrQEAAABAw0AoAEBE0EOVwL1AckEuAYoJJcAARRBE1EBlQTJBJgEKAAAAAIOFNICIR8TFOcG6gQAAAEDEwDVAQEVQQ5XBPUBmQW4BiagKAABFkEVUQGVBJkFmAQmGOsAHxQW5wafBQAAAQMUAIoCARdBDlcF9QG-BbgGJl2sAAEYQRdRAZUEvwWYBCZKCQAfFBjnBtQFAAABAxQAwAIBGUEOVwb1AeUFuAYpvEMAARpBGVEBlQTlBZgEKQAAAB8VGucGigYAAAEDFQD1AgEbQQ5XCPUBtga4BihhvAABHEEbUQGVBLYGmAQoAAAAAhUc0gIJAh4c0QIJAiEc0AIJAR1BDlcH9QGOBrgGKAvMAAEeQR1RAZUEjgaYBCgAAAACIR7SAh0CIRrUAiYCIhrUAgACIhbQAh4BH0EOVwP1AfEEuAYo74YAASBBH1EBlQTxBJgEKMtcAAIiIMsCFAEhZBAvlQT5A84CHgMAZgBpAG8CP3UHIQAAA2ZpbwABImQSL5UEoQTOAh4FAHAAaABvAG4AZQIcZAciAAAFcGhvbmUAASNkFC*VBMkEzgIeBQBlAG0AYQBpAGwCChQHIwAABWVtYWlsAAEkRSAalQTxBGAc0qMCixcBJUUkR5UE8QRKEzr-Aid7ByUAAQpEYXRlX01vbnRoAAEmQSAaAf8E8QRgHPgiAosXASdFJkf-BPEEShNgoAI*aQcnAAEIRGF0ZV9EYXkAAShFIC-pBfEEXh4AAAJngQcoAAAHYXBwdGltZQABKUUWGpUEmQW9AhwY6wKJFQEqRSlHlQSZBcsCEytcAkyrByoAAQpwcm9mZXNzaW9uAAErRRgalQS-Bb0CHEoJAokVASxFK0eVBL8FywIT2GoCONUHLAABCmRlcGFydG1lbnQAAS1kGi*VBOUFzgIeBgBkAG8AYwB0AG8AcgKNwwctAAAGZG9jdG9yAAEuZB4vlQSOBs4CHgsAYwBvAG4AdABhAGMAdAB0AGkAbQBlAp*3By4AAAtjb250YWN0dGltZQABL2QcL5UEtgbOAh4IAHAAcgBvAGIAbABlAG0AcwJnXQcvAAAIcHJvYmxlbXMAATBBDlcJ9QHeBrgGKsi-AAExQTBRAZUE3gaYBCoMEgABMkUxGpUE3ga9AhwMEgKJFQEzRTJHlQTeBssCE7mvAsVBBzMAAQlzdWJzY3JpYmUAATRBDlcK9QGIB7gGRlLcAtZgATVBNFEBlQSIB5gERtv6AAE2ZDUvlQSSB3oeDABmAGEAcQBLAGUAeQBzAHQAcgBpAG4AZwLjiQc2AAAJa2V5c3RyaW5nAAE3QQ5XC-UBzge4BlcAAAABOEE3UQGVBM4HmARXAAAAATlFOC*VBNgH3wE0AAACcWMCIyPJAgoCIyLFAgQCIwnjBE4CJAzfBAABOlUKNfUBoQO4BhBKwUrBAAIkOt0EBwE7RQYa0QGpAt0GZZRHAr4IATxFO1rRAcAC3QZOlEcCwVkCJDz5BEEBPVE8NQHRAd8C3QYgo5ijmAACKz3kBBcCKz3iBB0CLDzcBEcCLAjRBA0CLDqgBA8CLQqRBCoCLQr-A0oCLSHRAQYCLiHHARQCLiHCARwCMiHCARsCMiHCARYCMyHCARIENCHCARIBETQhHjYhwgESASA2IcIBEgECNyHBARMCNxC9ASMCOCK4AQ0COBK1AR4COCOwAQICOyOuAQMCPBKsAScCPRKrASMCPRKrAR8CPiKrARsEPyKrARsBDz8SPyEOPxE-Ih5BIqsBGwEgQSKrARsBAkIiqgEcAkIjqQECAkMjqQEHAkQjpwEMAkQjpQEQBEYjpAESAQ9GEkYiDkYRRiMeSCOkARIBIEgjpAESAQJJI6QBEwJKI6QBGgJKJzoBAksmORUCSyqjAQYCSxafASICTCubARkCTC2ZARACTBqXASQCTC6VAQsCTS6VARMCTy6UARICUC6WAQ4CUC6XAQgCUS6XAQICUhqXAScCUhqXASMCVBqXAR8CVS2XARsEWC2WARsBD1gSWCMOWBFYLR5aLZYBGwEgWi2WARsBAlsalAEfAlsukgEJAlwukQEVBGEukQEVAQ9hEmEtDmERYS4eZC6RARUBIGQukQEVAQJkLpABFgJlHo8BHgJlHo0BJQJmL4oBAwJmL4cBCARoL4UBCwEPaBJoLg5oEWgvHmovhQELASBqL4UBCwECbC*FAQwCbC*EARMCbS*EARoCbRyCAR4CbhyBASICbhyAASYCbzN*BAJvM30IAnAzfA0CcDN6EgJxMncXAnEydhsCcjF0HwJzMXMjAnQxcCYCdTVuAAJ1NWsDAnY1ZwcCdjZkAAJ3NmAEAnc2XAcCeDZWCgJ4Nk8OAnk2RBQCeTY0GgJ6NSIqAno1Fy0CezUPMwJ7NQg4An41BzgffjWaBMIHAAABA34AqgMCfzkEHwKBATkBHwE*RTdR9QHOB6ACVwAAAAKBAT6dAikCggE*mAIpAoIBPpECKAKDAT6JAigCgwE*-gEpAoQBPvQBKwKEAT7sAS4ChQE*4wEzH4UBPtQDgwgAAAEDhQEA4AMChQEEmQLVBgKHAQSVAtgGAocBBI8C2wYCiAEEiALfBgKIAQT2AfAGD8EBEsEBLwK9AgTQAfAGAr0CBP4B4gYCvQIErALUBgK*Agi8Ap0FAr4COBRPAr4COCZFAr8COTExAr8COTQuAsICOTQsDsQCEcQCLwTEAjk0LAEPxAISxAIvDsQCEcQCOR7GAjk0LAEgxgI5NCwBC8YCAAYlJygqLDM_";
        byte[] decode = Base64.VISOR.decode(post);
        StateFull stateFull = PacketSequenceParser.parseFull(decode);
        stateFull.getObjects().forEach(System.out::println);
    }

    private static byte[] unescape(byte[] src) {
        TByteArrayList unescaped = new TByteArrayList();
        boolean esc = false;
        for (byte b : src) {
            if (esc) {
                esc = false;
                switch (b) {
                    case '0': unescaped.add((byte)'\0'); break;
                    default: unescaped.add(b);
                }
            }
            else if (b == '\\') esc = true;
            else unescaped.add(b);
        }
        return unescaped.toArray();
    }

    private static List<byte[]> byteSplit(byte[] packet, char separator) {
        List<byte[]> split = Lists.newArrayList();
        boolean esc = false;
        int left = 0;
        for (int i = 0; i < packet.length; i++) {
            byte b = packet[i];
            if (esc) esc = false;
            else if (b == '\\') esc = true;
            else if (b == separator) {
                byte[] part = Arrays.copyOfRange(packet, left, i);
                split.add(part);
                left = i + 1;
            }
        }
        if(!esc && left != packet.length) split.add(Arrays.copyOfRange(packet, left, packet.length));
        return split;
    }

}

