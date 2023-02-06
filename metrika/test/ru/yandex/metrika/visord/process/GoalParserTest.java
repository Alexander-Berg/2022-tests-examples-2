package ru.yandex.metrika.visord.process;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;

import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.chunks.visitlog.GoalIds;
import ru.yandex.metrika.chunks.visitlog.ReachGoalParser;

/**
 * @author orantius
 * @version $Id$
 * @since 8/3/11
 */
@Ignore("METRIQA-936")
public class GoalParserTest {

    byte[] blob1 = {-23,-98,13,-26,-66,-39,-15,4,0,-19,-98,13,0,0,-23,-98,13,56,0,-21,-98,13,0,0,-23,-98,13,-97,1,0,-21,-98,13,0,0,-23,-98,13,8,0,-21,-98,13,0,0,-23,-98,13,41,0,-21,-98,13,0,0};
    byte[] blob2 = {-126,-65,13,-99,-64,-39,-15,4,0,-2,-66,13,0,0,-126,-65,13,7,0,-2,-66,13,0,0,-126,-65,13,5,0,-2,-66,13,0,0};
    byte[] blob3 = {-55,-84,26,-31,-65,-39,-15,4,0,-48,-45,28,0,0,-55,-84,26,105,0,-48,-45,28,0,0,-55,-84,26,16,0,-48,-45,28,0,0};
    @Test
    public void testParse() throws Exception {
        ReachGoalParser gp = new ReachGoalParser();
        readFile(gp, "/home/orantius/Desktop/1.blob");
        readFile(gp, "/home/orantius/Desktop/2.blob");
        readFile(gp, "/home/orantius/Desktop/3.blob");
    }

    private GoalIds readFile(ReachGoalParser gp, String pathname) throws IOException {
        File f = new File(pathname);
        BufferedInputStream is = new BufferedInputStream(new FileInputStream(f));
        byte[] bytes = new byte[(int) f.length()];
        //noinspection ResultOfMethodCallIgnored
        is.read(bytes);
        GoalIds parse = gp.parseToGoalIds(bytes);
        return parse;
    }
}
