#include <robot/jupiter/library/opt/common/common.h>
#include <robot/jupiter/library/opt/mropt.h>
#include <robot/jupiter/library/opt/common/params.h>
#include <robot/jupiter/protos/jupiter_doc.pb.h>

#include <robot/library/yt/static/command.h>
#include <robot/library/yt/static/tags.h>
#include <robot/mercury/library/tables/jupiter_doc.h>
#include <robot/mercury/library/tables/tables.h>

#include <google/protobuf/util/json_util.h>
#include <mapreduce/yt/client/client.h>
#include <mapreduce/yt/common/config.h>

#include <library/cpp/getopt/last_getopt.h>
#include <library/cpp/getopt/small/modchooser.h>
#include <library/cpp/json/writer/json.h>
#include <library/cpp/protobuf/protofile/protofile.h>

namespace NJupiter {
    namespace {

    class TJupiterDocDataReader {
        NYT::TTableReaderPtr<TJupiterDocData> TableReader;
        TMaybe<TJupiterDocData> CurrentRow;

        using TKey = std::pair<TString, TString>;
    public:
        TJupiterDocDataReader(NYT::IClientPtr client, TString path):
            TableReader(client->CreateTableReader<TJupiterDocData>(path))
        {
            Next();
        }
        bool IsValid() const {
            return CurrentRow.Defined() || TableReader->IsValid();
        }
        void Next() {
            CurrentRow.Clear();
            TMaybe<TKey> lastKey;
            NMercury::NPrivate::TJupiterDocDynamicTable::TRowCollector collector;
            for (; TableReader->IsValid(); TableReader->Next()) {
                const TJupiterDocData& row = TableReader->GetRow();

                TKey key = GetKey(row);
                if (lastKey.Defined() && lastKey.GetRef() != key) {
                    break;
                }
                lastKey = std::move(key);

                collector.AddRow(row);
            }
            TMaybe<NJupiter::TJupiterDocData> docData = collector.MakeResult();
            if (docData.Empty()) {
                return;
            }
            CurrentRow = std::move(docData.GetRef());
        }
        const TJupiterDocData& GetRow() const {
            if (!CurrentRow.Defined()) {
                ythrow yexception() << "attempt to read row from reader after it was exhausted";
            }
            return CurrentRow.GetRef();
        }
    private:
        TKey GetKey(const TJupiterDocData& row) const {
            return {row.GetHost(), row.GetPath()};
        }
    };

    template<class TProto>
    NJson::TJsonValue MessageToJsonValue(const TProto& message) {
        TString jsonString;
        google::protobuf::util::MessageToJsonString(message, &jsonString);
        NJson::TJsonValue jsonValue;
        Y_ENSURE(NJson::ReadJsonTree(jsonString, &jsonValue, true));
        return jsonValue;
    }

    template<class TProto>
    void CopyColumnContentAsJsonValue(const TJupiterDataColumn& column, const TString& name, NJson::TJsonValue* out) {
        if (!column.HasData()) {
            return;
        }
        TProto message;
        Y_ENSURE(message.ParseFromString(column.GetData()));
        out->InsertValue(name, MessageToJsonValue(message));
    }

    void AddIndent(int indent, IOutputStream* out) {
        while (indent-- > 0) {
            (*out) << ' ';
        }
    }

    void PrettyPrintJsonTree(const NJson::TJsonValue& tree, int indent, IOutputStream* out) {
        if (!tree.IsDefined() || tree.IsBoolean() || tree.IsDouble() || tree.IsInteger() || tree.IsUInteger()) {
            (*out) << ::ToString(tree);
            return;
        }
        if (tree.IsString()) {
            /* configure serialization to avoid escaped slashes (\/) */
            NJsonWriter::TBuf buf(NJsonWriter::HEM_RELAXED, out);
            buf.WriteJsonValue(&tree);
            return;
        }
        int nextIndent = indent + 2;
        if (tree.IsMap()) {
            TVector<TString> keys;
            for (const auto& [key, value] : tree.GetMap()) {
                Y_UNUSED(value);
                keys.push_back(key);
            }
            Sort(keys.begin(), keys.end());
            (*out) << '{' << '\n';
            bool first = true;
            for (const TString& key : keys) {
                if (first) {
                    first = false;
                } else {
                    (*out) << ',' << '\n';
                }
                AddIndent(nextIndent, out);
                (*out) << '"' << key << '"' << ':' << ' ';
                PrettyPrintJsonTree(tree[key], nextIndent, out);
            }
            (*out) << '\n';
            AddIndent(indent, out);
            (*out) << '}';
            return;
        }
        if (tree.IsArray()) {
            const NJson::TJsonValue::TArray& array = tree.GetArray();
            (*out) << '[' << '\n';
            bool first = true;
            for (auto it = array.begin(); it != array.end(); ++it) {
                if (first) {
                    first = false;
                } else {
                    (*out) << ',' << '\n';
                }
                AddIndent(nextIndent, out);
                PrettyPrintJsonTree(*it, nextIndent, out);
            }
            (*out) << '\n';
            AddIndent(indent, out);
            (*out) << ']';
            return;
        }
        ythrow yexception() << "JsonValue of unexpected type occurred in PrettyPrintJsonTree: " << ::ToString(tree);
    }

    NJson::TJsonValue MixedMessageToJsonValue(const TJupiterDocData& docData) {
        NJson::TJsonValue jsonValue;
        jsonValue.InsertValue("Host", docData.GetHost());
        jsonValue.InsertValue("Path", docData.GetPath());
        jsonValue.InsertValue("SplitIndex", docData.GetSplitIndex());
        // This field depends on time and should not be dumped in the tests
        // jsonValue.InsertValue("LastUpdated", docData.GetLastUpdated());
        jsonValue.InsertValue("IsRemoved", docData.GetIsRemoved());
        jsonValue.InsertValue("LastAccess", docData.GetLastAccess());
        NJson::TJsonValue dataValue;
        TJupiterDocDataColumns columns;
        Y_ENSURE(columns.ParseFromString(docData.GetData()));
        if (columns.Hasurldat()) {
            CopyColumnContentAsJsonValue<TUrldat>(columns.Geturldat(), "urldat", &dataValue);
        }
        /* Feel free to add more fields from Data into serialization. Only a small subset is added presently. */
        jsonValue.InsertValue("Data", dataValue);
        return jsonValue;
    }

    struct TDumpParams {
        TString SrcPath;
        TString FilePath;

        void Add(TCmdParams *params) {
            params->AddRequired("src-path", "", "<YT table path>", &SrcPath);
            params->AddRequired("file-path", "", "<file path>", &FilePath);
        }
    };
    
    } /* end of namespace */

    int DumpJupiterDocData(int argc, const char** argv) {
        TCmdParams params;

        TMrOpts mrOpts;
        TMrOptsParser(params, mrOpts)
            .AddServerName()
            .AddDebugMode();

        TDumpParams dumpParams;
        dumpParams.Add(&params);

        params.Parse(argc, argv);

        const NYT::IClientPtr& client = NYT::CreateClient(mrOpts.ServerName);
        TFileOutput output(dumpParams.FilePath);
        auto reader = MakeHolder<TJupiterDocDataReader>(client, dumpParams.SrcPath);
        for (; reader->IsValid(); reader->Next()) {
            const TJupiterDocData& row = reader->GetRow();
            const NJson::TJsonValue jsonValue = MixedMessageToJsonValue(row);
            PrettyPrintJsonTree(jsonValue, 0, &output);
            output << Endl;
        }
        output.Finish();
        return 0;
    }
}

int main(int argc, const char** argv) {
    NYT::Initialize(argc, argv);

    TModChooser modeChooser;
    modeChooser.SetSeparatedMode(true);
    modeChooser.SetVersionHandler(PrintProgramSvnVersion);

    modeChooser.AddMode("DumpJupiterDocData", &NJupiter::DumpJupiterDocData, "Download, serialize, and save to a file a JupiterDocData table");

    try {
        return modeChooser.Run(argc, argv);
    } catch(...) {
        Cerr << CurrentExceptionMessage();
        return 1;
    }
}

