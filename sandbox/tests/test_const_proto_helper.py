import pytest
import yatest.common
from io import StringIO, BytesIO
from textwrap import dedent

from sandbox.projects.yabs.SysConstLifetime.const_proto.const_proto_helper import (
    ConstProtoHelper, EConstProtoMode, ConstantNotFoundError, ConstantAlreadyExistsError,
    InvalidOwner, InvalidConstProtoMode
)

TEST_OWNERS_LOCAL_PATH = yatest.common.test_source_path('test_owners.json')


@pytest.fixture
def const_proto_helper():
    yield ConstProtoHelper(
        None,
        None,
        'BSSERVER-228',
        'yabs/proto/quality/sys_const.proto',
        TEST_OWNERS_LOCAL_PATH,
        'yabs/server/test/qabs_bsserver_pytest/data/db_null_snapshot.py'
    )


CONST_NAME = 'TestConstant'
CONST_VALUE = 228
CONST_TYPE = 'FEATURE_FLAG'
TEST_USER = 'TestUser'


@pytest.fixture
def const_proto_file():
    file_obj = StringIO(dedent(u"""\
        import "yabs/server/proto/quality/const_options.proto";

        package NFP;

        message TSysConst {{
            optional int64 AbAvgPriceCoeff = 1 [default = 0, (type) = FEATURE_FLAG];
            optional int64 {const_name} = 2 [default = 25, (type) = CONSTANT_VALUE];
            optional int64 SubstringTestConstant = 3 [default = 228, (type) = FEATURE_FLAG];
        }} // LAST: 3
    """.format(const_name=CONST_NAME)))
    yield file_obj


def test_helper_init(const_proto_helper):
    helper = const_proto_helper
    assert helper._ticket == 'BSSERVER-228'
    assert helper._proto_local_path == 'yabs/proto/quality/sys_const.proto'
    assert helper._owners_local_path == TEST_OWNERS_LOCAL_PATH
    assert helper._db_null_path == 'yabs/server/test/qabs_bsserver_pytest/data/db_null_snapshot.py'


def test_get_const_id_options_simple(const_proto_helper, const_proto_file):
    const_id, options = const_proto_helper._get_const_id_options(const_proto_file, CONST_NAME)
    assert const_id == 2
    assert options == {u'default': u'25', u'(type)': u'CONSTANT_VALUE'}


def test_get_const_id_options_error(const_proto_helper):
    file_obj = StringIO(dedent(u"""\
        import "yabs/server/proto/quality/const_options.proto";

        package NFP;

        message TSysConst {
            optional int64 AbAvgPriceCoeff = 1 [default = 0, (type) = FEATURE_FLAG];
            optional int64 SomeConstantHere = 2 [default = 25, (type) = CONSTANT_VALUE];
        }
    """))
    with pytest.raises(ConstantNotFoundError):
        const_proto_helper._get_const_id_options(file_obj, CONST_NAME)
    assert file_obj.tell() == 0


def test_write_with_new_const_update_existing(const_proto_helper, const_proto_file):
    out_file = StringIO()
    const_proto_helper._write_with_new_const(const_proto_file, out_file, CONST_NAME, '2', {u'default': unicode(CONST_VALUE), u'(type)': unicode(CONST_TYPE)})
    out_file.seek(0)
    assert const_proto_file.tell() == 0
    assert out_file.read() == dedent(u"""\
        import "yabs/server/proto/quality/const_options.proto";

        package NFP;

        message TSysConst {{
            optional int64 AbAvgPriceCoeff = 1 [default = 0, (type) = FEATURE_FLAG];
            optional int64 {const_name} = 2 [default = {const_value}, (type) = {const_type}];
            optional int64 SubstringTestConstant = 3 [default = 228, (type) = FEATURE_FLAG];
        }} // LAST: 3
    """.format(const_name=CONST_NAME, const_value=CONST_VALUE, const_type=CONST_TYPE))


def test_write_with_new_const_add_new_const(const_proto_helper, const_proto_file):
    out_file = StringIO()
    const_proto_helper._write_with_new_const(const_proto_file, out_file, 'SomeNewConst', '4', {u'default': unicode(CONST_VALUE), u'(type)': unicode(CONST_TYPE)})
    out_file.seek(0)
    assert const_proto_file.tell() == 0
    assert out_file.read() == dedent(u"""\
        import "yabs/server/proto/quality/const_options.proto";

        package NFP;

        message TSysConst {{
            optional int64 AbAvgPriceCoeff = 1 [default = 0, (type) = FEATURE_FLAG];
            optional int64 {const_name} = 2 [default = 25, (type) = CONSTANT_VALUE];
            optional int64 SubstringTestConstant = 3 [default = 228, (type) = FEATURE_FLAG];
            optional int64 SomeNewConst = 4 [default = {const_value}, (type) = {const_type}];
        }} // LAST: 4
    """.format(const_name=CONST_NAME, const_value=CONST_VALUE, const_type=CONST_TYPE))


def test_update_default_in_file(const_proto_helper, const_proto_file):
    out_file = StringIO()
    const_proto_helper._update_default_in_file(const_proto_file, out_file, CONST_NAME, CONST_VALUE, CONST_TYPE)
    out_file.seek(0)
    assert const_proto_file.tell() == 0
    assert out_file.read() == dedent(u"""\
        import "yabs/server/proto/quality/const_options.proto";

        package NFP;

        message TSysConst {{
            optional int64 AbAvgPriceCoeff = 1 [default = 0, (type) = FEATURE_FLAG];
            optional int64 {const_name} = 2 [default = {const_value}, (type) = {const_type}];
            optional int64 SubstringTestConstant = 3 [default = 228, (type) = FEATURE_FLAG];
        }} // LAST: 3
    """.format(const_name=CONST_NAME, const_value=CONST_VALUE, const_type=CONST_TYPE))


def test_get_last_const_id(const_proto_helper, const_proto_file):
    const_id = const_proto_helper._get_last_const_id(const_proto_file)
    assert const_proto_file.tell() == 0
    assert const_id == 3


def test_check_const_does_not_exist(const_proto_helper, const_proto_file):
    const_proto_helper._check_const_does_not_exist(const_proto_file, 'SomeNewConst')
    assert const_proto_file.tell() == 0
    with pytest.raises(ConstantAlreadyExistsError):
        const_proto_helper._check_const_does_not_exist(const_proto_file, CONST_NAME)
    assert const_proto_file.tell() == 0


def test_add_const_to_file(const_proto_helper, const_proto_file):
    new_const_name = 'SomeNewConst'
    new_const_value = '123'
    new_const_type = 'CONSTANT_VALUE'

    out_file = StringIO()
    const_proto_helper._add_const_to_file(const_proto_file, out_file, new_const_name, new_const_value, new_const_type)
    out_file.seek(0)
    assert const_proto_file.tell() == 0
    assert out_file.read() == dedent(u"""\
        import "yabs/server/proto/quality/const_options.proto";

        package NFP;

        message TSysConst {{
            optional int64 AbAvgPriceCoeff = 1 [default = 0, (type) = FEATURE_FLAG];
            optional int64 {const_name} = 2 [default = 25, (type) = CONSTANT_VALUE];
            optional int64 SubstringTestConstant = 3 [default = 228, (type) = FEATURE_FLAG];
            optional int64 {new_const_name} = 4 [default = {new_const_value}, (type) = {new_const_type}];
        }} // LAST: 4
    """.format(
        const_name=CONST_NAME,
        new_const_name=new_const_name,
        new_const_value=new_const_value,
        new_const_type=new_const_type
    ))


def test_set_const_owner(const_proto_helper):
    in_file = BytesIO(dedent("""\
        {
            "owners": {}
        }
        """))
    out_file = BytesIO()
    const_proto_helper._set_const_owner(in_file, out_file, CONST_NAME, TEST_USER)
    assert in_file.tell() == 0
    out_file.seek(0)
    assert out_file.read() == dedent("""\
        {
            "owners": {
                "TestConstant": "TestUser"
            }
        }
        """)


def test_get_current_constant_owner_with_unknown_mode(const_proto_helper):
    with pytest.raises(InvalidConstProtoMode):
        const_proto_helper.get_current_constant_owner(CONST_NAME, EConstProtoMode.UNKNOWN)


def test_get_current_constant_owner_with_add_mode(const_proto_helper):
    with pytest.raises(InvalidOwner):
        const_proto_helper.get_current_constant_owner(CONST_NAME, EConstProtoMode.ADD)


def test_get_current_owner_of_not_existing_constant(const_proto_helper):
    with pytest.raises(InvalidOwner):
        const_proto_helper.get_current_constant_owner('NotExistingConstant', EConstProtoMode.UPDATE)


def test_get_current_constant_owner(const_proto_helper):
    owner = const_proto_helper.get_current_constant_owner(CONST_NAME, EConstProtoMode.UPDATE)
    assert owner == TEST_USER


def test_update_db_null__new_constant(const_proto_helper):
    initial_db_null = '''
base.MkdbConstant(_from_snapshot=True, Name='mkdb-rtb-min-cpm', Value=1000, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SetCostLeftCutAtIntermediateCost', Value=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='CheckBroadmatchLimitAtIntermediateCost', Value=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SendBidReqIdInRtbAuctionInfo', Value=1, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SharedRtbDspCacheTtlMs', Value=0, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
'''

    expected_db_null = '''
base.MkdbConstant(_from_snapshot=True, Name='mkdb-rtb-min-cpm', Value=1000, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='NewConst', Value=1, Description='new constant')
base.RuntimeConstant(_from_snapshot=True, Name='SetCostLeftCutAtIntermediateCost', Value=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='CheckBroadmatchLimitAtIntermediateCost', Value=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SendBidReqIdInRtbAuctionInfo', Value=1, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SharedRtbDspCacheTtlMs', Value=0, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
'''

    actual_db_null, replace_count = const_proto_helper._set_const_in_db_null(
        initial_db_null,
        'NewConst',
        1,
        'new constant',
        True
    )

    assert replace_count == 0
    assert expected_db_null == actual_db_null


def test_update_db_null__update_one_constant(const_proto_helper):
    initial_db_null = '''
base.MkdbConstant(_from_snapshot=True, Name='mkdb-rtb-min-cpm', Value=1000, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SetCostLeftCutAtIntermediateCost', Value=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='CheckBroadmatchLimitAtIntermediateCost', Value=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SendBidReqIdInRtbAuctionInfo', Value=1, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SharedRtbDspCacheTtlMs', Value=0, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
'''

    expected_db_null = '''
base.MkdbConstant(_from_snapshot=True, Name='mkdb-rtb-min-cpm', Value=1000, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SetCostLeftCutAtIntermediateCost', Value=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='CheckBroadmatchLimitAtIntermediateCost', Value=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SendBidReqIdInRtbAuctionInfo', Value=0, Description='updated constant')
base.RuntimeConstant(_from_snapshot=True, Name='SharedRtbDspCacheTtlMs', Value=0, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
'''

    actual_db_null, replace_count = const_proto_helper._set_const_in_db_null(
        initial_db_null,
        'SendBidReqIdInRtbAuctionInfo',
        0,
        'updated constant',
        True
    )

    assert replace_count == 1
    assert expected_db_null == actual_db_null


def test_update_db_null__update_more_constant(const_proto_helper):
    initial_db_null = '''
base.MkdbConstant(_from_snapshot=True, Name='mkdb-rtb-min-cpm', Value=1000, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SetCostLeftCutAtIntermediateCost', Value=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='CheckBroadmatchLimitAtIntermediateCost', Value=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SendBidReqIdInRtbAuctionInfo', Value=1, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SendBidReqIdInRtbAuctionInfo', Value=0, Description='updated constant')
base.RuntimeConstant(_from_snapshot=True, Name='SharedRtbDspCacheTtlMs', Value=0, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SendBidReqIdInRtbAuctionInfo', Value=1, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SharedRtbDspCacheTtlMs', Value=0, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SendBidReqIdInRtbAuctionInfo', Value=1, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SharedRtbDspCacheTtlMs', Value=0, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SendBidReqIdInRtbAuctionInfo', Value=1, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SendBidReqIdInRtbAuctionInfo', Value=1, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SharedRtbDspCacheTtlMs', Value=0, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SendBidReqIdInRtbAuctionInfo', Value=1, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
'''

    expected_db_null = '''
base.MkdbConstant(_from_snapshot=True, Name='mkdb-rtb-min-cpm', Value=1000, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SetCostLeftCutAtIntermediateCost', Value=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='CheckBroadmatchLimitAtIntermediateCost', Value=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SendBidReqIdInRtbAuctionInfo', Value=0, Description='updated constant')
base.RuntimeConstant(_from_snapshot=True, Name='SharedRtbDspCacheTtlMs', Value=0, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SharedRtbDspCacheTtlMs', Value=0, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SharedRtbDspCacheTtlMs', Value=0, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SharedRtbDspCacheTtlMs', Value=0, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
'''

    actual_db_null, replace_count = const_proto_helper._set_const_in_db_null(
        initial_db_null,
        'SendBidReqIdInRtbAuctionInfo',
        0,
        'updated constant',
        True
    )

    assert replace_count == 7
    assert expected_db_null == actual_db_null


def test_update_db_null__update_commented_constant(const_proto_helper):
    initial_db_null = '''
base.MkdbConstant(_from_snapshot=True, Name='mkdb-rtb-min-cpm', Value=1000, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='NewConst', Value=1, Description='new constant')
base.RuntimeConstant(_from_snapshot=True, Name='SetCostLeftCutAtIntermediateCost', Value=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='CheckBroadmatchLimitAtIntermediateCost', Value=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='NewConst', Value=0, Description='new constant')
# base.RuntimeConstant(_from_snapshot=True, Name='NewConst', Value=1, Description='new constant', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SendBidReqIdInRtbAuctionInfo', Value=1, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
# base.RuntimeConstant(_from_snapshot=True, Name='NewConst', Value=1, Description='new constant', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
# base.RuntimeConstant(_from_snapshot=True, Name='NewConst', Value=1, Description='new constant', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SharedRtbDspCacheTtlMs', Value=0, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
'''

    expected_db_null = '''
base.MkdbConstant(_from_snapshot=True, Name='mkdb-rtb-min-cpm', Value=1000, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='NewConst', Value=0, Description='new constant')
base.RuntimeConstant(_from_snapshot=True, Name='SetCostLeftCutAtIntermediateCost', Value=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='CheckBroadmatchLimitAtIntermediateCost', Value=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
# base.RuntimeConstant(_from_snapshot=True, Name='NewConst', Value=1, Description='new constant', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SendBidReqIdInRtbAuctionInfo', Value=1, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
# base.RuntimeConstant(_from_snapshot=True, Name='NewConst', Value=1, Description='new constant', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
# base.RuntimeConstant(_from_snapshot=True, Name='NewConst', Value=1, Description='new constant', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
base.RuntimeConstant(_from_snapshot=True, Name='SharedRtbDspCacheTtlMs', Value=0, ContentSystemKey=0, Description='', UpdateTime=datetime.datetime(2009, 6, 10, 18, 3, 41))
'''

    actual_db_null, replace_count = const_proto_helper._set_const_in_db_null(
        initial_db_null,
        'NewConst',
        0,
        'new constant',
        True
    )

    assert replace_count == 2
    assert expected_db_null == actual_db_null
