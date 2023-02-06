package ru.yandex.metrika.managers;

import org.apache.logging.log4j.Level;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.tool.AllDatabases;
import ru.yandex.metrika.util.log.Log4jSetup;

/**
 * @author lemmsh
 * @since 7/18/14
 */

@Ignore
public class MirrorDaoTest {

    MirrorDaoImpl mirrorDao;

    @Before
    public void setUp() throws Exception {
        mirrorDao = new MirrorDaoImpl();
        mirrorDao.setCountersTemplate(AllDatabases.getTemplate("localhost", 3308, "root", "qwerty", "conv_main"));
        mirrorDao.postConstruct();

        Log4jSetup.basicSetup(Level.DEBUG);
    }

    @Test
    public void testMirrors() throws Exception {

        System.out.println(mirrorDao.getDomain(101024));
        System.out.println(mirrorDao.getDomains(101024));
        System.out.println(mirrorDao.getMirror(101024, 1));
        System.out.println(mirrorDao.findDomain(101024, 1));
        System.out.println(mirrorDao.getMirror(101024, 15));

    }
}
