<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="2.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:output method="html" indent="yes" encoding="utf-8"/>
    <xsl:strip-space elements="*"/>

    <xsl:template match="/">
        <html>
            <body>
                <div>
                    Found <xsl:value-of select="MessagePage/count"/> changed links.
                </div>
                <div>
                    All changed links <a href="http://portal.haze.yandex.net/#/links/list?show=new,notblocked">here</a>
                </div>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>