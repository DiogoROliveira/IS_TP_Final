<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:output method="xml" indent="yes"/>
    <xsl:template match="/">
        <root>
                <xsl:for-each select="//Airport_Code[(type='large_airport' or type='medium_airport') and (continent='EU' or continent='NA')]">
                    <xsl:copy-of select="."/>
                </xsl:for-each>
        </root>
    </xsl:template>
</xsl:stylesheet>
