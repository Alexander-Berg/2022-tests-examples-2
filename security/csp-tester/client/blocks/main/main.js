modules.define('main', ['i-bem-dom', 'BEMHTML', 'jquery', 'form', 'result', 'textarea', 'button', 'info-modal'],
    function(provide, bemDom, BEMHTML, $, Form, Result, Textarea, Button, InfoModal) {

var API_URL = '/api/v1/analyze';

provide(bemDom.declBlock(this.name, {
    onSetMod: {
        js: {
            inited: function() {
                this._result = this.findChildBlock(Result);
                this._textarea = this.findChildBlock(Textarea);
                this._submit = this.findChildBlock({ block: Button, modName: 'type', modVal: 'submit' });

                this._editor = CodeMirror.fromTextArea(this._textarea.domElem[0], {
                    mode: 'csp',
                    lineWrapping: true
                });

                this._editor.on('change', this._onChange.bind(this));
            }
        }
    },
    _onChange: function(codemirror, e) {
        var val = codemirror.getValue();
        this._submit.setMod('disabled', !val);
    },
    _onSubmit: function(e) {
        e.preventDefault();

        var _this = this,
            form = e.bemTarget,
            resultBlock = this._result;

        $.post(API_URL, form.serialize(), 'json').then(function(data) {
            if (data.error) {
                return InfoModal.show(BEMHTML.apply((data.error)));
            }

            if (data.policy) {
                _this._editor.setValue(data.pretty);
            }

            var hasIssues = !!data.issues.length,
                hasErrors = !!data.errors.length;

            if (hasIssues || hasErrors) {
                bemDom.update(resultBlock._elem('content').domElem, BEMHTML.apply(hasErrors ?
                    [
                        {
                            block: 'heading',
                            mods: { level: 1 },
                            content: 'Некорректная либо отсутствующая политика'
                        },
                        data.errors.map(function(err) {
                            return { content: err };
                        })
                    ] : [
                        {
                            block: 'heading',
                            mods: { level: 1 },
                            content: 'Обнаруженные ошибки CSP-политики'
                        },
                        data.protects || {
                            block: 'issues',
                            elem: 'no-protection',
                            content: [
                                'Анализируемая CSP-политика не защищает от XSS. ',
                                'Обратите внимание на критичные (выделены красным) ошибки в директивах ',
                                {
                                    tag: 'strong',
                                    content: 'default-src'
                                }, ',  ',
                                {
                                    tag: 'strong',
                                    content: 'script-src'
                                }, ' и  ',
                                {
                                    tag: 'strong',
                                    content: 'object-src'
                                }, '.'
                            ]
                        },
                        {
                            block: 'issues',
                            content: data.issues.map(function(issue) {
                                return {
                                    elem: 'issue',
                                    elemMods: { severity: issue.severity && issue.severity.label },
                                    content: issue.desc
                                };
                            })
                        },
                        hasIssues && {
                            block: 'cut',
                            switcher: 'Получить wiki-код для вставки',
                            content: {
                                block: 'textarea',
                                mods: { theme: 'islands', size: 'm', width: 'available' },
                                attrs: { readonly: true },
                                val: [
                                    '== CSP ==',
                                    '%%(csp)',
                                    data.pretty,
                                    '%%',
                                    '=== Обнаружены ошибки ===',
                                     data.protects ?
                                        '' :
                                        ('Анализируемая CSP-политика не защищает от XSS. ' +
                                        'Обратите внимание на критичные (выделены красным) ошибки в директивах %%default-src%%, %%script-src%% и %%object-src%%.\n'),
                                    data.issues.map(function(issue) {
                                        var color = {
                                            High: 'red',
                                            Low: 'grey'
                                        }[issue.severity.label];

                                        return '* ' + (color ? '!!(' + color + ')' : '') + issue.desc + (color ? '!!' : '');
                                    }).join('\n'),
                                    '----',
                                    'Отчёт подготовлен с помощью ((https://csp-tester.yandex-team.ru/ CSP Tester)) на основе ((https://wiki.yandex-team.ru/product-security/csp/ рекомендаций по составлению политики CSP)).'
                                ].join('\n')
                            }
                        }
                    ]
                ));
            }

            resultBlock.setMod('status', hasIssues || hasErrors ? 'invalid' : 'valid').setMod('visible');
            _this._emit('change', { hasIssues: hasIssues || hasErrors });
        }).fail(function(err) {
            InfoModal.show('Request failed, try again');
            console.log(err);
        });
    }
}, {
    lazyInit: false,
    onInit: function() {
        this._events(Form).on('submit', this.prototype._onSubmit);
    }
}));

});
