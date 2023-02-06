#include <robot/favicon/tests/protos/tables.pb.h>
#include <mapreduce/yt/interface/operation.h>
#include <mapreduce/yt/interface/client.h>
#include <mapreduce/yt/interface/protos/yamr.pb.h>

#include <util/string/cast.h>

namespace NFaviconTest {
    class TFooToBar final: public NYT::IMapper<
                                NYT::TTableReader<TFoo>, NYT::TTableWriter<TBar>> {
    public:
        void Do(TReader* reader, TWriter* writer) override {
            for (; reader->IsValid(); reader->Next()) {
                TFoo const& foo = reader->GetRow();

                Bar.SetBytes(foo.GetString());
                Bar.SetInt(foo.GetUint() * (foo.GetBool() ? 1 : -1));
                Bar.SetDouble(foo.GetEnum());
                auto m = Bar.MutableBoxes()->AddBox();
                m->MutableFoo()->CopyFrom(foo);
                m->SetTable(reader->GetTableIndex());

                if (Bar.GetBytes() != foo.GetString()) {
                    writer->AddRow(Bar);
                    Bar.Clear();
                }
            }

            if (Bar.SerializeAsString() != TBar().SerializeAsString()) {
                writer->AddRow(Bar);
            }
        }

        TBar Bar;
    };

    REGISTER_MAPPER(TFooToBar);

    class TCountWords: public NYT::IReducer<
                            NYT::TTableReader<TBar>, NYT::TTableWriter<TBar>> {
    public:
        void Do(TReader* reader, TWriter* writer) override {
            for (; reader->IsValid(); reader->Next()) {
                const TBar& row = reader->GetRow();
                if (Bar.GetBytes() == row.GetBytes()) {
                    Bar.SetInt(Bar.GetInt() + row.GetInt());
                } else {
                    Flush(writer);
                    Bar.SetBytes(row.GetBytes());
                    Bar.SetInt(row.GetInt());
                }
            }
            Flush(writer);
        }

        void Flush(TWriter* writer) {
            if (Bar.GetInt() > 0) {
                writer->AddRow(Bar);
            }
            Bar.Clear();
        }

        TBar Bar;
    };
    REGISTER_REDUCER(TCountWords);

    class TBarToYamr: public NYT::IReducer<
                           NYT::TTableReader<TBar>, NYT::TTableWriter<NProtoBuf::Message>> {
    public:
        void Do(TReader* reader, TWriter* writer) override {
            for (; reader->IsValid(); reader->Next()) {
                const TBar& row = reader->GetRow();
                NYT::TYamr yamr;
                yamr.SetKey(row.GetBytes());
                yamr.SetValue(ToString(row.GetInt()));
                writer->AddRow<NYT::TYamr>(yamr, 0);
                TMetaInfo meta;
                meta.SetTableIndex(reader->GetTableIndex());
                meta.SetRowIndex(reader->GetRowIndex());
                writer->AddRow<TMetaInfo>(meta, 1);
            }
        }
    };
    REGISTER_REDUCER(TBarToYamr);

}

int main(int argc, const char* argv[]) {
    NYT::Initialize(argc, argv);
    return EXIT_FAILURE;
}
