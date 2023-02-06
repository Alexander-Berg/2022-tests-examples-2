package ru.yandex.metrika.lambda.steps;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.qameta.allure.Allure;
import io.qameta.allure.Step;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.Pair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import ru.yandex.devtools.test.CanonicalFile;
import ru.yandex.devtools.test.Canonizer;
import ru.yandex.devtools.test.Links;
import ru.yandex.devtools.test.Paths;
import ru.yandex.inside.yt.kosher.Yt;
import ru.yandex.inside.yt.kosher.cypress.CypressNodeType;
import ru.yandex.inside.yt.kosher.cypress.YPath;
import ru.yandex.inside.yt.kosher.impl.ytree.builder.YTree;
import ru.yandex.inside.yt.kosher.impl.ytree.builder.YTreeBuilder;
import ru.yandex.inside.yt.kosher.impl.ytree.serialization.YTreeTextSerializer;
import ru.yandex.inside.yt.kosher.impl.ytree.serialization.YsonTags;
import ru.yandex.inside.yt.kosher.tables.YTableEntryTypes;
import ru.yandex.inside.yt.kosher.ytree.YTreeListNode;
import ru.yandex.inside.yt.kosher.ytree.YTreeNode;
import ru.yandex.inside.yt.kosher.ytree.YTreeStringNode;

import static java.util.Collections.emptyList;
import static java.util.stream.Collectors.joining;
import static java.util.stream.Collectors.toList;
import static java.util.stream.Collectors.toMap;
import static ru.yandex.devtools.test.Paths.getTestOutputsRoot;
import static ru.yandex.metrika.lambda.steps.FreemarkerUtils.renderTemplate;
import static ru.yandex.metrika.lambda.steps.YtUtils.ensureMap;
import static ru.yandex.metrika.lambda.steps.YtUtils.ensureTable;

@Component
public class CypressCanonizer {

    private static final Logger log = LoggerFactory.getLogger(CypressCanonizer.class);

    @Autowired
    private YtFactory ytFactory;

    @Autowired
    @Qualifier("hahnJdbcTemplateV1")
    private JdbcTemplate yqlV1Template;

    private ImmutableList.Builder<TableBuilder> tables = ImmutableList.builder();

    public static class TableBuilder {
        private TableBuilder() {
        }

        private YPath root;
        private boolean isScanRoot = false;
        private boolean isRecursive = false;
        private List<String> groupColumns = emptyList();
        private List<String> excludedColumns = emptyList();
        private String excludedColumnsRegexp = "";

        public TableBuilder path(YPath path) {
            root = path;
            return this;
        }

        public TableBuilder scan() {
            isScanRoot = true;
            return this;
        }

        public TableBuilder recursive() {
            isRecursive = true;
            return this;
        }

        public TableBuilder groupColumns(List<String> columns) {
            groupColumns = columns;
            return this;
        }

        public TableBuilder excludedColumns(List<String> columns) {
            excludedColumns = columns;
            return this;
        }

        public TableBuilder excludedColumnsRegexp(String regexp) {
            excludedColumnsRegexp = regexp;
            return this;
        }

        private List<TableInfo> build(Yt yt) {
            List<TableInfo> tables = new ArrayList<>();

            processPath(yt, root, isScanRoot, isRecursive, tables);

            return tables;
        }

        private void processPath(Yt yt, YPath path, boolean isScanRoot, boolean isRecursive, List<TableInfo> state) {
            log.debug("Process path: '{}'", path.toString());
            if (isScanRoot) {
                ensureMap(yt, path);
                for (YTreeStringNode node : yt.cypress().list(path)) {
                    YPath child = path.child(node.getValue());
                    String rawType = yt.cypress().get(child.attribute("type")).stringValue();
                    CypressNodeType nodeType = CypressNodeType.R.fromName(rawType);
                    if (nodeType.equals(CypressNodeType.TABLE)) {
                        state.add(processSingleTable(yt, child));
                    }
                    if (nodeType.equals(CypressNodeType.MAP) && isRecursive) {
                        processPath(yt, child, true, true, state);
                    }
                }
            } else {
                ensureTable(yt, path);
                state.add(processSingleTable(yt, path));
            }
        }

        private TableInfo processSingleTable(Yt yt, YPath tablePath) {
            log.debug("Process table: '{}'", tablePath.toString());
            if (yt.cypress().exists(tablePath)) {
                ensureTable(yt, tablePath);

                List<String> columns = new ArrayList<>();

                if (yt.cypress().exists(tablePath.attribute("schema"))) {
                    Pattern excludedColumnsPattern = Pattern.compile(excludedColumnsRegexp);

                    columns.addAll(yt.cypress().get(tablePath.attribute("schema")).asList().stream()
                            .map(n -> n.mapNode().getString("name"))
                            .filter(c -> !excludedColumns.contains(c))
                            .filter(c -> !excludedColumnsPattern.matcher(c).matches())
                            .collect(toList()));
                } else {
                    throw new RuntimeException(String.format("No attribute 'schema' for '%s'", tablePath.toString()));
                }
                return new TableInfo(tablePath, columns, groupColumns);
            } else {
                throw new RuntimeException(String.format("Path '%s' doesn't exist", tablePath.toString()));
            }
        }
    }

    private void addLinkToTabCrunchReportRoot() {
        Links.set("Tab Crunch Reports root", Path.of(getTestOutputsRoot(), "tab-crunch").toString());
    }

    private CanonicalFile canonizeFile(Yt yt, TableInfo tableInfo) {
        log.debug("Canonize file: '{}'", tableInfo.getTable().toString());

        Path canonicalFilePath = Path.of(getTestOutputsRoot(), "cypress", StringUtils.stripStart(tableInfo.getTable().toString(), "/"));
        Path tabCrunchReportFilePath = Path.of(getTestOutputsRoot(), "tab-crunch", StringUtils.stripStart(tableInfo.getTable().toString(), "/") + ".html");

        return new CanonicalFile(writeYtTableToFile(yt, tableInfo, canonicalFilePath), false, getCustomDiffTool(tableInfo, tabCrunchReportFilePath));
    }

    private String[] getCustomDiffTool(TableInfo tableInfo, Path tabCrunchReportFilePath) {
        return new String[]{
                getJavaPath(),
                "-jar",
                Paths.getBuildPath("metrika/qa/tab-crunch/tab-crunch-diff-tool.jar"),
                "--columns", tableInfo.getColumns().stream().collect(joining(" ")),
                "--group-columns", tableInfo.getGroupColumns().stream().collect(joining(" ")),
                "--output", tabCrunchReportFilePath.toString()
        };
    }

    private static String getJavaPath() {
        Path jdkDir = Path.of(System.getProperty("java.home"));

        Optional<Path> javaPath = tryFindJavaPath(jdkDir);

        return javaPath.get().toString();
    }

    private static Optional<Path> tryFindJavaPath(Path jdkDir) {
        Path[] candidates = new Path[] {
                jdkDir.resolve(Path.of("bin", "java")),
                jdkDir.resolve(Path.of("bin", "java.exe"))
        };

        return Stream.of(candidates)
                .filter(c -> c.toFile().exists())
                .findFirst();
    }

    private String writeYtTableToFile(Yt yt, TableInfo tableInfo, Path destination) {
        if (!Files.exists(destination.getParent())) {
            try {
                Files.createDirectories(destination.getParent());
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }

        try (BufferedWriter fileWriter = Files.newBufferedWriter(destination)) {
            RowMapperColumnsWriter writer = new RowMapperColumnsWriter(fileWriter);
            yt.tables().read(tableInfo.getTable(), YTableEntryTypes.YSON, writer);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        return destination.toString();
    }

    private CanonicalFile canonizeMetaFile(Yt yt, TableInfo tableInfo) {
        log.debug("Canonize meta file: '{}'", tableInfo.getTable().toString());

        Path canonicalFilePath = Path.of(getTestOutputsRoot(), "cypress", StringUtils.stripStart(tableInfo.getTable().toString(), "/") + ".meta");

        return new CanonicalFile(writeYtTableMetaToDiffFriendlyFile(yt, tableInfo, canonicalFilePath));
    }

    private Pair<CanonicalFile, CanonicalFile> canonizeFileWithMeta(Yt yt, TableInfo tableInfo) {
        log.debug("Canonize file with meta: '{}'", tableInfo.getTable().toString());
        return Pair.of(
                canonizeFile(yt, tableInfo),
                canonizeMetaFile(yt, tableInfo));
    }

    private String writeYtTableMetaToFile(Yt yt, TableInfo tableInfo, Path tableDestination) {
        Path destination = Path.of(tableDestination.toString() + ".meta");
        try (BufferedWriter fileWriter = Files.newBufferedWriter(destination)) {
            Map<String, YTreeNode> attrs = yt.cypress().get(tableInfo.getTable().allAttributes()).asMap();

            YTreeNode metaNode = YTree.builder().beginMap()
                    .key("type").value("table")
                    .key("format").value("yson")
                    .key("attributes").value(getMetaAttrs(attrs))
                    .endMap()
                    .build();
            fileWriter.write(YTreeTextSerializer.serialize(metaNode));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        return destination.toString();
    }

    private String writeYtTableMetaToDiffFriendlyFile(Yt yt, TableInfo tableInfo, Path tableDestination) {
        Path destination = Path.of(tableDestination.toString());
        try (BufferedWriter fileWriter = Files.newBufferedWriter(destination)) {
            Map<String, YTreeNode> attrs = yt.cypress().get(tableInfo.getTable().allAttributes()).asMap();
            if (attrs.containsKey("schema_mode") && attrs.get("schema_mode").stringValue().equals("strong")) {
                YTreeListNode schema = attrs.get("schema").listNode();
                for(YTreeNode schemaItem : schema) {
                    fileWriter.write(YTreeTextSerializer.serialize(schemaItem));
                    fileWriter.write(YsonTags.ITEM_SEPARATOR);
                    fileWriter.write("\n");
                }
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        return destination.toString();
    }

    private YTreeNode getMetaAttrs(Map<String, YTreeNode> attrs) {
        YTreeBuilder builder = YTree.builder().beginMap();

        if (attrs.containsKey("user_attribute_keys")) {
            for (YTreeNode k : attrs.get("user_attribute_keys").asList().stream()
                    .filter(k -> !k.stringValue().equals("_yql_op_id"))
                    .collect(Collectors.toList())) {
                builder.key(k.stringValue()).value(attrs.get(k.stringValue()));
            }
        }

        if (attrs.containsKey("schema_mode") && attrs.get("schema_mode").stringValue().equals("strong")) {
            builder.key("schema").value(attrs.get("schema"));
        }

        return builder.endMap().build();
    }

    private TableBuilder add(YPath path) {
        TableBuilder tableBuilder = new TableBuilder();
        tables.add(tableBuilder);
        tableBuilder.path(path);
        return tableBuilder;
    }

    public TableBuilder path(YPath path) {
        return add(path);
    }

    public void canonize() {
        addLinkToTabCrunchReportRoot();
        Canonizer.canonize(tables.build().stream()
                .flatMap(tableBuilder -> tableBuilder.build(ytFactory.getYt()).stream())
                .collect(toMap(tableInfo -> tableInfo.getTable().toString(), tableInfo -> canonizeFile(ytFactory.getYt(), tableInfo))));
    }

    public void canonizeWithMeta() {
        addLinkToTabCrunchReportRoot();
        Canonizer.canonize(tables.build().stream()
                .flatMap(tableBuilder -> tableBuilder.build(ytFactory.getYt()).stream())
                .flatMap(tableInfo -> {
                    Pair<CanonicalFile, CanonicalFile> filePair = canonizeFileWithMeta(ytFactory.getYt(), tableInfo);
                    return Stream.of(
                            Pair.of(tableInfo.getTableConstant().toString() + ".data", filePair.getLeft()),
                            Pair.of(tableInfo.getTableConstant().toString() + ".meta", filePair.getRight()));
                })
                .collect(toMap(pair -> pair.getKey(), pair -> pair.getValue()))
        );
    }

    public void dumpState() {
        /*
        Отладочный дамп состояния yt - //home и //logs в виде, пригодном к загрузке в кластер для
        дальнейшего анализа и отладки.
         */
        log.info("Dumping state");
        dumpState("home");
        dumpState("logs");
    }

    private void dumpState(String path) {
        TableBuilder tableBuilder = new TableBuilder().path(YPath.cypressRoot().child(path));
        tableBuilder.scan().recursive();

        for (TableInfo tableInfo : tableBuilder.build(ytFactory.getYt())) {
            Path destinationFilePath = Path.of(getTestOutputsRoot(), "cypress-state", StringUtils.stripStart(tableInfo.getTable().toString(), "/"));
            writeYtTableToFile(ytFactory.getYt(), tableInfo, destinationFilePath);
            writeYtTableMetaToFile(ytFactory.getYt(), tableInfo, destinationFilePath);
        }
    }

    @Step("Постпроцессинг {sourceRoot} -> {destinationTable}")
    public void postprocess(YPath sourceRoot, YPath destinationTable, List<String> groupColumns) {
        try (LogMonitor logMonitor = new LogMonitor("Консольный лог")) {
            final List<TableInfo> tables = new TableBuilder().path(sourceRoot).scan().recursive().build(ytFactory.getYt());

            String query = renderTemplate("steps/postprocess.yql.ftl", ImmutableMap.<String, Object>builder()
                    .put("sourceTables", tables.stream().map(t -> t.getTable().toString()).collect(toList()))
                    .put("destinationTable", destinationTable)
                    .put("groupColumns", groupColumns)
                    .build());

            Allure.addAttachment("postprocess", "text/plain", query, ".yql");

            yqlV1Template.execute(query);
        }
    }
}
