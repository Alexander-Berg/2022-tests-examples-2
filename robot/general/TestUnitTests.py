from devtools.fleur import ytest

@ytest.group
class UnitTest(ytest.UnitTestGroup):
    def __init__(self, context):
        super(UnitTest, self).__init__(context, '', 'yweb-robot-jupiter-tools-antispam-lib-ut')
