#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

import suggest_parser
from watchdog_helpers import get_url, assert_test_fail, form_url

import logging
import re
import sys, time
import json
import urllib
import urllib2


def check_template_text(test_name, answer, url, template, normalize_space=False, custom_answer = None):
    if isinstance(template, unicode): template = template.encode('UTF-8')

    random_marker = 'MIHVFENIAMGIRJZT'
    if normalize_space: template = ''.join(template.split())
    re_template = template
    re_template = re_template.replace('**', random_marker + '2')
    re_template = re_template.replace('*',  random_marker + '1')
    re_template = re.escape(re_template.decode('UTF-8')).encode('UTF-8')
    re_template = re_template.replace(random_marker + '2', '.*') #'**' matches everything
    re_template = re_template.replace(random_marker + '1', r'([^"]|\\.)*') #'*' matches only inside json string
    re_template = re_template.replace('CLICKSERVER', '((http(s)?:(\\\\)?/(\\\\)?/)yandex[.]ru(\\\\)?/clck(\\\\)?/jsredir|clck[.]yandex[.]ru)')
    re_template = re_template.replace('ODNOKLASSNIKI', '(www[.])?(odnoklassniki|ok)[.]ru')

    if normalize_space: answer = ''.join(answer.split())
    if not re.match('^' + re_template + '$', answer, re.DOTALL):
        if custom_answer is None:
            return assert_test_fail(test_name, url, template, answer)
        else:
            return assert_test_fail(test_name, url, template, custom_answer)

    return ''

#-----------------------------------------------------------------------
# function check_template:
#
# '**' means 'any characters'
# '*' means any characters without quote-" ( match only inside JSON-string )
#
# choose '*', if it is enough ( ** may match unexpected part of string, for example `X**Y**Z` will match `{"X",{Y:10}},foo="KAZA"`
#

def check_template(test_name, url, template, instance, normalize_space=False, user_agent = None, http_request_host = None, custom_answer = None, http_ip = None):
    assert url[0] == '/'
    answer = get_url(url, instance, user_agent = user_agent, http_request_host = http_request_host, http_ip = http_ip)
    return check_template_text(test_name, answer, url, template, normalize_space, custom_answer)

def check_template_with_uil_and_lr(queries, instance,
                                   uil_and_lrs=[['ru', 213]],
                                   test_name='empty suggest',
                                   handler_template='/suggest-ya.cgi?v=4&part={query}&lr={lr}&uil={uil}',
                                   response_template='["{query}",[],{{"r":{lr}}}]',
                                   normalize_space=False, user_agent=None, http_request_host=None,
                                   custom_answer=None, http_ip=None):
    # Use double {{ and }} if it is present in template
    ret_fail_msg = ''
    for query in queries:
        if isinstance(query, unicode): query = query.encode('UTF-8')
        if isinstance(response_template, unicode): response_template = response_template.encode('UTF-8')

        for uil, lr in uil_and_lrs:
            fail_msg = check_template(
                '%s for "%s"' % (query, test_name),
                handler_template.format(query=urllib.quote(query), lr=lr, uil=uil),
                response_template.format(query=query, lr=lr, uil=uil), instance)
            ret_fail_msg += fail_msg if ret_fail_msg == '' else '\n' + fail_msg
    return ret_fail_msg

def check_template_with_queries(queries, instance,
                                   test_name='empty suggest',
                                   handler_template='/suggest-ya.cgi?v=4&part={query}',
                                   response_template='**{query}**',
                                   normalize_space=False, user_agent=None, http_request_host=None,
                                   custom_answer=None, http_ip=None):
    # Use double {{ and }} if it is present in template
    ret_fail_msg = ''
    for item in queries:
        if isinstance(item, list):
            query = item[0]
            params = item[1] if len(item) > 1 else {}
        else:
            query = item
            params = {}

        if isinstance(query, unicode): query = query.encode('UTF-8')
        for elem in params:
            if isinstance(params[elem], unicode): params[elem] = params[elem].encode('UTF-8')

        fail_msg = check_template(
            '%s for "%s"' % (query, test_name),
            handler_template.format(query=urllib.quote(query), **params),
            response_template.format(query=query, **params), instance)
        ret_fail_msg += fail_msg if ret_fail_msg == '' else '\n' + fail_msg
    return ret_fail_msg

##############################################################################################
def check_nav_link_result_page(target, query_part, instance):
    assert isinstance(target, list)
    if isinstance(query_part, unicode): query_part = query_part.encode('UTF-8')

    url = '/suggest-ya.cgi?v=4&part=%s&lr=213' % urllib.quote_plus(query_part)
    def get_and_check():
        s = get_url(url, instance)
        try: parsed = json.loads(s)
        except: return "can't parse as JSON: '%s'" % repr(s)
        try: elem = parsed[1][0]
        except: return "can't find nav link in answer, (%s)" % repr(s)
        if elem[0] != "nav": return "first element is not a nav-link (%s %s)" % (repr(elem), repr(s))
        if len(elem) < 5: return "invalid nav-element, too short (%s %s)" % (repr(elem), repr(s))
        link = elem[4]
        if not re.match('^[a-z]+://', link):
            link = "http://" + link
        import urlparse, httplib
        try:
            url_parts = urlparse.urlsplit(link)
            conn = httplib.HTTPConnection(url_parts[1])
            get_query = urlparse.urlunsplit(('', '') + url_parts[2:])
            conn.request("GET", get_query)
            r1 = conn.getresponse()
        except:
            import traceback
            traceback.print_exc()
            return "can't open link '%s' from answer '%s'" % (repr(link), repr(s))


        def answer_check1():
            answer = r1.read()
            match = re.search(r'''<META http-equiv="refresh" content="0;URL='([^']*)'">''', answer)
            if not match:
                return """can't find <META http-equiv="refresh" content="0;URL='${URL_EXPECTED_HERE}'"> in answer = '%s'""" % repr(answer)
            if match.group(1) not in target:
                return "expected redirect to '%s' , got '%s', from link '%s'" % (repr(target), answer, repr(link))

        def answer_check2():
            if r1.status != 302:
                return "expected redirect status 302, got %s, from link '%s'" % (repr(r1.status), repr(link))
            if r1.getheader('Location') not in target:
                return "expected redirect to '%s' , got '%s', from link '%s'" % (repr(target), repr(r1.getheader('Location')), repr(link))

        err1 = answer_check1()
        err2 = answer_check2()
        if err1 and err2:
            return 'both redirections failed: 1) %s 2) %s' % (err1, err2)

    check_result = get_and_check()
    if check_result:
        return assert_test_fail(
            "nav-link for query '%s'" % (query_part),
            url,
            "redirection to '%s' in result page for query '%s'" % (target, query_part),
            check_result)
    return ''


def test_crossframe_ajax(instance):
    ret_fail_msg = ''
    for url in '/jquery-1-6-2.crossframeajax.html /jquery.crossframeajax.html /jquery-1-4-2.crossframeajax.html /jquery-1-4-4.crossframeajax.html'.split():
        fail_msg = check_template(url, url, '**text/javascript**', instance)
        ret_fail_msg += fail_msg if ret_fail_msg == '' else '\n' + fail_msg
    return ret_fail_msg

def test_default_experiment(instance):
    #check, that experiment 6 (with id 1471) is always enabled
    exprt6_match = 0
    for yandexuid_experiment in xrange(10000, 15000):
        answer = get_url('/suggest-ya.cgi?callback=xxx&v=4&lr=213&part=', instance, cookie='yandexuid=%s'%yandexuid_experiment)
        if '"exprt":"1471,' in answer:
            exprt6_match += 1
            break
    if not exprt6_match:
        return assert_test_fail('experiment 6 is always enabled', 'lot URLs with random "yandexuid" cookie', 'at least one answer with experiment 6 (... "exprt":"1471,... in JSON)', 'no experiments')
    return ''

# SUGGESTINC-23
def test_bad_yp_cookie(instance):
    yuid = '555'
    url = '/suggest-ya.cgi?v=4&uil=ru&part=вк&yu={0}'.format(yuid)
    answer = get_url(url, instance, cookie='yp=Sat Jul 08 2028 16:58:08 GMT 0500 (Пакистан, стандартное время).sp.nd:50:undefined; yandexuid={0}'.format(yuid))
    if not '"вконтакте"' in answer:
        return assert_test_fail("test_bad_yp_cookie", url, 'at least one suggestion with substring "вконтакте"', 'no "вконтакте" in response')
    return ''

def test_turkish_diacritic(instance):
    #normalize diacritics for Turkey:
    def explode_string(s):
        if s == '':
            yield ''
        else:
            variants, tail = re.match('^(\[.*?\]|.)(.*)$', s).groups()
            if variants[0] == '[':
                variants = variants[1:-1]
            for c in variants:
                for tail_exploded in explode_string(tail):
                    yield c + tail_exploded

    ret_fail_msg = ''
    for s in explode_string(u'sa[ğg]l[ıi]k+bakanl[ıi][ğg][ıi]'):
        url = '/suggest-ya.cgi?callback=x&v=3&&part=%s&sn=3&uil=tr&lr=11508' % s.encode('UTF-8')
        fail_msg = check_template("normalize diacritics for Turkey", url, '''x(["*",**"sağlık bakanlığı**''', instance)
        ret_fail_msg += fail_msg if ret_fail_msg == '' else '\n' + fail_msg
    return ret_fail_msg

def test_foreign_dictionary(instance):
    #check, that latin=1 and specfic region (lr=NNN) properly switch dictionaries
    url_petersburg  = '/suggest-ya.cgi?v=3&latin=0&callback=xxx&part=weather+in+&lr=2'
    answer_petersburg  = get_url(url_petersburg, instance)
    #weather in petersburg is not popular request for lr=2 -> change petersbutg to helsinki
    #if 'weather in petersburg' not in answer_petersburg and 'weather in st petersburg' not in answer_petersburg:
    #if 'weather in saint petersburg' not in answer_petersburg:
    #    return assert_test_fail('american latin=1 plus lr=NNN regionality', url_petersburg,  'weather in finland', answer_petersburg)
    return ''

def test_no_rus_char_in_foreign_contries(instance):
    ret_fail_msg = ''
    for switch_region in ['&uil=tr&lr=11508']:
        for char_code in xrange(ord('a'), ord('z')+1):
            char = chr(char_code)
            url = '/suggest-ya.cgi?v=3&callback=xxx&part=' + char + switch_region
            #note: test may broke if server start to escape russian symbols like \u1234
            page = get_url(url, instance)
            if re.search(u'[а-яА-Я]', page.decode('UTF-8')):
                fail_msg = assert_test_fail('no russian letters for ' + switch_region, url, 'no russian letters for ' + switch_region, page)
                ret_fail_msg += fail_msg if ret_fail_msg == '' else '\n' + fail_msg
    return ret_fail_msg

def check_ranking(test_name, url, before, after, instance):
    suggests = json.loads(get_url(url, instance))
    for suggest in suggests[1]:
        if suggest in before:
            return ''
        if suggest in after:
            expected = 'before: ' + json.dumps(before, ensure_ascii=False) + ' and after: ' + suggest
            got = 'before: ' + suggest + ' and after: ' + json.dumps(before, ensure_ascii=False)
            return assert_test_fail(test_name, url, expected, got)
    expected = 'anything from ' + json.dumps(before, ensure_ascii=False)
    got = json.dumps(suggests[1], ensure_ascii=False)
    return assert_test_fail(test_name, url, expected, got)

def check_duplicate_suggest(test_name, url, instance):
    suggests = json.loads(get_url(url, instance))
    if len(set(suggests[1])) != len(suggests[1]):
        return assert_test_fail(test_name, url, 'without duplicates', 'with duplicates')
    return ''

def test_request(test_name, url, data, instance, tvm_ticket=None):
    get_url(url, instance, data=data, headers={'X-Ya-Service-Ticket': tvm_ticket})
    return ''

# Tests with suggest_parser
def test_fulltext_suggest(test_name, instance, handler, params, query, expected):
    url = form_url(instance=instance, handler=handler, params=params, query=query)
    fulltext_suggest = suggest_parser.SuggestParserFactory().get_fulltext_suggest(url, handler)
    if expected not in fulltext_suggest:
        return assert_test_fail(test_name, url, expected, str(fulltext_suggest).decode('unicode_escape'))
    return ''

def test_nav_suggest(test_name, instance, handler, params, query, expected):
    url = form_url(instance=instance, handler=handler, params=params, query=query)
    nav_suggest = suggest_parser.SuggestParserFactory().get_nav_suggest(url, handler)
    if expected not in nav_suggest:
        return assert_test_fail(test_name, url, expected, str(nav_suggest).decode('unicode_escape'))
    return ''

def test_word_suggest(test_name, instance, handler, params, query, expected):
    url = form_url(instance=instance, handler=handler, params=params, query=query)
    word_suggest = suggest_parser.SuggestParserFactory().get_word_suggest(url, handler)
    if expected not in word_suggest:
        return assert_test_fail(test_name, url, expected, str(word_suggest).decode('unicode_escape'))
    return ''

def test_fact_suggest(test_name, instance, handler, params, query, expected):
    url = form_url(instance=instance, handler=handler, params=params, query=query)
    fact_suggest = suggest_parser.SuggestParserFactory().get_fact_suggest(url, handler)
    if expected not in fact_suggest:
        return assert_test_fail(test_name, url, expected, str(fact_suggest).decode('unicode_escape'))
    return ''

# берет по одному элементу из каждого списка и возвращает список таких комбинаций
def make_combinations(lists):
    if not lists:
        yield []
        return
    for item in lists[0]:
        for combination in make_combinations(lists[1:]):
            yield [item] + combination

def gen_cgi_flags(params):
    result = []
    for key, values in params.items():
        result.append(list(map(lambda v: "{0}={1}".format(key, v), values)))
    return result

def test_fulltext_suggest_with_params(test_name, instance, handlers, params, query, expected):
    for handler in handlers:
        cgi_flags = gen_cgi_flags(params)
        combinations = [item for item in make_combinations(cgi_flags)]
        for cgi_params in combinations:
            test_fulltext_suggest(test_name, instance, handler, cgi_params, query, expected)

def test_word_suggest_with_params(test_name, instance, handlers, params, query, expected):
    for handler in handlers:
        cgi_flags = gen_cgi_flags(params)
        combinations = [item for item in make_combinations(cgi_flags)]
        for cgi_params in combinations:
            test_word_suggest(test_name, instance, handler, cgi_params, query, expected)

def test_nav_suggest_with_params(test_name, instance, handlers, params, query, expected):
    for handler in handlers:
        cgi_flags = gen_cgi_flags(params)
        combinations = [item for item in make_combinations(cgi_flags)]
        for cgi_params in combinations:
            test_nav_suggest(test_name, instance, handler, cgi_params, query, expected)

def test_fact_suggest_with_params(test_name, instance, handlers, params, query, expected):
    for handler in handlers:
        cgi_flags = gen_cgi_flags(params)
        combinations = [item for item in make_combinations(cgi_flags)]
        for cgi_params in combinations:
            test_fact_suggest(test_name, instance, handler, cgi_params, query, expected)

def test_wizards_with_queries(test_name, instance, handlers, params, queries):
    for query in queries:
        for handler in handlers:
            cgi_flags = gen_cgi_flags(params)
            combinations = [item for item in make_combinations(cgi_flags)]
            for cgi_params in combinations:
                test_fact_suggest(test_name, instance, handler, cgi_params, query[0], query[1])

def test_clear_history(test_name, instance, handler, uuid):
    client_time = int(time.time())
    time_clear = client_time
    params = {'now': client_time, 'time': time_clear, 'uuid': uuid}
    cgi_params = urllib.urlencode(params)
    clear_history_url = instance + handler + cgi_params
    answer = get_url(clear_history_url)
    if answer != 'ok':
        return assert_test_fail(test_name, clear_history_url, 'history is cleared', 'history is not cleared: {}'.format(answer))
    # sleep for a while to make changes less predictable
    time.sleep(1)
    return ''

def test_export_history(test_name, instance, handler, uuid, queries):
    query_items = []
    for q in queries:
        current_time = int(time.time())
        if isinstance(q, unicode): q = q.encode('UTF-8')
        query_items.append({'text': q, 'time': current_time})
        # all queries will have different time attribute -> it is good
        time.sleep(1)
    post_data = json.dumps(query_items, ensure_ascii=False)
    current_time = int(time.time())
    params = {'now': current_time, 'srv': 'web', 'uuid': uuid}
    cgi_params = urllib.urlencode(params)
    export_history_url = instance + handler + cgi_params
    answer = get_url(export_history_url, data=post_data)
    obj = json.loads(answer)
    if 'not_saved' not in obj or len(obj['not_saved']) != 0:
        return assert_test_fail(test_name, export_history_url, 'history is saved', 'history is not saved: {}'.format(answer))
    return ''
