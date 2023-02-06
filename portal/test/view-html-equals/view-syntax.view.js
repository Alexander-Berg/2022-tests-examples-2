views('news',
    '<div class="news"[% bem:attrs %]>[% jpath:news.text %]</div>'
);

views('news__layout',
    '<div class="[% bem:news.class %]">[% l10n:title %]</div>'
);

views('news__footer',
    '[% news__first %]<div class="news__footer">[% news__second %]</div>[% news__third %]'
);
