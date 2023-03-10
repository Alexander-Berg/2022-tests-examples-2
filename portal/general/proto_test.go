package eventlog

import (

	"io/ioutil"
	"os"
	"reflect"
	"sync"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"google.golang.org/protobuf/reflect/protoreflect"
	"google.golang.org/protobuf/runtime/protoimpl"
	"google.golang.org/protobuf/proto"
	
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
)


func Test_proto(t *testing.T) {
	key := &TEntity{
		String_: "key",
		Int64: 0,
	}
	data := &TEntity{
		String_: "data",
		Int64: 1,
	}

	tmpFile, err := ioutil.TempFile("", "")
	require.NoError(t, err)
	require.NoError(t, tmpFile.Close())
	defer os.Remove(tmpFile.Name())
	fileOption := WithFile(tmpFile.Name())

	{
		logger, err := NewProtoLogger(&TEntity{}, &TEntity{}, fileOption.AsSink())
		require.NoError(t, err)
		frame := logger.NewFrame(key)
		frame.AddData(data)
		require.NoError(t, frame.Log())
		require.NoError(t, logger.Release())
	}

	{
		reader, err := NewProtoReader(&TEntity{}, &TEntity{}, fileOption.AsSource())
		require.NoError(t, err)
		frames, err := reader.DumpAll(NewReadOptions()).AllUntil(common.NewMapper(func(frame ReadFrame[Timestamped[*TEntity], Timestamped[*TEntity]]) bool {
			return frame == nil
		}))
		require.NoError(t, err)
		require.Len(t, frames, 1)
		frame := frames[0]
		assert.True(t, proto.Equal(frame.GetKey().Get(), key))
		assert.Len(t, frame.GetData(), 1)
		assert.True(t, proto.Equal(frame.GetData()[0].Get(), data))
		require.NoError(t, reader.Release())
	}
}




// Code generated by protoc-gen-go. DO NOT EDIT.
// versions:
// 	protoc-gen-go v1.26.0
// 	protoc        v3.18.1

const (
	// Verify that this generated code is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(20 - protoimpl.MinVersion)
	// Verify that runtime/protoimpl is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(protoimpl.MaxVersion - 20)
)

type TEntity struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	String_ string `protobuf:"bytes,1,opt,name=String,proto3" json:"String,omitempty"`
	Int64   int64  `protobuf:"varint,2,opt,name=Int64,proto3" json:"Int64,omitempty"`
}

func (x *TEntity) Reset() {
	*x = TEntity{}
	if protoimpl.UnsafeEnabled {
		mi := &file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_msgTypes[0]
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		ms.StoreMessageInfo(mi)
	}
}

func (x *TEntity) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*TEntity) ProtoMessage() {}

func (x *TEntity) ProtoReflect() protoreflect.Message {
	mi := &file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_msgTypes[0]
	if protoimpl.UnsafeEnabled && x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use TEntity.ProtoReflect.Descriptor instead.
func (*TEntity) Descriptor() ([]byte, []int) {
	return file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_rawDescGZIP(), []int{0}
}

func (x *TEntity) GetString_() string {
	if x != nil {
		return x.String_
	}
	return ""
}

func (x *TEntity) GetInt64() int64 {
	if x != nil {
		return x.Int64
	}
	return 0
}

var File_portal_avocado_libs_utils_eventlog_proto_test_entity_proto protoreflect.FileDescriptor

var file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_rawDesc = []byte{
	0x0a, 0x3a, 0x70, 0x6f, 0x72, 0x74, 0x61, 0x6c, 0x2f, 0x61, 0x76, 0x6f, 0x63, 0x61, 0x64, 0x6f,
	0x2f, 0x6c, 0x69, 0x62, 0x73, 0x2f, 0x75, 0x74, 0x69, 0x6c, 0x73, 0x2f, 0x65, 0x76, 0x65, 0x6e,
	0x74, 0x6c, 0x6f, 0x67, 0x2f, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x2f, 0x74, 0x65, 0x73, 0x74, 0x5f,
	0x65, 0x6e, 0x74, 0x69, 0x74, 0x79, 0x2e, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x12, 0x05, 0x70, 0x72,
	0x6f, 0x74, 0x6f, 0x22, 0x37, 0x0a, 0x07, 0x54, 0x45, 0x6e, 0x74, 0x69, 0x74, 0x79, 0x12, 0x16,
	0x0a, 0x06, 0x53, 0x74, 0x72, 0x69, 0x6e, 0x67, 0x18, 0x01, 0x20, 0x01, 0x28, 0x09, 0x52, 0x06,
	0x53, 0x74, 0x72, 0x69, 0x6e, 0x67, 0x12, 0x14, 0x0a, 0x05, 0x49, 0x6e, 0x74, 0x36, 0x34, 0x18,
	0x02, 0x20, 0x01, 0x28, 0x03, 0x52, 0x05, 0x49, 0x6e, 0x74, 0x36, 0x34, 0x42, 0x3b, 0x5a, 0x39,
	0x61, 0x2e, 0x79, 0x61, 0x6e, 0x64, 0x65, 0x78, 0x2d, 0x74, 0x65, 0x61, 0x6d, 0x2e, 0x72, 0x75,
	0x2f, 0x70, 0x6f, 0x72, 0x74, 0x61, 0x6c, 0x2f, 0x61, 0x76, 0x6f, 0x63, 0x61, 0x64, 0x6f, 0x2f,
	0x6c, 0x69, 0x62, 0x73, 0x2f, 0x75, 0x74, 0x69, 0x6c, 0x73, 0x2f, 0x65, 0x76, 0x65, 0x6e, 0x74,
	0x6c, 0x6f, 0x67, 0x2f, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x62, 0x06, 0x70, 0x72, 0x6f, 0x74, 0x6f,
	0x33,
}

var (
	file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_rawDescOnce sync.Once
	file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_rawDescData = file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_rawDesc
)

func file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_rawDescGZIP() []byte {
	file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_rawDescOnce.Do(func() {
		file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_rawDescData = protoimpl.X.CompressGZIP(file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_rawDescData)
	})
	return file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_rawDescData
}

var file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_msgTypes = make([]protoimpl.MessageInfo, 1)
var file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_goTypes = []interface{}{
	(*TEntity)(nil), // 0: proto.TEntity
}
var file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_depIdxs = []int32{
	0, // [0:0] is the sub-list for method output_type
	0, // [0:0] is the sub-list for method input_type
	0, // [0:0] is the sub-list for extension type_name
	0, // [0:0] is the sub-list for extension extendee
	0, // [0:0] is the sub-list for field type_name
}

func init() { file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_init() }
func file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_init() {
	if File_portal_avocado_libs_utils_eventlog_proto_test_entity_proto != nil {
		return
	}
	if !protoimpl.UnsafeEnabled {
		file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_msgTypes[0].Exporter = func(v interface{}, i int) interface{} {
			switch v := v.(*TEntity); i {
			case 0:
				return &v.state
			case 1:
				return &v.sizeCache
			case 2:
				return &v.unknownFields
			default:
				return nil
			}
		}
	}
	type x struct{}
	out := protoimpl.TypeBuilder{
		File: protoimpl.DescBuilder{
			GoPackagePath: reflect.TypeOf(x{}).PkgPath(),
			RawDescriptor: file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_rawDesc,
			NumEnums:      0,
			NumMessages:   1,
			NumExtensions: 0,
			NumServices:   0,
		},
		GoTypes:           file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_goTypes,
		DependencyIndexes: file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_depIdxs,
		MessageInfos:      file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_msgTypes,
	}.Build()
	File_portal_avocado_libs_utils_eventlog_proto_test_entity_proto = out.File
	file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_rawDesc = nil
	file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_goTypes = nil
	file_portal_avocado_libs_utils_eventlog_proto_test_entity_proto_depIdxs = nil
}
