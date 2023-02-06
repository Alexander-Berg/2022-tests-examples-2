package ru.yandex.metrika.util.metr19165;

import java.io.File;
import java.net.URL;
import java.util.Collections;
import java.util.Iterator;

import org.jsonschema2pojo.AbstractRuleLogger;
import org.jsonschema2pojo.DefaultGenerationConfig;
import org.jsonschema2pojo.Jsonschema2Pojo;
import org.jsonschema2pojo.util.URLUtil;
import org.junit.Ignore;

/**
 *
 * Created by orantius on 12/2/15.
 */
@Ignore
public class SchemaTest {

    public static void main(String[] args) throws Exception {

        DefaultGenerationConfig config = new DefaultGenerationConfig() {
           /* @Override
            public Class<? extends RuleFactory> getCustomRuleFactory() {
                return CustomRuleFactory.class;
            }*/

            /*@Override
            public boolean isUseCommonsLang3() {
                return true;
            }*/

            @Override
            public boolean isUseJodaDates() {
                return true;
            }

            @Override
            public boolean isUseLongIntegers() {
                return true;
            }

            @Override
            public boolean isGenerateBuilders() {
                return true;
            }

            @Override
            public File getTargetDirectory() {
                return new File("/home/orantius/dev/projects/metrika/metrika-api/faced/src/generated-schema");
            }

            @Override
            public Iterator<URL> getSource() {
                //return Collections.singleton(URLUtil.parseURL("file:///home/orantius/dev/projects/metrika/metrika-api/common/src/java/ru/yandex/metrika/util/schemas")).iterator();
                return Collections.singleton(URLUtil.parseURL("file:///home/orantius/dev/projects/metrika/metrika-api/faced/src/java/ru/yandex/metrika/util/schemas")).iterator();
            }
        };
        Jsonschema2Pojo.generate(config, new NoOpRuleLogger());
    }

    public static class NoOpRuleLogger extends AbstractRuleLogger {
        @Override
        public boolean isDebugEnabled() {
            return false;
        }

        @Override
        public boolean isErrorEnabled() {
            return false;
        }

        @Override
        public boolean isInfoEnabled() {
            return false;
        }

        @Override
        public boolean isTraceEnabled() {
            return false;
        }

        @Override
        public boolean isWarnEnabled() {
            return false;
        }

        @Override
        protected void doDebug(String msg) {
        }

        @Override
        protected void doError(String msg, Throwable e) {
        }

        @Override
        protected void doInfo(String msg) {
        }

        @Override
        protected void doTrace(String msg) {
        }

        @Override
        protected void doWarn(String msg, Throwable e) {
        }
    }
}
