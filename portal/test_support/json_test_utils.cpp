#include "json_test_utils.h"

#include <library/cpp/json/json_reader.h>
#include <library/cpp/json/writer/json_value.h>
#include <library/cpp/json/writer/json.h>

#include <util/system/yassert.h>

#include <util/generic/algorithm.h>
#include <util/generic/maybe.h>
#include <util/generic/vector.h>
#include <util/generic/hash_set.h>
#include <util/string/builder.h>
#include <util/string/split.h>

namespace NMordaBlocks {
    namespace NTest {

        namespace {
            using NJson::TJsonValue;

            constexpr int IdentSpaces = 4;

            bool IsComplexType(const TJsonValue& value) {
                return value.GetType() == NJson::JSON_ARRAY || value.GetType() == NJson::JSON_MAP;
            }

            void PrintValue(const TJsonValue& oldValue, IOutputStream& diffOutput) {
                if (oldValue.GetType() == NJson::JSON_STRING) {
                    diffOutput << oldValue.GetString();
                } else {
                    diffOutput << oldValue;
                }
            }

            void PrintIdent(int ident, IOutputStream& diffOutput) {
                for (int i = 0; i < ident * IdentSpaces; ++i) {
                    diffOutput.Write(' ');
                }
            }

            TString ComputeKey(const TJsonValue& value) {
                NJsonWriter::TBuf buf(NJsonWriter::HEM_DONT_ESCAPE_HTML);
                buf.WriteJsonValue(&value);
                return buf.Str();
            }

            void PrintLongStringsDiff(const TString& oldValue, const TString& newValue, int ident, IOutputStream& diffOutput) {
                size_t diffStartAt = 0;
                while (diffStartAt < oldValue.size() && diffStartAt < newValue.size() && oldValue[diffStartAt] == newValue[diffStartAt]) {
                    ++diffStartAt;
                }
                PrintIdent(ident, diffOutput);
                diffOutput << "common prefix:\n";
                PrintIdent(ident, diffOutput);
                if (diffStartAt == 0) {
                    diffOutput << "(empty)";
                } else {
                    diffOutput << oldValue.substr(0, diffStartAt);
                }
                diffOutput << "\n\n";

                PrintIdent(ident, diffOutput);
                diffOutput << "old suffix:\n";
                PrintIdent(ident, diffOutput);
                diffOutput << oldValue.substr(diffStartAt);
                diffOutput << "\n\n";

                PrintIdent(ident, diffOutput);
                diffOutput << "new suffix:\n";
                PrintIdent(ident, diffOutput);
                diffOutput << newValue.substr(diffStartAt);
                diffOutput << "\n";
            }

            void PrintJsonWithIdent(const TJsonValue& value, int ident, IOutputStream& diffOutput) {
                NJsonWriter::TBuf buf(NJsonWriter::HEM_DONT_ESCAPE_HTML);
                buf.SetIndentSpaces(IdentSpaces);
                buf.WriteJsonValue(&value);
                TVector<TString> lines;
                StringSplitter(buf.Str()).Split('\n').AddTo(&lines);
                for (const TString& line : lines) {
                    PrintIdent(ident, diffOutput);
                    diffOutput << line << "\n";
                }
            }

            void PrintDiff(const TJsonValue& oldValue, const TJsonValue& newValue, int ident, bool nested, IOutputStream& diffOutput) {
                if (oldValue.GetType() == NJson::JSON_STRING && newValue.GetType() == NJson::JSON_STRING) {
                    const TString& oldValueString = oldValue.GetString();
                    const TString& newValueString = newValue.GetString();
                    if (oldValueString.size() > 50 || newValueString.size() > 50) {
                        if (nested) {
                            diffOutput << "\n";
                        }
                        PrintLongStringsDiff(oldValueString, newValueString, nested ? ident + 1 : ident, diffOutput);
                        return;
                    }
                }
                if (nested) {
                    diffOutput << ": ";
                }
                PrintValue(oldValue, diffOutput);
                diffOutput << " -> ";
                PrintValue(newValue, diffOutput);
                diffOutput << "\n";
            }

            void CompareJsonValues(const TJsonValue& oldValue, const TJsonValue& newValue,
                                   int ident, IOutputStream& diffOutput) {
                if (oldValue == newValue) {
                    return;
                }
                if (oldValue.GetType() == NJson::JSON_MAP) {
                    //todo node type changed
                    Y_VERIFY(newValue.GetType() == NJson::JSON_MAP, "unexpected node type [%d]", newValue.GetType());

                    const auto& oldValueMap = oldValue.GetMap();
                    const auto& newValueMap = newValue.GetMap();
                    for (const auto& p : oldValueMap) {
                        auto it = newValueMap.find(p.first);
                        if (it == newValueMap.end()) {
                            PrintIdent(ident, diffOutput);
                            diffOutput << "-" << p.first << ": " << p.second << "\n";
                        } else if (p.second != it->second) {
                            PrintIdent(ident, diffOutput);
                            diffOutput << p.first;
                            if (!IsComplexType(p.second) && !IsComplexType(it->second)) {
                                PrintDiff(p.second, it->second, ident, true, diffOutput);
                            } else {
                                diffOutput << "\n";
                                CompareJsonValues(p.second, it->second, ident + 1, diffOutput);
                            }
                        }
                    }
                    for (const auto& p : newValueMap) {
                        auto it = oldValueMap.find(p.first);
                        if (it == oldValueMap.end()) {
                            PrintIdent(ident, diffOutput);
                            diffOutput << "+" << p.first << ": " << p.second << "\n";
                        }
                    }
                } else if (oldValue.GetType() == NJson::JSON_ARRAY) {
                    //todo node type changed
                    Y_VERIFY(newValue.GetType() == NJson::JSON_ARRAY, "unexpected node type [%d]", newValue.GetType());

                    const auto& oldValueArray = oldValue.GetArray();
                    const auto& newValueArray = newValue.GetArray();
                    PrintIdent(ident, diffOutput);
                    diffOutput << "length: " << oldValueArray.size();
                    if (newValueArray.size() != oldValueArray.size()) {
                        diffOutput << " -> " << newValueArray.size();
                    }
                    diffOutput << "\n";
                    THashMap<TString, TVector<const TJsonValue*>> newValueIndex;
                    THashSet<const TJsonValue*> matchedNewValues;
                    TVector<const TJsonValue*> notMatchedNewValues;
                    TVector<const TJsonValue*> notMatchedOldValues;
                    for (const auto& x : newValueArray) {
                        newValueIndex[ComputeKey(x)].push_back(&x);
                    }
                    for (auto& x : newValueIndex) {
                        Reverse(x.second.begin(), x.second.end());
                    }
                    for (const auto& x : oldValueArray) {
                        TString key = ComputeKey(x);
                        auto it = newValueIndex.find(key);
                        if (it != newValueIndex.end() && !it->second.empty()) {
                            Y_VERIFY(matchedNewValues.emplace(it->second.back()).second);
                            it->second.pop_back();
                            continue;
                        }
                        notMatchedOldValues.push_back(&x);
                    }
                    for (const auto& x : newValueArray) {
                        auto it = matchedNewValues.find(&x);
                        if (it != matchedNewValues.end()) {
                            continue;
                        }
                        notMatchedNewValues.push_back(&x);
                    }
                    if (notMatchedOldValues.size() == 1 && notMatchedNewValues.size() == 1) {
                        CompareJsonValues(*notMatchedOldValues[0], *notMatchedNewValues[0], ident + 1, diffOutput);
                    } else {
                        for (const auto& x : notMatchedOldValues) {
                            PrintIdent(ident, diffOutput);
                            diffOutput << "-\n";
                            PrintJsonWithIdent(*x, ident + 1, diffOutput);
                        }
                        for (const auto& x : notMatchedNewValues) {
                            PrintIdent(ident, diffOutput);
                            diffOutput << "+\n";
                            PrintJsonWithIdent(*x, ident + 1, diffOutput);
                        }
                    }

                } else if (oldValue != newValue) {
                    PrintDiff(oldValue, newValue, ident, false, diffOutput);
                }
            }

        } // namespace

        NJson::TJsonValue ReadJsonFromString(TStringBuf jsonString) {
            NJson::TJsonValue result;
            NJson::ReadJsonTree(jsonString, &result, true);
            return result;
        }

        TString ConvertToString(const NJson::TJsonValue& json) {
            NJsonWriter::TBuf sout;
            sout.WriteJsonValue(&json, true);
            return sout.Str();
        }

        bool JsonsEqual(const NJson::TJsonValue& lhs, const NJson::TJsonValue& rhs) {
            return ConvertToString(lhs) == ConvertToString(rhs);
        }

        bool JsonsEqual(TStringBuf jsonRaw, const NJson::TJsonValue& rhs) {
            return JsonsEqual(ReadJsonFromString(jsonRaw), rhs);
        }

        TString JsonStringDiff(const NJson::TJsonValue& first, const NJson::TJsonValue& second) {
            TStringBuilder result;
            CompareJsonValues(first, second, 1, result.Out);
            return result;
        }

        TString JsonStringDiff(TStringBuf jsonRawFirst, const NJson::TJsonValue& second) {
            return JsonStringDiff(ReadJsonFromString(jsonRawFirst), second);
        }

    } // namespace NTest

} // namespace NMordaBlocks
