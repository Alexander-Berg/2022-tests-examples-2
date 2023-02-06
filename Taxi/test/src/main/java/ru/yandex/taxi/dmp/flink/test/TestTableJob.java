package ru.yandex.taxi.dmp.flink.test;

import org.apache.flink.table.api.DataTypes;
import org.apache.flink.table.api.Schema;
import org.apache.flink.table.api.TableDescriptor;
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.functions.ScalarFunction;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.taxi.dmp.flink.config.Environment;
import ru.yandex.taxi.dmp.flink.utils.FlinkUtils;

import static org.apache.flink.table.api.Expressions.$;
import static org.apache.flink.table.api.Expressions.call;

@SuppressWarnings("checkstyle:HideUtilityClassConstructor")
public class TestTableJob {
    private static final transient Logger log = LoggerFactory.getLogger(TestTableJob.class);

    private static TestArgs parsedArgs;

    public static void main(String[] args) throws Exception {
        parsedArgs = new TestArgs(Environment.fromString(args[0]));

        TableEnvironment env = FlinkUtils.tableEnvironment(parsedArgs);

        var sourceSchema = Schema.newBuilder()
                .column("name", DataTypes.STRING())
                .build();

        var sourceTable = env.from(
                logbrokerTable(parsedArgs.getTestInTopic())
                        .format("csv")
                        .schema(sourceSchema)
                        .build()
        );

        ScalarFunction func = new TestMapFunction();
        env.createTemporarySystemFunction("func", func);

        var result = sourceTable.map(call("func", $("name"))).as("a", "b");

        var targetDescriptor = logbrokerTable(parsedArgs.getTestOutTopic()).format("json").build();

        result.executeInsert(targetDescriptor);

        /*
        output is
        {"a":"pre-Vladimir","b":"Vladimir"}
        {"a":"pre-Alexander","b":"Alexander"}
        {"a":"pre-Natalya","b":"Natalya"}
        {"a":"pre-Oleg","b":"Oleg"}
        {"a":"pre-Konstantin","b":"Konstantin"}
        {"a":"pre-Valeriy","b":"Valeriy"}
        {"a":"pre-Alexandra","b":"Alexandra"}
        ...
         */
    }

    private static TableDescriptor.Builder logbrokerTable(String topic) {
        return TableDescriptor
                .forConnector("logbroker")
                .option("installation", "logbroker")
                .option("topic", topic)
                .option("consumer", parsedArgs.getLogbrokerConsumer())
                .option("credentials", "default-oauth");
    }
}
