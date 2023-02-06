# -*- coding: utf-8 -*-

FEMALE_NAMES_MOCK_FILE = {
    'ru': u"""
    # comment
    александра,шура саша,,a al
    василиса
    вероника,ника
    джулия,,,d j jul djul
    кристина,,christine hristina,k c kris cris krist crist
    лилия,лиля,lilly
    сабрина,,sabrine
    фекла
    """,
    'en': u"""
    ada,,adie
    anna,,ann anne annie nance nancy
    annette,,annetta annie netta nettie netty
    april
    aurora,,rori

    denise,,denice denny
    """,
    'tr': u"""
    # comments
    """,
}

MALE_NAMES_MOCK_FILE = {
    'ru': u"""
    # comment
    азарий
    александр,саня саша,alexandros,a al alek aleck
    артемий,тема,,a ar art
    артем,тема,,a ar art artem tema
    василий,вася,basile
    виктор,витя,victor,v vik vic vict vick vikt vickt
    семен,сэм,,s
    семён,семен симеон,simeon simon,sam
    """,
    'en': u"""
    arnold,,arnie
    abraham,,abe abie bram
    alan,,allan allen al
    brian,,bryan bryant
    dennis,,denis den denny
    """,
    'tr': u"""
    # comments
    """,
}

TRANSLITERATIONS_MOCK_FILE = {
    'en': u"""
    # comments
    """,
    'ru': u"""
    # comment
    0т 0
    а a
    б b
    ^в v
    в v w
    г g
    дж j dj dzh
    др$ der dr
    д d

    ^ев ev eu ew
    ев$ ev eff ew
    ^ек ek yek
    е e
    ё yo io eo
    ж zh j
    з z
    ий$ y ij
    ия ia ya iya ija
    и i
    й i j y
    кв kv kw qu
    ксю xiu ksu ksju
    кс x ks
    к% k c
    ^ке ke
    ^ки ki
    ^к k c
    к k ck
    л l
    м m
    н n
    #ов$ off ov ow
    ов$ ov off ow
    о o
    п p
    р r
    с s
    тр$ ter tr
    т t
    у u
    ф f
    х h kh x
    ц ts tz cz
    ^ч tch ch
    ч$ tch ch 4
    ч ch 4
    ш sh sch
    щ sh sch
    ъи ji
    ъе je ie
    ъю ju iu
    ъ
    ый$ iy y yj ii
    ы y i
    ьи ji yi
    ье je ie
    ью ju iu
    ь
    э e
    ^ю yu iu
    ю yu iu u
    %я ya ia
    я ya ja ia
    """,
    'tr': u"""
    s s sh
    ş sh s
    ı i
    ğ g
    ö o
    ü u
    ç ch
    """,
}

LOADED_NAMES = {
    'u': {},
    'm': {
        'ru': {
            u'азарий': {'chunks': [], 'synonyms': set(), 'synonyms_en': set()},
            u'артемий': {
                'chunks': [u'a', u'ar', u'art'],
                'synonyms': {u'тема'},
                'synonyms_en': set(),
            },
            u'артем': {
                'chunks': [u'a', u'ar', u'art', u'artem', u'tema'],
                'synonyms': {u'тема'},
                'synonyms_en': set(),
            },
            u'тема': {
                'chunks': [],
                'synonyms': {u'артем', u'артемий'},
                'synonyms_en': set(),
            },
            u'василий': {
                'chunks': [],
                'synonyms': {u'вася'},
                'synonyms_en': {u'basile'},
            },
            u'вася': {
                'chunks': [],
                'synonyms': {u'василий'},
                'synonyms_en': {u'basile'},
            },
            u'basile': {
                'chunks': [],
                'synonyms': {u'василий', u'вася'},
                'synonyms_en': set(),
            },
            u'саня': {
                'chunks': [],
                'synonyms': {u'александр', u'саша'},
                'synonyms_en': {u'alexandros'},
            },
            u'саша': {
                'chunks': [],
                'synonyms': {u'александр', u'саня'},
                'synonyms_en': {u'alexandros'},
            },
            u'александр': {
                'chunks': [u'a', u'al', u'alek', u'aleck'],
                'synonyms': {u'саня', u'саша'},
                'synonyms_en': {u'alexandros'},
            },
            u'alexandros': {
                'chunks': [],
                'synonyms': {u'александр', u'саня', u'саша'},
                'synonyms_en': set(),
            },
            u'виктор': {
                'chunks': [u'v', u'vik', u'vic', u'vict', u'vick', u'vikt', u'vickt'],
                'synonyms': {u'витя'},
                'synonyms_en': {u'victor'},
            },
            u'витя': {
                'chunks': [],
                'synonyms': {u'виктор'},
                'synonyms_en': {u'victor'},
            },
            u'victor': {
                'chunks': [],
                'synonyms': {u'виктор', u'витя'},
                'synonyms_en': set(),
            },
            u'семен': {
                'chunks': [u's', u'sam'],
                'synonyms': {u'сэм', u'семён', u'симеон'},
                'synonyms_en': {u'simeon', u'simon'},
            },
            u'сэм': {
                'chunks': [],
                'synonyms': {u'семен'},
                'synonyms_en': set(),
            },
            u'симеон': {
                'chunks': [],
                'synonyms': {u'семен'},
                'synonyms_en': {u'simeon', u'simon'},
            },
            u'simon': {
                'chunks': [],
                'synonyms': {u'семен', u'семён', u'симеон', u'сэм'},
                'synonyms_en': {u'simeon'},
            },
            u'simeon': {
                'chunks': [],
                'synonyms': {u'семен', u'семён', u'симеон', u'сэм'},
                'synonyms_en': {u'simon'},
            },
        },
        'en': {
            u'bryan': {'chunks': [], 'synonyms_en': {u'bryant'}, 'synonyms': {u'brian'}},
            u'dennis': {'chunks': [], 'synonyms_en': {u'denis', u'den', u'denny'}, 'synonyms': set()},
            u'abe': {'chunks': [], 'synonyms_en': {u'bram', u'abie'}, 'synonyms': {u'abraham'}},
            u'bryant': {'chunks': [], 'synonyms_en': {u'bryan'}, 'synonyms': {u'brian'}},
            u'allan': {'chunks': [], 'synonyms_en': {u'allen', u'al'}, 'synonyms': {u'alan'}},
            u'arnold': {'chunks': [], 'synonyms_en': {u'arnie'}, 'synonyms': set()},
            u'al': {'chunks': [], 'synonyms_en': {u'allen', u'allan'}, 'synonyms': {u'alan'}},
            u'brian': {'chunks': [], 'synonyms_en': {u'bryan', u'bryant'}, 'synonyms': set()},
            u'denis': {'chunks': [], 'synonyms_en': {u'den', u'denny'}, 'synonyms': {u'dennis'}},
            u'alan': {'chunks': [], 'synonyms_en': {u'allen', u'allan', u'al'}, 'synonyms': set()},
            u'den': {'chunks': [], 'synonyms_en': {u'denis', u'denny'}, 'synonyms': {u'dennis'}},
            u'denny': {'chunks': [], 'synonyms_en': {u'denis', u'den'}, 'synonyms': {u'dennis'}},
            u'allen': {'chunks': [], 'synonyms_en': {u'allan', u'al'}, 'synonyms': {u'alan'}},
            u'arnie': {'chunks': [], 'synonyms_en': set(), 'synonyms': {u'arnold'}},
            u'abraham': {'chunks': [], 'synonyms_en': {u'abe', u'bram', u'abie'}, 'synonyms': set()},
            u'bram': {'chunks': [], 'synonyms_en': {u'abe', u'abie'}, 'synonyms': {u'abraham'}},
            u'abie': {'chunks': [], 'synonyms_en': {u'abe', u'bram'}, 'synonyms': {u'abraham'}},
        },
        'tr': {},
    },
    'f': {
        'ru': {
            u'александра': {
                'chunks': [u'a', u'al'],
                'synonyms': {u'шура', u'саша'},
                'synonyms_en': set(),
            },
            u'шура': {
                'chunks': [],
                'synonyms': {u'александра', u'саша'},
                'synonyms_en': set(),
            },
            u'саша': {
                'chunks': [],
                'synonyms': {u'александра', u'шура'},
                'synonyms_en': set(),
            },
            u'лилия': {'chunks': [], 'synonyms': {u'лиля'}, 'synonyms_en': {u'lilly'}},
            u'лиля': {'chunks': [], 'synonyms': {u'лилия'}, 'synonyms_en': {u'lilly'}},
            u'lilly': {'chunks': [], 'synonyms': {u'лилия', u'лиля'}, 'synonyms_en': set()},
            u'вероника': {'chunks': [], 'synonyms': {u'ника'}, 'synonyms_en': set()},
            u'ника': {'chunks': [], 'synonyms': {u'вероника'}, 'synonyms_en': set()},
            u'василиса': {'chunks': [], 'synonyms': set(), 'synonyms_en': set()},
            u'фекла': {'chunks': [], 'synonyms': set(), 'synonyms_en': set()},
            u'кристина': {
                'chunks': [u'k', u'c', u'kris', u'cris', u'krist', u'crist'],
                'synonyms': set(),
                'synonyms_en': {u'christine', u'hristina'},
            },
            u'christine': {
                'chunks': [],
                'synonyms': {u'кристина'},
                'synonyms_en': {u'hristina'},
            },
            u'hristina': {
                'chunks': [],
                'synonyms': {u'кристина'},
                'synonyms_en': {u'christine'},
            },
            u'джулия': {'chunks': [u'd', u'j', u'jul', u'djul'], 'synonyms': set(), 'synonyms_en': set()},
            u'сабрина': {'chunks': [], 'synonyms': set(), 'synonyms_en': {u'sabrine'}},
            u'sabrine': {'chunks': [], 'synonyms': {u'сабрина'}, 'synonyms_en': set()},
        },
        'en': {
            u'ada': {'chunks': [], 'synonyms_en': {u'adie'}, 'synonyms': set()},
            u'adie': {'chunks': [], 'synonyms_en': set(), 'synonyms': {u'ada'}},
            u'denice': {'chunks': [], 'synonyms_en': {u'denny'}, 'synonyms': {u'denise'}},
            u'netty': {
                'chunks': [],
                'synonyms_en': {u'annie', u'netta', u'annetta', u'nettie'},
                'synonyms': {u'annette'},
            },
            u'annie': {
                'chunks': [],
                'synonyms_en': {u'netty', u'nance', u'nancy',
                                u'netta', u'anne', u'ann', u'nettie', u'annetta'},
                'synonyms': {u'anna', u'annette'},
            },
            u'rori': {'chunks': [], 'synonyms_en': set(), 'synonyms': {u'aurora'}},
            u'nance': {
                'chunks': [],
                'synonyms_en': {u'annie', u'nancy', u'anne', u'ann'},
                'synonyms': {u'anna'},
            },
            u'denny': {'chunks': [], 'synonyms_en': {u'denice'}, 'synonyms': {u'denise'}},
            u'denise': {'chunks': [], 'synonyms_en': {u'denice', u'denny'}, 'synonyms': set()},
            u'april': {'chunks': [], 'synonyms_en': set(), 'synonyms': set()},
            u'aurora': {'chunks': [], 'synonyms_en': {u'rori'}, 'synonyms': set()},
            u'nancy': {
                'chunks': [],
                'synonyms_en': {u'annie', u'nance', u'anne', u'ann'},
                'synonyms': {u'anna'},
            },
            u'annette': {
                'chunks': [],
                'synonyms_en': {u'netta', u'nettie', u'annie', u'netty', u'annetta'},
                'synonyms': set(),
            },
            u'netta': {
                'chunks': [],
                'synonyms_en': {u'netty', u'annie', u'annetta', u'nettie'},
                'synonyms': {u'annette'},
            },
            u'anne': {
                'chunks': [],
                'synonyms_en': {u'annie', u'nance', u'nancy', u'ann'},
                'synonyms': {u'anna'},
            },
            u'annetta': {
                'chunks': [],
                'synonyms_en': {u'netty', u'annie', u'netta', u'nettie'},
                'synonyms': {u'annette'},
            },
            u'ann': {
                'chunks': [],
                'synonyms_en': {u'annie', u'nance', u'nancy', u'anne'},
                'synonyms': {u'anna'},
            },
            u'anna': {
                'chunks': [],
                'synonyms_en': {u'annie', u'nance', u'ann', u'nancy', u'anne'},
                'synonyms': set(),
            },
            u'nettie': {
                'chunks': [],
                'synonyms_en': {u'netty', u'annie', u'netta', u'annetta'},
                'synonyms': {u'annette'},
            },
        },
        'tr': {},
    },
}

LOADED_RULES = {
    'ru': {
        u'0': [{'pattern': u'0т', 'replacements': [{'factor': 1.0, 'replacement': u'0'}], 'characters': u'0т'}],
        u'б': [{'pattern': u'б', 'replacements': [{'factor': 1.0, 'replacement': u'b'}], 'characters': u'б'}],
        u'а': [{'pattern': u'а', 'replacements': [{'factor': 1.0, 'replacement': u'a'}], 'characters': u'а'}],
        u'г': [{'pattern': u'г', 'replacements': [{'factor': 1.0, 'replacement': u'g'}], 'characters': u'г'}],
        u'в': [
            {'pattern': u'^в', 'replacements': [{'factor': 1.0, 'replacement': u'v'}], 'characters': u'в'},
            {'pattern': u'в', 'replacements': [
                {'factor': 1.0, 'replacement': u'v'},
                {'factor': 0.98, 'replacement': u'w'},
            ], 'characters': u'в'},
        ],
        u'е': [
            {'pattern': u'^ев', 'replacements': [
                {'factor': 1.0, 'replacement': u'ev'},
                {'factor': 0.98, 'replacement': u'eu'},
                {'factor': 0.96, 'replacement': u'ew'},
            ], 'characters': u'ев'},
            {'pattern': u'ев$', 'replacements': [
                {'factor': 1.0, 'replacement': u'ev'},
                {'factor': 0.98, 'replacement': u'eff'},
                {'factor': 0.96, 'replacement': u'ew'},
            ], 'characters': u'ев'},
            {'pattern': u'^ек', 'replacements': [
                {'factor': 1.0, 'replacement': u'ek'},
                {'factor': 0.98, 'replacement': u'yek'},
            ], 'characters': u'ек'},
            {'pattern': u'е', 'replacements': [
                {'factor': 1.0, 'replacement': u'e'},
            ], 'characters': u'е'}],
        u'д': [
            {'pattern': u'дж', 'replacements': [
                {'factor': 1.0, 'replacement': u'j'},
                {'factor': 0.98, 'replacement': u'dj'},
                {'factor': 0.96, 'replacement': u'dzh'},
            ], 'characters': u'дж'},
            {'pattern': u'др$', 'replacements': [
                {'factor': 1.0, 'replacement': u'der'},
                {'factor': 0.98, 'replacement': u'dr'},
            ], 'characters': u'др'},
            {'pattern': u'д', 'replacements': [
                {'factor': 1.0, 'replacement': u'd'},
            ], 'characters': u'д'},
        ],
        u'з': [
            {'pattern': u'з', 'replacements': [
                {'factor': 1.0, 'replacement': u'z'},
            ], 'characters': u'з'},
        ],
        u'ж': [
            {'pattern': u'ж', 'replacements': [
                {'factor': 1.0, 'replacement': u'zh'},
                {'factor': 0.98, 'replacement': u'j'},
            ], 'characters': u'ж'},
        ],
        u'й': [
            {'pattern': u'й', 'replacements': [
                {'factor': 1.0, 'replacement': u'i'},
                {'factor': 0.98, 'replacement': u'j'},
                {'factor': 0.96, 'replacement': u'y'},
            ], 'characters': u'й'},
        ],
        u'и': [
            {'pattern': u'ий$', 'replacements': [
                {'factor': 1.0, 'replacement': u'y'},
                {'factor': 0.98, 'replacement': u'ij'},
            ], 'characters': u'ий'},
            {'pattern': u'ия', 'replacements': [
                {'factor': 1.0, 'replacement': u'ia'},
                {'factor': 0.98, 'replacement': u'ya'},
                {'factor': 0.96, 'replacement': u'iya'},
                {'factor': 0.94, 'replacement': u'ija'},
            ], 'characters': u'ия'},
            {'pattern': u'и', 'replacements': [
                {'factor': 1.0, 'replacement': u'i'},
            ], 'characters': u'и'},
        ],
        u'л': [
            {'pattern': u'л', 'replacements': [
                {'factor': 1.0, 'replacement': u'l'},
            ], 'characters': u'л'},
        ],
        u'к': [
            {'pattern': u'кв', 'replacements': [
                {'factor': 1.0, 'replacement': u'kv'},
                {'factor': 0.98, 'replacement': u'kw'},
                {'factor': 0.96, 'replacement': u'qu'},
            ], 'characters': u'кв'},
            {'pattern': u'ксю', 'replacements': [
                {'factor': 1.0, 'replacement': u'xiu'},
                {'factor': 0.98, 'replacement': u'ksu'},
                {'factor': 0.96, 'replacement': u'ksju'},
            ], 'characters': u'ксю'},
            {'pattern': u'кс', 'replacements': [
                {'factor': 1.0, 'replacement': u'x'},
                {'factor': 0.98, 'replacement': u'ks'},
            ], 'characters': u'кс'},
            {'pattern': u'к[бвгджзйклмнпрстфхцчшщғқңһbcdfghjklmnpqrstvwxz]', 'replacements': [
                {'factor': 1.0, 'replacement': u'k'},
                {'factor': 0.98, 'replacement': u'c'},
            ], 'characters': u'к'},
            {'pattern': u'^ке', 'replacements': [
                {'factor': 1.0, 'replacement': u'ke'},
            ], 'characters': u'ке'},
            {'pattern': u'^ки', 'replacements': [
                {'factor': 1.0, 'replacement': u'ki'},
            ], 'characters': u'ки'},
            {'pattern': u'^к', 'replacements': [
                {'factor': 1.0, 'replacement': u'k'},
                {'factor': 0.98, 'replacement': u'c'},
            ], 'characters': u'к'},
            {'pattern': u'к', 'replacements': [
                {'factor': 1.0, 'replacement': u'k'},
                {'factor': 0.98, 'replacement': u'ck'},
            ], 'characters': u'к'}],
        u'н': [{'pattern': u'н', 'replacements': [{'factor': 1.0, 'replacement': u'n'}], 'characters': u'н'}],
        u'м': [{'pattern': u'м', 'replacements': [{'factor': 1.0, 'replacement': u'm'}], 'characters': u'м'}],
        u'п': [{'pattern': u'п', 'replacements': [{'factor': 1.0, 'replacement': u'p'}], 'characters': u'п'}],
        u'о': [
            {'pattern': u'ов$', 'replacements': [
                {'factor': 1.0, 'replacement': u'ov'},
                {'factor': 0.98, 'replacement': u'off'},
                {'factor': 0.96, 'replacement': u'ow'},
            ], 'characters': u'ов'},
            {'pattern': u'о', 'replacements': [
                {'factor': 1.0, 'replacement': u'o'},
            ], 'characters': u'о'},
        ],
        u'с': [
            {'pattern': u'с', 'replacements': [
                {'factor': 1.0, 'replacement': u's'},
            ], 'characters': u'с'},
        ],
        u'р': [
            {'pattern': u'р', 'replacements': [
                {'factor': 1.0, 'replacement': u'r'},
            ], 'characters': u'р'},
        ],
        u'у': [
            {'pattern': u'у', 'replacements': [
                {'factor': 1.0, 'replacement': u'u'},
            ], 'characters': u'у'},
        ],
        u'т': [
            {'pattern': u'тр$', 'replacements': [
                {'factor': 1.0, 'replacement': u'ter'},
                {'factor': 0.98, 'replacement': u'tr'},
            ], 'characters': u'тр'},
            {'pattern': u'т', 'replacements': [
                {'factor': 1.0, 'replacement': u't'},
            ], 'characters': u'т'},
        ],
        u'х': [
            {'pattern': u'х', 'replacements': [
                {'factor': 1.0, 'replacement': u'h'},
                {'factor': 0.98, 'replacement': u'kh'},
                {'factor': 0.96, 'replacement': u'x'},
            ], 'characters': u'х'},
        ],
        u'ф': [{'pattern': u'ф', 'replacements': [{'factor': 1.0, 'replacement': u'f'}], 'characters': u'ф'}],
        u'ч': [
            {'pattern': u'^ч', 'replacements': [
                {'factor': 1.0, 'replacement': u'tch'},
                {'factor': 0.98, 'replacement': u'ch'},
            ], 'characters': u'ч'},
            {'pattern': u'ч$', 'replacements': [
                {'factor': 1.0, 'replacement': u'tch'},
                {'factor': 0.98, 'replacement': u'ch'},
                {'factor': 0.96, 'replacement': u'4'},
            ], 'characters': u'ч'},
            {'pattern': u'ч', 'replacements': [
                {'factor': 1.0, 'replacement': u'ch'},
                {'factor': 0.98, 'replacement': u'4'},
            ], 'characters': u'ч'},
        ],
        u'ц': [
            {'pattern': u'ц', 'replacements': [
                {'factor': 1.0, 'replacement': u'ts'},
                {'factor': 0.98, 'replacement': u'tz'},
                {'factor': 0.96, 'replacement': u'cz'},
            ], 'characters': u'ц'},
        ],
        u'щ': [
            {'pattern': u'щ', 'replacements': [
                {'factor': 1.0, 'replacement': u'sh'},
                {'factor': 0.98, 'replacement': u'sch'},
            ], 'characters': u'щ'},
        ],
        u'ш': [
            {'pattern': u'ш', 'replacements': [
                {'factor': 1.0, 'replacement': u'sh'},
                {'factor': 0.98, 'replacement': u'sch'},
            ], 'characters': u'ш'},
        ],
        u'ы': [
            {'pattern': u'ый$', 'replacements': [
                {'factor': 1.0, 'replacement': u'iy'},
                {'factor': 0.98, 'replacement': u'y'},
                {'factor': 0.96, 'replacement': u'yj'},
                {'factor': 0.94, 'replacement': u'ii'},
            ], 'characters': u'ый'},
            {'pattern': u'ы', 'replacements': [
                {'factor': 1.0, 'replacement': u'y'},
                {'factor': 0.98, 'replacement': u'i'},
            ], 'characters': u'ы'},
        ],
        u'ъ': [
            {'pattern': u'ъи', 'replacements': [
                {'factor': 1.0, 'replacement': u'ji'},
            ], 'characters': u'ъи'},
            {'pattern': u'ъе', 'replacements': [
                {'factor': 1.0, 'replacement': u'je'},
                {'factor': 0.98, 'replacement': u'ie'},
            ], 'characters': u'ъе'},
            {'pattern': u'ъю', 'replacements': [
                {'factor': 1.0, 'replacement': u'ju'},
                {'factor': 0.98, 'replacement': u'iu'},
            ], 'characters': u'ъю'},
            {'pattern': u'ъ', 'replacements': [], 'characters': u'ъ'},
        ],
        u'э': [
            {'pattern': u'э', 'replacements': [
                {'factor': 1.0, 'replacement': u'e'},
            ], 'characters': u'э'},
        ],
        u'ь': [
            {'pattern': u'ьи', 'replacements': [
                {'factor': 1.0, 'replacement': u'ji'},
                {'factor': 0.98, 'replacement': u'yi'},
            ], 'characters': u'ьи'},
            {'pattern': u'ье', 'replacements': [
                {'factor': 1.0, 'replacement': u'je'},
                {'factor': 0.98, 'replacement': u'ie'},
            ], 'characters': u'ье'},
            {'pattern': u'ью', 'replacements': [
                {'factor': 1.0, 'replacement': u'ju'},
                {'factor': 0.98, 'replacement': u'iu'},
            ], 'characters': u'ью'},
            {'pattern': u'ь', 'replacements': [], 'characters': u'ь'},
        ],
        u'я': [
            {'pattern': u'[бвгджзйклмнпрстфхцчшщғқңһbcdfghjklmnpqrstvwxz]я', 'replacements': [
                {'factor': 1.0, 'replacement': u'ya'},
                {'factor': 0.98, 'replacement': u'ia'},
            ], 'characters': u'я'},
            {'pattern': u'я', 'replacements': [
                {'factor': 1.0, 'replacement': u'ya'},
                {'factor': 0.98, 'replacement': u'ja'},
                {'factor': 0.96, 'replacement': u'ia'},
            ], 'characters': u'я'},
        ],
        u'ю': [
            {'pattern': u'^ю', 'replacements': [
                {'factor': 1.0, 'replacement': u'yu'},
                {'factor': 0.98, 'replacement': u'iu'},
            ], 'characters': u'ю'},
            {'pattern': u'ю', 'replacements': [
                {'factor': 1.0, 'replacement': u'yu'},
                {'factor': 0.98, 'replacement': u'iu'},
                {'factor': 0.96, 'replacement': u'u'},
            ], 'characters': u'ю'},
        ],
        u'ё': [
            {'pattern': u'ё', 'replacements': [
                {'factor': 1.0, 'replacement': u'yo'},
                {'factor': 0.98, 'replacement': u'io'},
                {'factor': 0.96, 'replacement': u'eo'},
            ], 'characters': u'ё'},
        ],
    },
    'en': {},
    'tr': {
        u'\xe7': [{'pattern': u'\xe7', 'replacements': [{'factor': 1.0, 'replacement': u'ch'}], 'characters': u'\xe7'}],
        u'ı': [{'pattern': u'ı', 'replacements': [{'factor': 1.0, 'replacement': u'i'}], 'characters': u'ı'}],
        u's': [
            {'pattern': u's', 'replacements': [
                {'factor': 1.0, 'replacement': u's'},
                {'factor': 0.98, 'replacement': u'sh'},
            ], 'characters': u's'},
        ],
        u'ş': [
            {'pattern': u'ş', 'replacements': [
                {'factor': 1.0, 'replacement': u'sh'},
                {'factor': 0.98, 'replacement': u's'},
            ], 'characters': u'ş'},
        ],
        u'\xf6': [
            {'pattern': u'\xf6', 'replacements': [
                {'factor': 1.0, 'replacement': u'o'},
            ], 'characters': u'\xf6'},
        ],
        u'\xfc': [{'pattern': u'\xfc', 'replacements': [
            {'factor': 1.0, 'replacement': u'u'},
        ], 'characters': u'\xfc'}],
        u'ğ': [{'pattern': u'ğ', 'replacements': [{'factor': 1.0, 'replacement': u'g'}], 'characters': u'ğ'}],
    },
}

LANG_TO_MIXES = {
    'ru': [
        {
            'factor': 1.0,
            'limit': 1,
            'params': ['login_synonym'],
            'separator': False,
            'validator': None,
        },
        {
            'factor': 1.0,
            'limit': 2,
            'params': ['surname_synonym'],
            'separator': False,
            'validator': None
        },
        {
            'factor': 1.0,
            'limit': 4,
            'params': ['surname_synonym', 'name_synonym'],
            'separator': False,
            'validator': None,
        },
        {
            'factor': 1.0,
            'limit': 4,
            'params': ['name_synonym', 'surname_synonym'],
            'separator': False,
            'validator': None,
        },

        {
            'factor': 0.98,
            'limit': 1,
            'params': ['login_synonym', 'surname_synonym'],
            'separator': False,
            'validator': 'string_ne_transliteration',
        },
        {
            'factor': 0.98,
            'limit': 2,
            'params': ['surname_synonym', 'login_synonym'],
            'separator': False,
            'validator': 'transliteration_ne_string',
        },

        {
            'factor': 0.97,
            'limit': 1,
            'params': ['surname_synonym', 'login_number'],
            'separator': False,
            'validator': 'transliteration_ne_wonumber',
        },

        {
            'factor': 0.96,
            'limit': 3,
            'params': ['name_synonym'],
            'separator': False,
            'validator': None,
        },
        {
            'factor': 0.96,
            'limit': 2,
            'params': ['surname_synonym', 'login_wo_number'],
            'separator': False,
            'validator': 'transliteration_ne_string',
        },
        {
            'factor': 0.96,
            'limit': 1,
            'params': ['login_wo_number', 'surname_synonym'],
            'separator': False,
            'validator': 'string_ne_transliteration',
        },

        {
            'factor': 0.95,
            'limit': 1,
            'params': ['login_wo_number'],
            'separator': False,
            'validator': None,
        },

        {
            'factor': 0.94,
            'limit': 1,
            'params': ['login_number'],
            'separator': False,
            'validator': None,
        },
        {
            'factor': 0.94,
            'limit': 4,
            'params': ['name_chunk', 'surname_synonym'],
            'separator': False,
            'validator': None,
        },
        {
            'factor': 0.94,
            'limit': 1,
            'params': ['name_synonym', 'surname_synonym'],
            'separator': True,
            'validator': None,
        },
        {
            'factor': 0.94,
            'limit': 1,
            'params': ['surname_synonym', 'name_synonym'],
            'separator': True,
            'validator': None,
        },

        {
            'factor': 0.93,
            'limit': 4,
            'params': ['surname_synonym', 'name_chunk'],
            'separator': False,
            'validator': None,
        },

        {
            'factor': 0.91,
            'limit': 2,
            'params': ['name_synonym', 'login_synonym'],
            'separator': False,
            'validator': 'transliteration_ne_string',
        },
        {
            'factor': 0.91,
            'limit': 1,
            'params': ['name_synonym', 'login_number'],
            'separator': False,
            'validator': 'transliteration_ne_wonumber',
        },
        {
            'factor': 0.91,
            'limit': 2,
            'params': ['name_synonym', 'login_wo_number'],
            'separator': False,
            'validator': 'transliteration_ne_string',
        },
        {
            'factor': 0.92,
            'params': ['prefix', 'login_synonym'],
            'limit': 2,
            'separator': True,
            'validator': False,
        },
    ],
    'en': [
        {
            'factor': 1.0,
            'params': ['login_synonym'],
            'limit': 1,
            'separator': False,
            'validator': None,
        },
        {
            'factor': 1.0,
            'params': ['surname_synonym'],
            'limit': 2,
            'separator': False,
            'validator': None,
        },
        {
            'factor': 1.0,
            'params': ['name_synonym', 'surname_synonym'],
            'limit': 5,
            'separator': False,
            'validator': None,
        },
        {
            'factor': 1.0,
            'params': ['name_chunk', 'surname_synonym'],
            'limit': 2,
            'separator': True,
            'validator': None,
        },

        {
            'factor': 0.98,
            'params': ['login_synonym', 'surname_synonym'],
            'limit': 1,
            'separator': False,
            'validator': 'string_ne_transliteration',
        },
        {
            'factor': 0.98,
            'params': ['login_synonym', 'name_synonym'],
            'limit': 1,
            'separator': False,
            'validator': 'string_ne_transliteration',
        },
        {
            'factor': 0.98,
            'params': ['surname_synonym', 'login_synonym'],
            'limit': 2,
            'separator': False,
            'validator': 'transliteration_ne_string',
        },
        {
            'factor': 0.98,
            'params': ['name_chunk', 'surname_synonym'],
            'limit': 4,
            'separator': False,
            'validator': None,
        },

        {
            'factor': 0.96,
            'params': ['name_synonym'],
            'limit': 4,
            'separator': False,
            'validator': None,
        },
        {
            'factor': 0.96,
            'params': ['surname_synonym', 'login_wo_number'],
            'limit': 2,
            'separator': False,
            'validator': 'transliteration_ne_string',
        },
        {
            'factor': 0.96,
            'params': ['login_wo_number', 'surname_synonym'],
            'limit': 1,
            'separator': False,
            'validator': 'string_ne_transliteration',
        },

        {
            'factor': 0.95,
            'params': ['login_wo_number'],
            'limit': 1,
            'separator': False,
            'validator': None,
        },

        {
            'factor': 0.94,
            'params': ['login_number'],
            'limit': 1,
            'separator': False,
            'validator': None,
        },
        {
            'factor': 0.94,
            'params': ['name_synonym', 'surname_synonym'],
            'limit': 2,
            'separator': True,
            'validator': None,
        },

        {
            'factor': 0.91,
            'params': ['name_synonym', 'login_synonym'],
            'limit': 2,
            'separator': False,
            'validator': 'transliteration_ne_string',
        },
        {
            'factor': 0.91,
            'params': ['name_synonym', 'login_wo_number'],
            'limit': 2,
            'separator': False,
            'validator': 'transliteration_ne_string',
        },

        {
            'factor': 0.92,
            'params': ['prefix', 'login_synonym'],
            'limit': 2,
            'separator': True,
            'validator': False,
        },
    ],
}

TEST_LOGIN_PREFIXES = ['ya']

LETTER_TO_NUMBER_REPLACEMENTS = {
    'e': [
        {
            'replacements': [
                {'replacement': 'e', 'factor': 1.0},
                {'replacement': '3', 'factor': 0.9},
            ],
            'pattern': 'e',
            'characters': 'e',
        },
    ],
    'i': [
        {
            'replacements': [
                {'replacement': 'i', 'factor': 1.0},
                {'replacement': '1', 'factor': 0.9},
            ],
            'pattern': 'i',
            'characters': 'i',
        },
    ],
}

LETTER_TO_NUMBER_REPLACEMENTS_KEYS = set(LETTER_TO_NUMBER_REPLACEMENTS.keys())

PREFIX_WEIGHT = 96
