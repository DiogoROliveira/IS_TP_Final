<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <!-- Output method as XML -->
  <xsl:output method="xml" indent="yes"/>
  
  <!-- Identity template to copy all nodes by default -->
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>
  
  <!-- Main template to filter and transform the root element -->
  <xsl:template match="/root">
    <filtered-temperatures>
      <!-- 1. Filter by specific region -->
      <xsl:for-each select="Temp[Region='North America']">
        <north-america-temp>
          <xsl:copy-of select="*"/>
        </north-america-temp>
      </xsl:for-each>
      
      <!-- 2. Filter temperatures above a certain threshold -->
      <high-temperatures>
        <xsl:for-each select="Temp[AvgTemperature > 25]">
          <hot-location>
            <xsl:copy-of select="*"/>
          </hot-location>
        </xsl:for-each>
      </high-temperatures>
      
      <!-- 3. Filter by specific year -->
      <temps-by-year>
        <xsl:for-each select="Temp[Year = 2023]">
          <recent-temp>
            <xsl:copy-of select="*"/>
          </recent-temp>
        </xsl:for-each>
      </temps-by-year>
      
      <!-- 4. Aggregate statistics -->
      <temperature-summary>
        <total-records>
          <xsl:value-of select="count(Temp)"/>
        </total-records>
        <average-global-temp>
          <xsl:value-of select="format-number(sum(Temp/AvgTemperature) div count(Temp), '0.00')"/>
        </average-global-temp>
      </temperature-summary>
    </filtered-temperatures>
  </xsl:template>
</xsl:stylesheet>
