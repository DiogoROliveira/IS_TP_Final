<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="yes"/>
    
    <xsl:template match="/">
      <root>
        <xsl:for-each-group select="//Temp" group-by="Region">
                <xsl:copy-of select="."/>
        </xsl:for-each-group>
      </root>
    </xsl:template>
</xsl:stylesheet>
