# coding=utf-8
__author__ = 'alexsingle'

import sys
from io import StringIO
import pandas as pd


from metr_utils import generate_query
from metr_utils.databases import clickhouse as ch, yql_db, yt_db

import yt.wrapper as yt

yt.config.set_proxy('hahn.yt.yandex.net')

yql_query = """
--Coverage report (@alexsingle)

pragma yt.DefaultMemoryLimit = '8G';
$parse_date = DateTime::Parse("%Y-%m-%d");

$is_domain = Re2::Match("^([a-zа-яё0-9]([a-zа-яё0-9\\\-_]{{0,61}}[a-zа-яё0-9])?\\\.)+(xn\\\-\\\-[a-z0-9\\\-]{{2,}}|[a-zа-яё]{{2,}})$");

$d3_exclusion = ('at.tut.by','blogs.mail.ru','blogs.privet.ru','blogspot.co.at','blogspot.co.il','blogspot.co.ke','blogspot.co.nz','blogspot.co.uk','blogspot.com.ar','blogspot.com.au','blogspot.com.br','blogspot.com.by','blogspot.com.co','blogspot.com.cy','blogspot.com.eg','blogspot.com.es','blogspot.com.mt','blogspot.com.ng','blogspot.com.tr','blogspot.com.uy','h.com.ua','ho.com.ua','lj.rossia.org','mywebpage.netscape.com','pp.net.ua','web.ur.ru','afisha.yandex.ru','fotki.yandex.ru','maps.yandex.ru','market.yandex.ru','money.yandex.ru','news.yandex.ru','rabota.yandex.ru','rasp.yandex.ru','realty.yandex.ru','slovari.yandex.ru','store.yandex.ru','taxi.yandex.ru','toloka.yandex.ru','travel.yandex.ru','tv.yandex.ru','video.yandex.ru','ws.co.ua','cdn.ampproject.org');

$d2_exclusion = ('0catch.com','0pk.ru','16mb.com','1bb.ru','1gb.ru','2bb.ru','3bb.ru','3dn.ru','4bb.ru','4u.ru','50megs.com','50webs.com','5bb.ru','6bb.ru','70mb.ru','96.lt','abkhazia.su','ac.at','ac.be','ac.id','ac.il','ac.jp','ac.ru','ac.th','ac.uk','adygeya.ru','adygeya.su','aecru.org','afaik.ru','agava.ru','aha.ru','aiq.ru','aktyubinsk.su','al.ru','alfamoon.com','alfaspace.net','alltrades.ru','altai.ru','am9.ru','amur.ru','amursk.ru','an.md','appspot.com','arkhangelsk.ru','arkhangelsk.su','armenia.su','ashgabad.su','astrakhan.ru','at.ua','av.tr','az.ru','azerbaijan.su','baikal.ru','balashov.su','bashkiria.ru','bashkiria.su','bbs.tr','be.md','bel.tr','belgorod.ru','belgorod.su','beon.ru','besaba.com','best-host.ru','bip.ru','bir.ru','biz.tr','biz.ua','bl.md','blog.ru','blogonline.ru','blogsome.com','blogspot.be','blogspot.ca','blogspot.ch','blogspot.com','blogspot.cz','blogspot.de','blogspot.dk','blogspot.fi','blogspot.fr','blogspot.gr','blogspot.hu','blogspot.ie','blogspot.in','blogspot.it','blogspot.jp','blogspot.mx','blogspot.nl','blogspot.no','blogspot.pt','blogspot.ro','blogspot.ru','blogspot.se','blogspot.sg','blogspot.tw','boom.ru','borda.ru','bos.ru','br.md','brest.by','bryansk.ru','bryansk.su','bs.md','bukhara.su','buryatia.ru','by.com','by.ru','byethost8.com','cbg.ru','cc.md','cc.ua','cg.md','ch.md','chat.ru','chel.ru','chelyabinsk.ru','chernovtsy.ua','chimkent.su','chita.ru','chukotka.ru','chuvashia.ru','ck.ua','cl.md','clan.su','cm.md','cmw.ru','cn.md','cn.ua','co.id','co.il','co.in','co.jp','co.kr','co.md','co.nz','co.th','co.ua','co.uk','co.za','com.af','com.al','com.ar','com.au','com.bd','com.bh','com.bn','com.bo','com.br','com.by','com.bz','com.cn','com.co','com.com','com.cy','com.de','com.do','com.ec','com.ee','com.eg','com.es','com.et','com.ge','com.gh','com.gr','com.gt','com.hk','com.hr','com.jm','com.kh','com.kw','com.kz','com.lb','com.ly','com.md','com.mk','com.mm','com.mt','com.mx','com.my','com.na','com.ng','com.ni','com.np','com.om','com.pa','com.pe','com.pg','com.ph','com.pk','com.pl','com.pr','com.pt','com.py','com.qa','com.ro','com.ru','com.sa','com.sg','com.sv','com.tn','com.tr','com.tw','com.ua','com.uy','com.vc','com.ve','com.vn','cr.md','crimea.ua','cs.md','ct.md','cu.md','cv.ua','cwx.ru','da.ru','dagestan.ru','dagestan.su','dax.ru','db.md','dem.ru','diary.ru','dn.md','dn.ua','do.am','donetsk.ua','dp.ua','dr.md','dtn.ru','dudinka.ru','e-burg.ru','e-stile.ru','east-kazakhstan.su','ed.md','edu.au','edu.ru','edu.tr','edu.ua','esy.es','eu.int','exnet.su','fanforum.ru','far.ru','fareast.ru','fastbb.ru','fatal.ru','fl.md','flybb.ru','fo.ru','forever.kz','forum24.ru','forumbb.ru','fr.md','freewebpage.org','fromru.com','fromru.su','front.ru','fsbo.ru','fud.ru','fvds.ru','ge.md','gen.tr','geocities.com','georgia.su','gl.md','go.id','go.ru','gob.ar','gob.gt','gob.mx','gob.pa','gob.pe','gob.sv','gob.ve','gomel.by','gov.ac','gov.ae','gov.af','gov.ag','gov.ai','gov.al','gov.an','gov.ao','gov.ar','gov.au','gov.aw','gov.az','gov.ba','gov.bb','gov.bd','gov.bf','gov.bh','gov.bi','gov.bm','gov.bn','gov.bo','gov.br','gov.bs','gov.bt','gov.bw','gov.by','gov.bz','gov.cd','gov.ch','gov.ci','gov.ck','gov.cl','gov.cm','gov.cn','gov.co','gov.com','gov.cu','gov.cv','gov.cx','gov.cy','gov.cz','gov.de','gov.dj','gov.dk','gov.dm','gov.do','gov.dz','gov.ec','gov.ee','gov.eg','gov.er','gov.et','gov.fj','gov.fk','gov.fo','gov.gd','gov.gg','gov.gh','gov.gi','gov.gm','gov.gn','gov.gr','gov.gs','gov.gu','gov.gw','gov.gy','gov.hk','gov.hn','gov.ht','gov.hu','gov.ie','gov.il','gov.im','gov.in','gov.iq','gov.ir','gov.it','gov.je','gov.jm','gov.jo','gov.kh','gov.ki','gov.kn','gov.kr','gov.kw','gov.ky','gov.la','gov.lb','gov.lc','gov.lk','gov.lr','gov.ls','gov.lt','gov.lv','gov.ly','gov.ma','gov.me','gov.mg','gov.mk','gov.ml','gov.mm','gov.mn','gov.mo','gov.mp','gov.mr','gov.ms','gov.mt','gov.mu','gov.mv','gov.mw','gov.my','gov.mz','gov.na','gov.net','gov.nf','gov.ng','gov.np','gov.nr','gov.nu','gov.om','gov.org','gov.pf','gov.pg','gov.ph','gov.pk','gov.pl','gov.pn','gov.pr','gov.ps','gov.pt','gov.py','gov.qa','gov.ro','gov.rs','gov.ru','gov.rw','gov.sa','gov.sb','gov.sc','gov.sd','gov.se','gov.sg','gov.sh','gov.si','gov.sk','gov.sl','gov.sr','gov.st','gov.sy','gov.sz','gov.tc','gov.tk','gov.tl','gov.tm','gov.tn','gov.to','gov.tp','gov.tr','gov.tt','gov.tw','gov.ua','gov.uk','gov.vc','gov.ve','gov.vg','gov.vi','gov.vn','gov.vu','gov.ws','gov.ye','gov.yu','gov.za','gov.zm','gov.zw','gr.md','grodno.by','grozny.ru','grozny.su','h1.ru','h10.ru','h11.ru','h12.ru','h14.ru','h15.ru','h16.ru','h17.ru','h18.ru','habrahabr.ru','hn.md','ho.ua','hobi.ru','hoha.ru','hol.es','holm.ru','hop.ru','hostia.ru','hotbox.ru','hoter.ru','hotmail.ru','hut.ru','hut1.ru','hut2.ru','i-nets.ru','iatp.by','id.ru','if.ua','in.ua','inc.ru','inf.ua','infacms.com','info.md','info.tr','infobox.ru','int.ru','io.ua','irk.ru','irkutsk.ru','ivano-frankivsk.ua','ivanovo.ru','ivanovo.su','izhevsk.ru','jamal.ru','jamango.ru','jambyl.su','jar.ru','jimdo.com','jino-net.ru','jino.ru','joshkar-ola.ru','joy.by','k-uralsk.ru','k12.tr','kalmykia.ru','kalmykia.su','kaluga.ru','kaluga.su','kamchatka.ru','karacol.su','karaganda.su','karelia.ru','karelia.su','kazan.ru','kazan.ws','kchr.ru','kemerovo.ru','kh.ua','khabarovsk.ru','khakassia.ru','khakassia.su','kharkov.ua','kherson.ua','khv.ru','kiev.ua','kirov.ru','km.ru','km.ua','kms.ru','koenig.ru','komi.ru','komi.su','kostroma.ru','krasnodar.su','krasnoyarsk.ru','krovatka.su','ks.ua','kuban.ru','kurgan.ru','kurgan.su','kursk.ru','kustanai.ru','kustanai.su','kuzbass.ru','lact.ru','land.ru','lenug.su','lg.ua','lgg.ru','lipetsk.ru','liveinternet.ru','livejournal.com','loveplanet.ru','lp.md','ltd.ua','ltd.uk','lugansk.ua','lutsk.ua','lv.md','lviv.ua','lx-host.net','magadan.ru','magnitka.ru','mail.ru','mail15.com','mail333.com','mail333.su','mam.by','mangyshlak.su','mari-el.ru','mari.ru','marine.ru','mchost.ru','me.uk','minsk.by','mirahost.ru','mk.ua','mogilev.by','moiforum.info','moikrug.ru','mordovia.ru','mordovia.su','mosreg.ru','moy.su','mozello.com','mozello.ru','mpchat.com','msk.ru','msk.su','msu.ru','murmansk.ru','murmansk.su','my1.ru','mybb.ru','mybb2.ru','mylivepage.ru','mytis.ru','na.by','nakhodka.ru','nalchik.ru','nalchik.su','name.tr','narod.ru','narod2.ru','navoi.su','ne.jp','net.au','net.br','net.cn','net.co','net.hr','net.id','net.il','net.in','net.nz','net.ph','net.pk','net.pl','net.ru','net.tr','net.tw','net.ua','net.uk','net.vn','netangels.ru','newhost.ru','newmail.ru','nextmail.ru','nightmail.ru','nikolaev.ua','nkz.ru','nm.ru','nn.ru','nnov.ru','norilsk.ru','north-kazakhstan.su','nov.ru','nov.su','novosibirsk.ru','novsk.ru','ns.md','nsk.ru','nsk.su','nsknet.ru','obninsk.com','obninsk.su','oc.md','od.ua','odessa.ua','of.by','offtop.ru','ok.ru','oml.ru','omsk.ru','or.jp','or.kz','or.md','orc.ru','orenburg.ru','org.ar','org.au','org.bd','org.br','org.by','org.cn','org.co','org.eg','org.es','org.hk','org.il','org.in','org.md','org.mx','org.my','org.ng','org.nz','org.pe','org.ph','org.pk','org.pl','org.rs','org.ru','org.sa','org.sg','org.tr','org.tw','org.ua','org.uk','org.uy','org.ve','org.vn','org.za','oryol.ru','oskol.ru','p0.ru','palana.ru','pe.hu','penza.ru','penza.su','perm.ru','pisem.net','pisem.su','pl.ua','plc.uk','pochta.org','pochta.ru','pochtamt.ru','pokrovsk.su','poltava.ua','polubomu.ru','pop3.ru','postman.ru','pp.ru','pp.ua','pskov.ru','ptz.ru','pud.ru','pyatigorsk.ru','r2.ru','r35.ru','r52.ru','rb.md','rbcmail.ru','rnd.ru','rovno.ua','rs.md','ru.net','ru.ru','rubtsovsk.ru','russian.ru','rv.ua','rxfly.net','ryazan.ru','rz.md','s36.ru','sakhalin.ru','samara.ru','saratov.ru','sbn.bz','sch.uk','sd.md','sebastopol.ua','sg.md','shop.by','simbirsk.ru','sitecity.ru','siteedit.ru','sky.ru','sl.md','smolensk.ru','smtp.ru','snz.ru','so.kz','sochi.su','sp.ru','spb.ru','spb.su','spybb.ru','sr.md','st.md','stavropol.ru','stih.ru','stsland.ru','stv.ru','subs.ru','sumy.ua','surgut.ru','sv.md','syzran.ru','tagil.ru','tamb.ru','tambov.ru','tashkent.su','tatarstan.ru','te.ua','termez.su','ternopil.ua','tg.md','tl.md','togliatti.su','tom.ru','tomsk.ru','tomsknet.ru','tora.ru','tr.gg','tr.md','tripod.com','troitsk.su','ts.md','ts6.ru','tsaritsyn.ru','tselinograd.su','tsk.ru','tu1.ru','tula.net','tula.ru','tula.su','tulpar.net','tumblr.com','tut.by','tut.su','tuva.ru','tuva.su','tv.tr','tver.ru','tyumen.ru','ucoz.com','ucoz.es','ucoz.kz','ucoz.net','ucoz.org','ucoz.ru','ucoz.ua','udm.ru','udmurtia.ru','ufanet.ru','ukrbiz.net','ulan-ude.ru','umi.ru','un.md','ur.ru','url.ph','uz.ua','uzhgorod.ua','vdonsk.ru','vinnica.ua','vio.ru','vip.su','vipcentr.ru','vippochta.ru','vipshop.ru','viptop.ru','vitebsk.by','vl.md','vl.ru','vladikavkaz.ru','vladikavkaz.su','vladimir.ru','vladimir.su','vladivostok.ru','vn.ua','vo.uz','volgograd.ru','vologda.ru','vologda.su','voronezh.ru','vov.ru','vrn.ru','wallst.ru','web.tr','webhost.ru','webservis.ru','webstolica.ru','weebly.com','wmsite.ru','wordpress.com','wyksa.ru','x53.ru','xeno.ru','xost.ru','ya.ru','yakutia.ru','yakutia.su','yalta.ua','yamal.ru','yandex.ru','yar.ru','yard.ru','yaroslavl.ru','yekaterinburg.ru','ykt.ru','yuzhno-sakhalinsk.ru','yvision.kz','zaporizhzhe.ua','zgrad.ru','zoob.info','zp.ua','ru.com','yandex-team.ru','turbopages.org','mos.ru');

$raw_domain = ($x) -> {{return Url::CutWWW(Url::GetHost($x)) }};

$d4_extract_re = Re2::Capture('([^.]*\\\.[^.]*\\\.[^.]*\\\.[^.]*)$');
$d3_extract_re = Re2::Capture('([^.]*\\\.[^.]*\\\.[^.]*)$');
$d2_extract_re = Re2::Capture('([^.]*\\\.[^.]*)$');

$d4_plus_match_re = Re2::Match('.*([^.]*\\\.[^.]*\\\.[^.]*\\\.[^.]*)$');
$d3_plus_match_re = Re2::Match('.*([^.]*\\\.[^.]*\\\.[^.]*)$');

$d4_extract_res = ($x) -> {{return $d4_extract_re($raw_domain($x))._1}};
$d3_extract_res = ($x) -> {{return $d3_extract_re($raw_domain($x))._1}};
$d2_extract_res = ($x) -> {{return $d2_extract_re($raw_domain($x))._1}};


$has_metrika_domain = ($x) -> {{
    return if($d4_plus_match_re($raw_domain($x)) and $d3_extract_res($x) in $d3_exclusion, $d4_extract_res($x),
        if($d3_plus_match_re($raw_domain($x))and $d2_extract_res($x) in $d2_exclusion, $d3_extract_res($x), $d2_extract_res($x)
        )
    )
}};

$get_url_from_params = ($http_params) -> {{RETURN String::CgiUnescape(Url::GetCGIParam('http://fake.domain/?' || ($http_params ?? ""), 'url'))}};

$main_table =
(select
    domain,
    country,
    ddate,
    uid
from
(
SELECT
    Url::HostNameToPunycode($has_metrika_domain($get_url_from_params(http_params))) as domain,
    Geo::RoundRegionByIp(ip, 'country').id as country,
    cast(DateTime::MakeDate(DateTime::FromSeconds(cast(unixtime as UInt32))) as String) as ddate,
    if(yandexuid == '-' or yandexuid is null, if(fyandexuid is null, ip, fyandexuid), yandexuid) as uid
from
    range(`logs/bar-navig-log/1d`, `{date_start}`, `{date_end}`)
where
    http_params != 'ver=0&show=0' and
    yasoft = 'yabrowser' and
    Unicode::IsUtf($get_url_from_params(http_params))
)
where
    ddate >= '{date_start}' and
    ddate <= '{date_end}' and
    domain is not null and
    domain!='' and
    $is_domain(domain)
);


--Final table
insert into `home/metrica-analytics/.tmp/browser_desktop_week_test` with truncate
select
    total.domain as domain,
    total.ddate as ddate,
    cast(if(country.max_country!=0, country.max_country, 0) as Uint64) as country_desktop,
    country.country_users as country_users_desktop,
    total.users as users_desktop,
    total.hits as hits_desktop
from
(
select
    domain,
    ddate,
    count(distinct uid) as users,
    count(1) as hits
from
    $main_table
group by
    domain,
    ddate
) as total
inner join
(
select
    domain,
    ddate,
    MAX_BY(country, users_country) as max_country,
    max(users_country) as country_users
from
    (
    select
        domain,
        ddate,
        country,
        count(distinct uid) as users_country
    from
        $main_table
    group by
        domain,
        country,
        ddate
    )
group by
    domain,
    ddate
) as country
using (domain, ddate)
"""

mobile_query = """
select
    HasMetrikaDomain as `domain`,
    EventDate as ddate,
    users as users_mobile,
    hits as hits_mobile,
    country as country_mobile,
    country_users as country_users_mobile
from
(
    WITH
        domain(cutWWW('http://' || domain(PP_Key2))) as rawDomain,
        if( extract(rawDomain, '([^.]*\\\.[^.]*\\\.[^.]*\\\.[^.]*)$')!= '' and extract(rawDomain, '([^.]*\\\.[^.]*\\\.[^.]*)$') in ('at.tut.by','blogs.mail.ru','blogs.privet.ru','blogspot.co.at','blogspot.co.il','blogspot.co.ke','blogspot.co.nz','blogspot.co.uk','blogspot.com.ar','blogspot.com.au','blogspot.com.br','blogspot.com.by','blogspot.com.co','blogspot.com.cy','blogspot.com.eg','blogspot.com.es','blogspot.com.mt','blogspot.com.ng','blogspot.com.tr','blogspot.com.uy','h.com.ua','ho.com.ua','lj.rossia.org','mywebpage.netscape.com','pp.net.ua','web.ur.ru','afisha.yandex.ru','fotki.yandex.ru','maps.yandex.ru','market.yandex.ru','money.yandex.ru','news.yandex.ru','rabota.yandex.ru','rasp.yandex.ru','realty.yandex.ru','slovari.yandex.ru','store.yandex.ru','taxi.yandex.ru','toloka.yandex.ru','travel.yandex.ru','tv.yandex.ru','video.yandex.ru','ws.co.ua','cdn.ampproject.org'),
                extract(rawDomain, '([^.]*\\\.[^.]*\\\.[^.]*\\\.[^.]*)$'),
                if(extract(rawDomain, '([^.]*\\\.[^.]*\\\.[^.]*)$') != '' and extract(rawDomain, '([^.]*\\\.[^.]*)$') in ('0catch.com','0pk.ru','16mb.com','1bb.ru','1gb.ru','2bb.ru','3bb.ru','3dn.ru','4bb.ru','4u.ru','50megs.com','50webs.com','5bb.ru','6bb.ru','70mb.ru','96.lt','abkhazia.su','ac.at','ac.be','ac.id','ac.il','ac.jp','ac.ru','ac.th','ac.uk','adygeya.ru','adygeya.su','aecru.org','afaik.ru','agava.ru','aha.ru','aiq.ru','aktyubinsk.su','al.ru','alfamoon.com','alfaspace.net','alltrades.ru','altai.ru','am9.ru','amur.ru','amursk.ru','an.md','appspot.com','arkhangelsk.ru','arkhangelsk.su','armenia.su','ashgabad.su','astrakhan.ru','at.ua','av.tr','az.ru','azerbaijan.su','baikal.ru','balashov.su','bashkiria.ru','bashkiria.su','bbs.tr','be.md','bel.tr','belgorod.ru','belgorod.su','beon.ru','besaba.com','best-host.ru','bip.ru','bir.ru','biz.tr','biz.ua','bl.md','blog.ru','blogonline.ru','blogsome.com','blogspot.be','blogspot.ca','blogspot.ch','blogspot.com','blogspot.cz','blogspot.de','blogspot.dk','blogspot.fi','blogspot.fr','blogspot.gr','blogspot.hu','blogspot.ie','blogspot.in','blogspot.it','blogspot.jp','blogspot.mx','blogspot.nl','blogspot.no','blogspot.pt','blogspot.ro','blogspot.ru','blogspot.se','blogspot.sg','blogspot.tw','boom.ru','borda.ru','bos.ru','br.md','brest.by','bryansk.ru','bryansk.su','bs.md','bukhara.su','buryatia.ru','by.com','by.ru','byethost8.com','cbg.ru','cc.md','cc.ua','cg.md','ch.md','chat.ru','chel.ru','chelyabinsk.ru','chernovtsy.ua','chimkent.su','chita.ru','chukotka.ru','chuvashia.ru','ck.ua','cl.md','clan.su','cm.md','cmw.ru','cn.md','cn.ua','co.id','co.il','co.in','co.jp','co.kr','co.md','co.nz','co.th','co.ua','co.uk','co.za','com.af','com.al','com.ar','com.au','com.bd','com.bh','com.bn','com.bo','com.br','com.by','com.bz','com.cn','com.co','com.com','com.cy','com.de','com.do','com.ec','com.ee','com.eg','com.es','com.et','com.ge','com.gh','com.gr','com.gt','com.hk','com.hr','com.jm','com.kh','com.kw','com.kz','com.lb','com.ly','com.md','com.mk','com.mm','com.mt','com.mx','com.my','com.na','com.ng','com.ni','com.np','com.om','com.pa','com.pe','com.pg','com.ph','com.pk','com.pl','com.pr','com.pt','com.py','com.qa','com.ro','com.ru','com.sa','com.sg','com.sv','com.tn','com.tr','com.tw','com.ua','com.uy','com.vc','com.ve','com.vn','cr.md','crimea.ua','cs.md','ct.md','cu.md','cv.ua','cwx.ru','da.ru','dagestan.ru','dagestan.su','dax.ru','db.md','dem.ru','diary.ru','dn.md','dn.ua','do.am','donetsk.ua','dp.ua','dr.md','dtn.ru','dudinka.ru','e-burg.ru','e-stile.ru','east-kazakhstan.su','ed.md','edu.au','edu.ru','edu.tr','edu.ua','esy.es','eu.int','exnet.su','fanforum.ru','far.ru','fareast.ru','fastbb.ru','fatal.ru','fl.md','flybb.ru','fo.ru','forever.kz','forum24.ru','forumbb.ru','fr.md','freewebpage.org','fromru.com','fromru.su','front.ru','fsbo.ru','fud.ru','fvds.ru','ge.md','gen.tr','geocities.com','georgia.su','gl.md','go.id','go.ru','gob.ar','gob.gt','gob.mx','gob.pa','gob.pe','gob.sv','gob.ve','gomel.by','gov.ac','gov.ae','gov.af','gov.ag','gov.ai','gov.al','gov.an','gov.ao','gov.ar','gov.au','gov.aw','gov.az','gov.ba','gov.bb','gov.bd','gov.bf','gov.bh','gov.bi','gov.bm','gov.bn','gov.bo','gov.br','gov.bs','gov.bt','gov.bw','gov.by','gov.bz','gov.cd','gov.ch','gov.ci','gov.ck','gov.cl','gov.cm','gov.cn','gov.co','gov.com','gov.cu','gov.cv','gov.cx','gov.cy','gov.cz','gov.de','gov.dj','gov.dk','gov.dm','gov.do','gov.dz','gov.ec','gov.ee','gov.eg','gov.er','gov.et','gov.fj','gov.fk','gov.fo','gov.gd','gov.gg','gov.gh','gov.gi','gov.gm','gov.gn','gov.gr','gov.gs','gov.gu','gov.gw','gov.gy','gov.hk','gov.hn','gov.ht','gov.hu','gov.ie','gov.il','gov.im','gov.in','gov.iq','gov.ir','gov.it','gov.je','gov.jm','gov.jo','gov.kh','gov.ki','gov.kn','gov.kr','gov.kw','gov.ky','gov.la','gov.lb','gov.lc','gov.lk','gov.lr','gov.ls','gov.lt','gov.lv','gov.ly','gov.ma','gov.me','gov.mg','gov.mk','gov.ml','gov.mm','gov.mn','gov.mo','gov.mp','gov.mr','gov.ms','gov.mt','gov.mu','gov.mv','gov.mw','gov.my','gov.mz','gov.na','gov.net','gov.nf','gov.ng','gov.np','gov.nr','gov.nu','gov.om','gov.org','gov.pf','gov.pg','gov.ph','gov.pk','gov.pl','gov.pn','gov.pr','gov.ps','gov.pt','gov.py','gov.qa','gov.ro','gov.rs','gov.ru','gov.rw','gov.sa','gov.sb','gov.sc','gov.sd','gov.se','gov.sg','gov.sh','gov.si','gov.sk','gov.sl','gov.sr','gov.st','gov.sy','gov.sz','gov.tc','gov.tk','gov.tl','gov.tm','gov.tn','gov.to','gov.tp','gov.tr','gov.tt','gov.tw','gov.ua','gov.uk','gov.vc','gov.ve','gov.vg','gov.vi','gov.vn','gov.vu','gov.ws','gov.ye','gov.yu','gov.za','gov.zm','gov.zw','gr.md','grodno.by','grozny.ru','grozny.su','h1.ru','h10.ru','h11.ru','h12.ru','h14.ru','h15.ru','h16.ru','h17.ru','h18.ru','habrahabr.ru','hn.md','ho.ua','hobi.ru','hoha.ru','hol.es','holm.ru','hop.ru','hostia.ru','hotbox.ru','hoter.ru','hotmail.ru','hut.ru','hut1.ru','hut2.ru','i-nets.ru','iatp.by','id.ru','if.ua','in.ua','inc.ru','inf.ua','infacms.com','info.md','info.tr','infobox.ru','int.ru','io.ua','irk.ru','irkutsk.ru','ivano-frankivsk.ua','ivanovo.ru','ivanovo.su','izhevsk.ru','jamal.ru','jamango.ru','jambyl.su','jar.ru','jimdo.com','jino-net.ru','jino.ru','joshkar-ola.ru','joy.by','k-uralsk.ru','k12.tr','kalmykia.ru','kalmykia.su','kaluga.ru','kaluga.su','kamchatka.ru','karacol.su','karaganda.su','karelia.ru','karelia.su','kazan.ru','kazan.ws','kchr.ru','kemerovo.ru','kh.ua','khabarovsk.ru','khakassia.ru','khakassia.su','kharkov.ua','kherson.ua','khv.ru','kiev.ua','kirov.ru','km.ru','km.ua','kms.ru','koenig.ru','komi.ru','komi.su','kostroma.ru','krasnodar.su','krasnoyarsk.ru','krovatka.su','ks.ua','kuban.ru','kurgan.ru','kurgan.su','kursk.ru','kustanai.ru','kustanai.su','kuzbass.ru','lact.ru','land.ru','lenug.su','lg.ua','lgg.ru','lipetsk.ru','liveinternet.ru','livejournal.com','loveplanet.ru','lp.md','ltd.ua','ltd.uk','lugansk.ua','lutsk.ua','lv.md','lviv.ua','lx-host.net','magadan.ru','magnitka.ru','mail.ru','mail15.com','mail333.com','mail333.su','mam.by','mangyshlak.su','mari-el.ru','mari.ru','marine.ru','mchost.ru','me.uk','minsk.by','mirahost.ru','mk.ua','mogilev.by','moiforum.info','moikrug.ru','mordovia.ru','mordovia.su','mosreg.ru','moy.su','mozello.com','mozello.ru','mpchat.com','msk.ru','msk.su','msu.ru','murmansk.ru','murmansk.su','my1.ru','mybb.ru','mybb2.ru','mylivepage.ru','mytis.ru','na.by','nakhodka.ru','nalchik.ru','nalchik.su','name.tr','narod.ru','narod2.ru','navoi.su','ne.jp','net.au','net.br','net.cn','net.co','net.hr','net.id','net.il','net.in','net.nz','net.ph','net.pk','net.pl','net.ru','net.tr','net.tw','net.ua','net.uk','net.vn','netangels.ru','newhost.ru','newmail.ru','nextmail.ru','nightmail.ru','nikolaev.ua','nkz.ru','nm.ru','nn.ru','nnov.ru','norilsk.ru','north-kazakhstan.su','nov.ru','nov.su','novosibirsk.ru','novsk.ru','ns.md','nsk.ru','nsk.su','nsknet.ru','obninsk.com','obninsk.su','oc.md','od.ua','odessa.ua','of.by','offtop.ru','ok.ru','oml.ru','omsk.ru','or.jp','or.kz','or.md','orc.ru','orenburg.ru','org.ar','org.au','org.bd','org.br','org.by','org.cn','org.co','org.eg','org.es','org.hk','org.il','org.in','org.md','org.mx','org.my','org.ng','org.nz','org.pe','org.ph','org.pk','org.pl','org.rs','org.ru','org.sa','org.sg','org.tr','org.tw','org.ua','org.uk','org.uy','org.ve','org.vn','org.za','oryol.ru','oskol.ru','p0.ru','palana.ru','pe.hu','penza.ru','penza.su','perm.ru','pisem.net','pisem.su','pl.ua','plc.uk','pochta.org','pochta.ru','pochtamt.ru','pokrovsk.su','poltava.ua','polubomu.ru','pop3.ru','postman.ru','pp.ru','pp.ua','pskov.ru','ptz.ru','pud.ru','pyatigorsk.ru','r2.ru','r35.ru','r52.ru','rb.md','rbcmail.ru','rnd.ru','rovno.ua','rs.md','ru.net','ru.ru','rubtsovsk.ru','russian.ru','rv.ua','rxfly.net','ryazan.ru','rz.md','s36.ru','sakhalin.ru','samara.ru','saratov.ru','sbn.bz','sch.uk','sd.md','sebastopol.ua','sg.md','shop.by','simbirsk.ru','sitecity.ru','siteedit.ru','sky.ru','sl.md','smolensk.ru','smtp.ru','snz.ru','so.kz','sochi.su','sp.ru','spb.ru','spb.su','spybb.ru','sr.md','st.md','stavropol.ru','stih.ru','stsland.ru','stv.ru','subs.ru','sumy.ua','surgut.ru','sv.md','syzran.ru','tagil.ru','tamb.ru','tambov.ru','tashkent.su','tatarstan.ru','te.ua','termez.su','ternopil.ua','tg.md','tl.md','togliatti.su','tom.ru','tomsk.ru','tomsknet.ru','tora.ru','tr.gg','tr.md','tripod.com','troitsk.su','ts.md','ts6.ru','tsaritsyn.ru','tselinograd.su','tsk.ru','tu1.ru','tula.net','tula.ru','tula.su','tulpar.net','tumblr.com','tut.by','tut.su','tuva.ru','tuva.su','tv.tr','tver.ru','tyumen.ru','ucoz.com','ucoz.es','ucoz.kz','ucoz.net','ucoz.org','ucoz.ru','ucoz.ua','udm.ru','udmurtia.ru','ufanet.ru','ukrbiz.net','ulan-ude.ru','umi.ru','un.md','ur.ru','url.ph','uz.ua','uzhgorod.ua','vdonsk.ru','vinnica.ua','vio.ru','vip.su','vipcentr.ru','vippochta.ru','vipshop.ru','viptop.ru','vitebsk.by','vl.md','vl.ru','vladikavkaz.ru','vladikavkaz.su','vladimir.ru','vladimir.su','vladivostok.ru','vn.ua','vo.uz','volgograd.ru','vologda.ru','vologda.su','voronezh.ru','vov.ru','vrn.ru','wallst.ru','web.tr','webhost.ru','webservis.ru','webstolica.ru','weebly.com','wmsite.ru','wordpress.com','wyksa.ru','x53.ru','xeno.ru','xost.ru','ya.ru','yakutia.ru','yakutia.su','yalta.ua','yamal.ru','yandex.ru','yar.ru','yard.ru','yaroslavl.ru','yekaterinburg.ru','ykt.ru','yuzhno-sakhalinsk.ru','yvision.kz','zaporizhzhe.ua','zgrad.ru','zoob.info','zp.ua','ru.com','yandex-team.ru','turbopages.org','mos.ru'),
                    extract(rawDomain, '([^.]*\\\.[^.]*\\\.[^.]*)$'),
                    extract(rawDomain, '([^.]*\\\.[^.]*)$')
                )
        ) as HasMetrikaDomain
    Select HasMetrikaDomain, EventDate, uniq(DeviceIDHash) AS users,
        count() as hits
    from
        mobgiga.events_all
    ARRAY JOIN
        ParsedParams.Key1 AS PP_Key1,
        ParsedParams.Key2 AS PP_Key2
    WHERE
        APIKey IN (18313, 18316, 19531, 19534, 106400) AND
        EventDate >= '{date_start}' AND
        EventDate <= '{date_end}' AND
        EventName = 'url opened' AND
        PP_Key1 = 'url' AND
        rawDomain != '' AND
        match(rawDomain, '^([a-zа-яё0-9]([a-zа-яё0-9\\\-_]{{0,61}}[a-zа-яё0-9])?\\\.)+(xn\\\-\\\-[a-z0-9\\\-]{{2,}}|[a-zа-яё]{{2,}})$') and
        cityHash64(HasMetrikaDomain) % {mobile_sample_base} = {sample}
    group by
        HasMetrikaDomain,
        EventDate
) as a
all inner join
(
    select
        HasMetrikaDomain,
        EventDate,
        max(devices) as country_users,
        argMax(one_country, devices) as country
    from
    (
        WITH
            domain(cutWWW('http://' || domain(PP_Key2))) as rawDomain,
            if( extract(rawDomain, '([^.]*\\\.[^.]*\\\.[^.]*\\\.[^.]*)$')!= '' and extract(rawDomain, '([^.]*\\\.[^.]*\\\.[^.]*)$') in ('at.tut.by','blogs.mail.ru','blogs.privet.ru','blogspot.co.at','blogspot.co.il','blogspot.co.ke','blogspot.co.nz','blogspot.co.uk','blogspot.com.ar','blogspot.com.au','blogspot.com.br','blogspot.com.by','blogspot.com.co','blogspot.com.cy','blogspot.com.eg','blogspot.com.es','blogspot.com.mt','blogspot.com.ng','blogspot.com.tr','blogspot.com.uy','h.com.ua','ho.com.ua','lj.rossia.org','mywebpage.netscape.com','pp.net.ua','web.ur.ru','afisha.yandex.ru','fotki.yandex.ru','maps.yandex.ru','market.yandex.ru','money.yandex.ru','news.yandex.ru','rabota.yandex.ru','rasp.yandex.ru','realty.yandex.ru','slovari.yandex.ru','store.yandex.ru','taxi.yandex.ru','toloka.yandex.ru','travel.yandex.ru','tv.yandex.ru','video.yandex.ru','ws.co.ua','cdn.ampproject.org'),
                    extract(rawDomain, '([^.]*\\\.[^.]*\\\.[^.]*\\\.[^.]*)$'),
                    if(extract(rawDomain, '([^.]*\\\.[^.]*\\\.[^.]*)$') != '' and extract(rawDomain, '([^.]*\\\.[^.]*)$') in ('0catch.com','0pk.ru','16mb.com','1bb.ru','1gb.ru','2bb.ru','3bb.ru','3dn.ru','4bb.ru','4u.ru','50megs.com','50webs.com','5bb.ru','6bb.ru','70mb.ru','96.lt','abkhazia.su','ac.at','ac.be','ac.id','ac.il','ac.jp','ac.ru','ac.th','ac.uk','adygeya.ru','adygeya.su','aecru.org','afaik.ru','agava.ru','aha.ru','aiq.ru','aktyubinsk.su','al.ru','alfamoon.com','alfaspace.net','alltrades.ru','altai.ru','am9.ru','amur.ru','amursk.ru','an.md','appspot.com','arkhangelsk.ru','arkhangelsk.su','armenia.su','ashgabad.su','astrakhan.ru','at.ua','av.tr','az.ru','azerbaijan.su','baikal.ru','balashov.su','bashkiria.ru','bashkiria.su','bbs.tr','be.md','bel.tr','belgorod.ru','belgorod.su','beon.ru','besaba.com','best-host.ru','bip.ru','bir.ru','biz.tr','biz.ua','bl.md','blog.ru','blogonline.ru','blogsome.com','blogspot.be','blogspot.ca','blogspot.ch','blogspot.com','blogspot.cz','blogspot.de','blogspot.dk','blogspot.fi','blogspot.fr','blogspot.gr','blogspot.hu','blogspot.ie','blogspot.in','blogspot.it','blogspot.jp','blogspot.mx','blogspot.nl','blogspot.no','blogspot.pt','blogspot.ro','blogspot.ru','blogspot.se','blogspot.sg','blogspot.tw','boom.ru','borda.ru','bos.ru','br.md','brest.by','bryansk.ru','bryansk.su','bs.md','bukhara.su','buryatia.ru','by.com','by.ru','byethost8.com','cbg.ru','cc.md','cc.ua','cg.md','ch.md','chat.ru','chel.ru','chelyabinsk.ru','chernovtsy.ua','chimkent.su','chita.ru','chukotka.ru','chuvashia.ru','ck.ua','cl.md','clan.su','cm.md','cmw.ru','cn.md','cn.ua','co.id','co.il','co.in','co.jp','co.kr','co.md','co.nz','co.th','co.ua','co.uk','co.za','com.af','com.al','com.ar','com.au','com.bd','com.bh','com.bn','com.bo','com.br','com.by','com.bz','com.cn','com.co','com.com','com.cy','com.de','com.do','com.ec','com.ee','com.eg','com.es','com.et','com.ge','com.gh','com.gr','com.gt','com.hk','com.hr','com.jm','com.kh','com.kw','com.kz','com.lb','com.ly','com.md','com.mk','com.mm','com.mt','com.mx','com.my','com.na','com.ng','com.ni','com.np','com.om','com.pa','com.pe','com.pg','com.ph','com.pk','com.pl','com.pr','com.pt','com.py','com.qa','com.ro','com.ru','com.sa','com.sg','com.sv','com.tn','com.tr','com.tw','com.ua','com.uy','com.vc','com.ve','com.vn','cr.md','crimea.ua','cs.md','ct.md','cu.md','cv.ua','cwx.ru','da.ru','dagestan.ru','dagestan.su','dax.ru','db.md','dem.ru','diary.ru','dn.md','dn.ua','do.am','donetsk.ua','dp.ua','dr.md','dtn.ru','dudinka.ru','e-burg.ru','e-stile.ru','east-kazakhstan.su','ed.md','edu.au','edu.ru','edu.tr','edu.ua','esy.es','eu.int','exnet.su','fanforum.ru','far.ru','fareast.ru','fastbb.ru','fatal.ru','fl.md','flybb.ru','fo.ru','forever.kz','forum24.ru','forumbb.ru','fr.md','freewebpage.org','fromru.com','fromru.su','front.ru','fsbo.ru','fud.ru','fvds.ru','ge.md','gen.tr','geocities.com','georgia.su','gl.md','go.id','go.ru','gob.ar','gob.gt','gob.mx','gob.pa','gob.pe','gob.sv','gob.ve','gomel.by','gov.ac','gov.ae','gov.af','gov.ag','gov.ai','gov.al','gov.an','gov.ao','gov.ar','gov.au','gov.aw','gov.az','gov.ba','gov.bb','gov.bd','gov.bf','gov.bh','gov.bi','gov.bm','gov.bn','gov.bo','gov.br','gov.bs','gov.bt','gov.bw','gov.by','gov.bz','gov.cd','gov.ch','gov.ci','gov.ck','gov.cl','gov.cm','gov.cn','gov.co','gov.com','gov.cu','gov.cv','gov.cx','gov.cy','gov.cz','gov.de','gov.dj','gov.dk','gov.dm','gov.do','gov.dz','gov.ec','gov.ee','gov.eg','gov.er','gov.et','gov.fj','gov.fk','gov.fo','gov.gd','gov.gg','gov.gh','gov.gi','gov.gm','gov.gn','gov.gr','gov.gs','gov.gu','gov.gw','gov.gy','gov.hk','gov.hn','gov.ht','gov.hu','gov.ie','gov.il','gov.im','gov.in','gov.iq','gov.ir','gov.it','gov.je','gov.jm','gov.jo','gov.kh','gov.ki','gov.kn','gov.kr','gov.kw','gov.ky','gov.la','gov.lb','gov.lc','gov.lk','gov.lr','gov.ls','gov.lt','gov.lv','gov.ly','gov.ma','gov.me','gov.mg','gov.mk','gov.ml','gov.mm','gov.mn','gov.mo','gov.mp','gov.mr','gov.ms','gov.mt','gov.mu','gov.mv','gov.mw','gov.my','gov.mz','gov.na','gov.net','gov.nf','gov.ng','gov.np','gov.nr','gov.nu','gov.om','gov.org','gov.pf','gov.pg','gov.ph','gov.pk','gov.pl','gov.pn','gov.pr','gov.ps','gov.pt','gov.py','gov.qa','gov.ro','gov.rs','gov.ru','gov.rw','gov.sa','gov.sb','gov.sc','gov.sd','gov.se','gov.sg','gov.sh','gov.si','gov.sk','gov.sl','gov.sr','gov.st','gov.sy','gov.sz','gov.tc','gov.tk','gov.tl','gov.tm','gov.tn','gov.to','gov.tp','gov.tr','gov.tt','gov.tw','gov.ua','gov.uk','gov.vc','gov.ve','gov.vg','gov.vi','gov.vn','gov.vu','gov.ws','gov.ye','gov.yu','gov.za','gov.zm','gov.zw','gr.md','grodno.by','grozny.ru','grozny.su','h1.ru','h10.ru','h11.ru','h12.ru','h14.ru','h15.ru','h16.ru','h17.ru','h18.ru','habrahabr.ru','hn.md','ho.ua','hobi.ru','hoha.ru','hol.es','holm.ru','hop.ru','hostia.ru','hotbox.ru','hoter.ru','hotmail.ru','hut.ru','hut1.ru','hut2.ru','i-nets.ru','iatp.by','id.ru','if.ua','in.ua','inc.ru','inf.ua','infacms.com','info.md','info.tr','infobox.ru','int.ru','io.ua','irk.ru','irkutsk.ru','ivano-frankivsk.ua','ivanovo.ru','ivanovo.su','izhevsk.ru','jamal.ru','jamango.ru','jambyl.su','jar.ru','jimdo.com','jino-net.ru','jino.ru','joshkar-ola.ru','joy.by','k-uralsk.ru','k12.tr','kalmykia.ru','kalmykia.su','kaluga.ru','kaluga.su','kamchatka.ru','karacol.su','karaganda.su','karelia.ru','karelia.su','kazan.ru','kazan.ws','kchr.ru','kemerovo.ru','kh.ua','khabarovsk.ru','khakassia.ru','khakassia.su','kharkov.ua','kherson.ua','khv.ru','kiev.ua','kirov.ru','km.ru','km.ua','kms.ru','koenig.ru','komi.ru','komi.su','kostroma.ru','krasnodar.su','krasnoyarsk.ru','krovatka.su','ks.ua','kuban.ru','kurgan.ru','kurgan.su','kursk.ru','kustanai.ru','kustanai.su','kuzbass.ru','lact.ru','land.ru','lenug.su','lg.ua','lgg.ru','lipetsk.ru','liveinternet.ru','livejournal.com','loveplanet.ru','lp.md','ltd.ua','ltd.uk','lugansk.ua','lutsk.ua','lv.md','lviv.ua','lx-host.net','magadan.ru','magnitka.ru','mail.ru','mail15.com','mail333.com','mail333.su','mam.by','mangyshlak.su','mari-el.ru','mari.ru','marine.ru','mchost.ru','me.uk','minsk.by','mirahost.ru','mk.ua','mogilev.by','moiforum.info','moikrug.ru','mordovia.ru','mordovia.su','mosreg.ru','moy.su','mozello.com','mozello.ru','mpchat.com','msk.ru','msk.su','msu.ru','murmansk.ru','murmansk.su','my1.ru','mybb.ru','mybb2.ru','mylivepage.ru','mytis.ru','na.by','nakhodka.ru','nalchik.ru','nalchik.su','name.tr','narod.ru','narod2.ru','navoi.su','ne.jp','net.au','net.br','net.cn','net.co','net.hr','net.id','net.il','net.in','net.nz','net.ph','net.pk','net.pl','net.ru','net.tr','net.tw','net.ua','net.uk','net.vn','netangels.ru','newhost.ru','newmail.ru','nextmail.ru','nightmail.ru','nikolaev.ua','nkz.ru','nm.ru','nn.ru','nnov.ru','norilsk.ru','north-kazakhstan.su','nov.ru','nov.su','novosibirsk.ru','novsk.ru','ns.md','nsk.ru','nsk.su','nsknet.ru','obninsk.com','obninsk.su','oc.md','od.ua','odessa.ua','of.by','offtop.ru','ok.ru','oml.ru','omsk.ru','or.jp','or.kz','or.md','orc.ru','orenburg.ru','org.ar','org.au','org.bd','org.br','org.by','org.cn','org.co','org.eg','org.es','org.hk','org.il','org.in','org.md','org.mx','org.my','org.ng','org.nz','org.pe','org.ph','org.pk','org.pl','org.rs','org.ru','org.sa','org.sg','org.tr','org.tw','org.ua','org.uk','org.uy','org.ve','org.vn','org.za','oryol.ru','oskol.ru','p0.ru','palana.ru','pe.hu','penza.ru','penza.su','perm.ru','pisem.net','pisem.su','pl.ua','plc.uk','pochta.org','pochta.ru','pochtamt.ru','pokrovsk.su','poltava.ua','polubomu.ru','pop3.ru','postman.ru','pp.ru','pp.ua','pskov.ru','ptz.ru','pud.ru','pyatigorsk.ru','r2.ru','r35.ru','r52.ru','rb.md','rbcmail.ru','rnd.ru','rovno.ua','rs.md','ru.net','ru.ru','rubtsovsk.ru','russian.ru','rv.ua','rxfly.net','ryazan.ru','rz.md','s36.ru','sakhalin.ru','samara.ru','saratov.ru','sbn.bz','sch.uk','sd.md','sebastopol.ua','sg.md','shop.by','simbirsk.ru','sitecity.ru','siteedit.ru','sky.ru','sl.md','smolensk.ru','smtp.ru','snz.ru','so.kz','sochi.su','sp.ru','spb.ru','spb.su','spybb.ru','sr.md','st.md','stavropol.ru','stih.ru','stsland.ru','stv.ru','subs.ru','sumy.ua','surgut.ru','sv.md','syzran.ru','tagil.ru','tamb.ru','tambov.ru','tashkent.su','tatarstan.ru','te.ua','termez.su','ternopil.ua','tg.md','tl.md','togliatti.su','tom.ru','tomsk.ru','tomsknet.ru','tora.ru','tr.gg','tr.md','tripod.com','troitsk.su','ts.md','ts6.ru','tsaritsyn.ru','tselinograd.su','tsk.ru','tu1.ru','tula.net','tula.ru','tula.su','tulpar.net','tumblr.com','tut.by','tut.su','tuva.ru','tuva.su','tv.tr','tver.ru','tyumen.ru','ucoz.com','ucoz.es','ucoz.kz','ucoz.net','ucoz.org','ucoz.ru','ucoz.ua','udm.ru','udmurtia.ru','ufanet.ru','ukrbiz.net','ulan-ude.ru','umi.ru','un.md','ur.ru','url.ph','uz.ua','uzhgorod.ua','vdonsk.ru','vinnica.ua','vio.ru','vip.su','vipcentr.ru','vippochta.ru','vipshop.ru','viptop.ru','vitebsk.by','vl.md','vl.ru','vladikavkaz.ru','vladikavkaz.su','vladimir.ru','vladimir.su','vladivostok.ru','vn.ua','vo.uz','volgograd.ru','vologda.ru','vologda.su','voronezh.ru','vov.ru','vrn.ru','wallst.ru','web.tr','webhost.ru','webservis.ru','webstolica.ru','weebly.com','wmsite.ru','wordpress.com','wyksa.ru','x53.ru','xeno.ru','xost.ru','ya.ru','yakutia.ru','yakutia.su','yalta.ua','yamal.ru','yandex.ru','yar.ru','yard.ru','yaroslavl.ru','yekaterinburg.ru','ykt.ru','yuzhno-sakhalinsk.ru','yvision.kz','zaporizhzhe.ua','zgrad.ru','zoob.info','zp.ua','ru.com','yandex-team.ru','turbopages.org','mos.ru'),
                        extract(rawDomain, '([^.]*\\\.[^.]*\\\.[^.]*)$'),
                        extract(rawDomain, '([^.]*\\\.[^.]*)$')
                    )
            ) as HasMetrikaDomain
        SELECT
            HasMetrikaDomain,
            regionToCountry(RegionID) AS one_country,
            EventDate,
            uniq(DeviceIDHash) AS devices
        from
            mobgiga.events_all
        ARRAY JOIN
            ParsedParams.Key1 AS PP_Key1,
            ParsedParams.Key2 AS PP_Key2
        WHERE
            APIKey IN (18313, 18316, 19531, 19534, 106400) AND
            EventDate >= '{date_start}' AND
            EventDate <= '{date_end}' AND
            EventName = 'url opened' AND
            PP_Key1 = 'url' AND
            rawDomain != '' AND
            match(rawDomain, '^([a-zа-яё0-9]([a-zа-яё0-9\\\-_]{{0,61}}[a-zа-яё0-9])?\\\.)+(xn\\\-\\\-[a-z0-9\\\-]{{2,}}|[a-zа-яё]{{2,}})$') and
            cityHash64(HasMetrikaDomain) % toUInt32({mobile_sample_base}) = {sample}
        group by
            HasMetrikaDomain,
            EventDate,
            one_country
    )
    group by
        HasMetrikaDomain,
        EventDate
) as b
using
    (HasMetrikaDomain,
    EventDate)
"""


def merge_mobile_desktop(mobile_queries, opts):
    def pick_max_country(row):
        if int(row['country_users_desktop']) >= int(row['country_users_mobile']):
            return int(row['country_desktop'])
        else:
            return int(row['country_mobile'])

    mobile_data = []

    for one_mobile_query in mobile_queries:
        mobile_data.append(ch.get_df(query=one_mobile_query, max_memory_usage_for_user='20000000000', max_memory_usage='20000000000', max_execution_time='6000', max_memory_usage_for_all_queries='0'))

    mobile_data_df = pd.concat([one_table for one_table in mobile_data], sort=True)

    desktop_data_df = pd.DataFrame(yt.read_table('//home/metrica-analytics/.tmp/browser_desktop_week_test'))
    full_df = desktop_data_df.merge(mobile_data_df, on=['ddate', 'domain'], how='outer').fillna(0)

    full_df['country'] = full_df.apply(lambda row: pick_max_country(row), axis=1)
    full_df['hits'] = full_df['hits_desktop'].astype(int) + full_df['hits_mobile'].astype(int)
    full_df['users'] = full_df['users_desktop'].astype(int) + full_df['users_mobile'].astype(int)
    final_df = full_df[['ddate', 'domain', 'hits', 'users', 'country']][full_df['hits'] > 10]
    return final_df


def get_data(opts):
    mobile_sample_base = 3
    mobile_queries = []
    query_full_desktop = generate_query.get_query(yql_query)

    for sample in range(mobile_sample_base):
        mobile_queries.append(generate_query.get_query(mobile_query, format_dict={'sample': sample, 'mobile_sample_base': mobile_sample_base}))

    yql_db.get_df(query_full_desktop)
    final_df = merge_mobile_desktop(mobile_queries, opts)

    doms_final = final_df[['domain']].drop_duplicates().to_csv(index=False, header=False, sep='\t')

    yt_table_3 = generate_query.get_query('//home/metrica-analytics/reports/metrika_cover/test_browser_hits/{date_start}', shift=opts.shift + 1)
    yt_db.write_to_yt(yt_table_3, final_df, schema={'domain': 'string', 'ddate': 'string', 'country': 'uint32', 'hits': 'uint64', 'users': 'uint64'})
