package ru.yandex.metrika.zkqueue.core.flap;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.concurrent.atomic.AtomicBoolean;

import org.apache.curator.test.TestingZooKeeperMain;
import org.apache.zookeeper.ZooDefs;
import org.apache.zookeeper.proto.CreateRequest;
import org.apache.zookeeper.server.ByteBufferInputStream;
import org.apache.zookeeper.server.NIOServerCnxn;
import org.apache.zookeeper.server.NIOServerCnxnFactory;
import org.apache.zookeeper.server.Request;
import org.apache.zookeeper.server.ZooKeeperServer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * A connection factory that will behave like the NIOServerCnxnFactory except that
 * it will unexpectedly close the connection right after the <b>first</b> znode has
 * been created in Zookeeper.
 * Subsequent create operations will succeed.
 * <p>
 * The class was taken and modified from curator source here: http://bit.ly/2BXflZp
 */
public class ChaosMonkeyCnxnFactory extends NIOServerCnxnFactory {
    private static final Logger log = LoggerFactory.getLogger(ChaosMonkeyCnxnFactory.class);

    public static final String FIRST_LOCK_PREFIX_PROPERTY = "first-lock-path";

    @Override
    public void startup(ZooKeeperServer zks) throws IOException, InterruptedException {
        super.startup(new ChaosMonkeyZookeeperServer(zks));
    }

    static class ChaosMonkeyZookeeperServer extends ZooKeeperServer {
        private final ZooKeeperServer zks;
        private AtomicBoolean alreadyFailed = new AtomicBoolean();

        ChaosMonkeyZookeeperServer(ZooKeeperServer zks) {
            this.zks = zks;
            setTxnLogFactory(zks.getTxnLogFactory());
            setTickTime(zks.getTickTime());
            setMinSessionTimeout(zks.getMinSessionTimeout());
            setMaxSessionTimeout(zks.getMaxSessionTimeout());
        }

        @Override
        public void startup() {
            super.startup();
            if (zks instanceof TestingZooKeeperMain.TestZooKeeperServer) {
                ((TestingZooKeeperMain.TestZooKeeperServer) zks).noteStartup();
            } else {
                throw new RuntimeException("Unknown ZooKeeperServer: " + zks.getClass());
            }
        }

        @Override
        public void submitRequest(Request si) {
            // Submit the request to the legacy Zookeeper server
            log.debug("Applied : " + si.toString());
            super.submitRequest(si);
            // Raise an error if a lock is created
            if ((si.type == ZooDefs.OpCode.create) || (si.type == ZooDefs.OpCode.create2)) {
                final CreateRequest createRequest = new CreateRequest();
                try {
                    final ByteBuffer duplicate = si.request.duplicate();
                    duplicate.rewind();
                    ByteBufferInputStream.byteBuffer2Record(duplicate, createRequest);
                    final String prefix = System.getProperty(FIRST_LOCK_PREFIX_PROPERTY);
                    if (createRequest.getPath().startsWith(prefix)
                            && alreadyFailed.compareAndSet(false, true)) {
                        // The znode has been created, close the connection and don't tell it to client
                        log.warn("Closing connection right after " + createRequest.getPath() + " creation");
                        ((NIOServerCnxn) si.cnxn).close();
                    }
                } catch (Exception e) {
                    // Should not happen
                    ((NIOServerCnxn) si.cnxn).close();
                }
            }
        }
    }
}
