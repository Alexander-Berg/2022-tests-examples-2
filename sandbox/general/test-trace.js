
var children = {

        status : 500,
        body: 'Traceback (most recent call last):\n' +
                '  File "/home/zomb-sandbox/web/server/request.py", line 340, in _process\n' +
                '    return self.reply(m(req))\n' +
                '  File "/home/zomb-sandbox/web/controller.py", line 761, in view_task\n' +
                '    template_dir = projects.TYPES[task.type].package\n' +
                'KeyError: u\'ANTIROBOT_LEARN\'\n\n' +
                'Server: sandbox-server01.search.yandex.net',

        processor : function(urlParts, reqBody, mockedData, status){

            return {
                status : status,
                body   : mockedData
            };
        }
    };

module.exports = children;
