package ru.yandex.metrika.util;

import java.io.IOException;
import java.util.Collection;
import java.util.HashMap;
import java.util.Map;

import com.sun.net.httpserver.HttpHandler;
import gnu.trove.list.array.TIntArrayList;
import org.apache.logging.log4j.Level;
import org.junit.After;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;
import org.springframework.jdbc.core.JdbcOperations;
import org.springframework.remoting.httpinvoker.SimpleHttpInvokerServiceExporter;
import org.springframework.remoting.support.SimpleHttpServerFactoryBean;

import ru.yandex.metrika.util.collections.MapUtil;
import ru.yandex.metrika.util.log.Log4jSetup;
import ru.yandex.metrika.util.route.HttpInvokeRouter;
import ru.yandex.metrika.util.route.Route;
import ru.yandex.metrika.util.route.RouteConfigSimple;
import ru.yandex.metrika.util.route.RouteConfigurerXml;
import ru.yandex.metrika.util.route.layers.LayerDao;
import ru.yandex.metrika.util.route.layers.LayerInfoProvider;

import static org.junit.Assert.assertEquals;
import static org.mockito.Mockito.mock;

/**
 * @author orantius
 * @version $Id$
 * @since 9/29/11
 */
@Ignore
public class HttpInvokeRouterTest {

    private static final RouteConfigSimple MASTER_ADDRESS = new RouteConfigSimple("127.0.0.1", 8085);
    private static final RouteConfigSimple SLAVE_ADDRESS = new RouteConfigSimple("127.0.0.1", 8086);
    private static final String REMOTING_URL = "/remoting/url";
    static Map<String, Map<Integer, RouteConfigSimple>> layers = MapUtil.map(
            new String[]{"label" ,
                    "label_replica"},
            new Map[]{
                    MapUtil.map(new Integer[]{1}, new RouteConfigSimple[]{MASTER_ADDRESS}),
                    MapUtil.map(new Integer[]{1}, new RouteConfigSimple[]{SLAVE_ADDRESS}),
            }
    );
    private HttpInvokeRouter<DummyService> dr;

    DummyService main = new DummyServiceImpl("main");
    DummyService repl = new DummyServiceImpl("repl");

    private SimpleHttpServerFactoryBean master;
    private SimpleHttpServerFactoryBean slave;

    @Before
    public void setUp() throws Exception {
        Log4jSetup.basicSetup(Level.DEBUG);
        buildDR();

        startMaster();
        startSlave();
    }

    private void startSlave() {
        try {
            slave = buildServer(SLAVE_ADDRESS.getPort(), repl);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void startMaster() {
        try {
            master = buildServer(MASTER_ADDRESS.getPort(), main);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    @After
    public void tearDown() {
        master.destroy();
        slave.destroy();
    }

    private static SimpleHttpServerFactoryBean buildServer(int port, DummyService impl) throws IOException {
        SimpleHttpInvokerServiceExporter exporter = new SimpleHttpInvokerServiceExporter();
        exporter.setServiceInterface(DummyService.class);
        exporter.setService(impl);
        exporter.afterPropertiesSet();
        SimpleHttpServerFactoryBean server = new SimpleHttpServerFactoryBean();
        server.setPort(port);
        server.setContexts(MapUtil.map(new String[]{REMOTING_URL},
                new HttpHandler[]{exporter}));
        server.afterPropertiesSet();
        return server;
    }

    private void buildDR() throws Exception {
        dr = new HttpInvokeRouter<>(DummyService.class);
        dr.setPath(REMOTING_URL);
        dr.setCounterDao(new CountersImpl());
        //JdbcOperations m = mock(JdbcOperations.class);
        JdbcOperations m2 = mock(JdbcOperations.class);
        //when(m.getJdbcOperations()).thenReturn(m2);

        // dr.setJdbc(m);
        RouteConfigurerXml rcx = new RouteConfigurerXml();
        rcx.setRouter(dr);
        rcx.afterPropertiesSet();
        //dr.afterPropertiesSet();
    }

    /**
     * по умолчанию работаем с мастером
     */
    @Test
    public void testCall() {
        DummyService serviceProxy = dr.getRouteForCounter(42);
        String echo = serviceProxy.echo("42");
        assertEquals("42main", echo);
    }

    /**
     * если мастер падает работаем с репликой
     */
    @Test
    public void testMasterFail() {
        DummyService serviceProxy = dr.getRouteForCounter(42);
        String echo = serviceProxy.echo("42");
        assertEquals("42main", echo);
        master.destroy();
        String echo2 = serviceProxy.echo("43");
        assertEquals("43repl", echo2);
    }

    /**
     * если мастер тухнет, а потом включается, то через некоторое время переключаемся опять на мастер
     */
    @Test
    public void testMasterRestart() {
        DummyService serviceProxy = dr.getRouteForCounter(42);
        {
            String echo = serviceProxy.echo("42");
            assertEquals("42main", echo);
        }
        master.destroy();
        {
            String echo = serviceProxy.echo("43");
            assertEquals("43repl", echo);
        }
        startMaster();
        {
            for(int i = 0; i < 100; i++) {
                String echo = serviceProxy.echo(String.valueOf(i));
                if (i < 41) {
                    assertEquals(i+"repl", echo);
                } else {
                    assertEquals(i+"main", echo);
                }
            }
        }
    }

    /**
     * если работаем с репликой и в это время падает реплика, то делается попытка вызвать мастер. если мастер уже жив - то с него возвращается ответ.
     */
    @Test
    public void testSlaveFail() {
        DummyService serviceProxy = dr.getRouteForCounter(42);
        {
            String echo = serviceProxy.echo("42");
            assertEquals("42main", echo);
        }
        master.destroy();
        {
            String echo = serviceProxy.echo("43");
            assertEquals("43repl", echo);
        }
        startMaster();
        slave.destroy();
        {
            String echo = serviceProxy.echo("44");
            assertEquals("44main", echo);
        }

    }


    static class CountersImpl implements LayerDao, LayerInfoProvider {
        @Override
        public int getLayer(int counterId) {
            return 1;
        }

        @Override
        public boolean isValidLayer(int layer) {
            return layer == 1;
        }


        @Override
        public TIntArrayList getLayers() {
            TIntArrayList res = new TIntArrayList();
            res.add(1);
            return res;
        }

        @Override
        public Map<Integer, Integer> getLayers(Collection<Integer> counterIds) {
            Map<Integer, Integer> layers = new HashMap<>();
            counterIds.forEach(counterId -> layers.put(counterId, 1));
            return layers;
        }
    }

    interface DummyService extends Route {
        String echo(String arg);
    }

    public static class DummyServiceImpl implements DummyService {
        String id ;
        public DummyServiceImpl(String repl) {
            id = repl;
        }

        @Override
        public String echo(String arg) {
            /*try {
                Thread.sleep(10000);
            } catch (InterruptedException e) {
                e.printStackTrace();  //To change body of catch statement use File | Settings | File Templates.
            }*/
            return arg + id;
        }

        @Override
        public void ping() {
            //To change body of implemented methods use File | Settings | File Templates.
        }

        @Override
        public void cleanConnections() {
        }
    }
}
