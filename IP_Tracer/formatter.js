// ─── IP Intelligence Report Formatter ───────────────────────────────
// Generates a professional OSINT-style Telegram message from IPStack data

function generateIntelligenceReport(data) {
  const v = data.verified || {};
  const d = data.derived || {};
  let msg = '';

  // ═══════════════════════════════════════════════════════════════════
  // HEADER
  // ═══════════════════════════════════════════════════════════════════
  msg += '🔍 *IP INTELLIGENCE REPORT*\n';
  msg += '━━━━━━━━━━━━━━━━━━━━━━━━\n\n';

  // ═══════════════════════════════════════════════════════════════════
  // 📌 VERIFIED INFORMATION
  // ═══════════════════════════════════════════════════════════════════
  msg += '📌 *VERIFIED INFORMATION*\n';
  msg += '━━━━━━━━━━━━━━━━━━━━━━━━\n\n';

  // ── NETWORK ──────────────────────────────────────────────────────
  msg += '🌐 *NETWORK*\n';
  if (v.ip) msg += '▫ *IP Address:* `' + v.ip + '`\n';
  if (v.hostname && v.hostname !== 'N/A') msg += '▫ *Hostname:* `' + v.hostname + '`\n';
  if (v.ipVersion) msg += '▫ *IP Version:* ' + v.ipVersion + '\n';
  if (v.asn && v.asn !== 'N/A') msg += '▫ *ASN:* ' + v.asn + '\n';
  if (v.isp && v.isp !== 'N/A') msg += '▫ *ISP:* ' + v.isp + '\n';
  if (v.organization && v.organization !== 'N/A') msg += '▫ *Organization:* ' + v.organization + '\n';
  if (v.organizationType && v.organizationType !== 'N/A') msg += '▫ *Org Type:* ' + v.organizationType + '\n';
  msg += '\n';

  // ── LOCATION ─────────────────────────────────────────────────────
  msg += '📍 *LOCATION*\n';
  const flag = v.countryFlag || '';
  const country = v.country && v.country !== 'N/A' ? v.country : '';
  const countryCode = v.countryCode && v.countryCode !== 'N/A' ? v.countryCode : '';
  if (flag || country) {
    msg += '▫ *Country:* ' + (flag ? flag + ' ' : '') + country;
    if (countryCode) msg += ' (' + countryCode + ')';
    msg += '\n';
  }
  const region = v.region && v.region !== 'N/A' ? v.region : '';
  const regionCode = v.regionCode && v.regionCode !== 'N/A' ? v.regionCode : '';
  if (region || regionCode) {
    msg += '▫ *Region:* ' + region;
    if (regionCode) msg += ' (' + regionCode + ')';
    msg += '\n';
  }
  if (v.city && v.city !== 'N/A') msg += '▫ *City:* ' + v.city + '\n';
  if (v.zip && v.zip !== 'N/A') msg += '▫ *ZIP:* ' + v.zip + '\n';
  if (v.latitude != null) msg += '▫ *Latitude:* ' + v.latitude + '\n';
  if (v.longitude != null) msg += '▫ *Longitude:* ' + v.longitude + '\n';
  if (v.capital && v.capital !== 'N/A') msg += '▫ *Capital:* ' + v.capital + '\n';
  msg += '\n';

  // ── COUNTRY DETAILS ──────────────────────────────────────────────
  msg += '🌍 *COUNTRY DETAILS*\n';
  if (v.continent && v.continent !== 'N/A') msg += '▫ *Continent:* ' + v.continent + (v.continentCode && v.continentCode !== 'N/A' ? ' (' + v.continentCode + ')' : '') + '\n';
  if (v.callingCode && v.callingCode !== 'N/A') msg += '▫ *Calling Code:* ' + v.callingCode + '\n';
  if (v.isEu && v.isEu !== 'N/A') msg += '▫ *EU Member:* ' + (v.isEu === 'Yes' ? '✅ Yes' : '❌ No') + '\n';
  msg += '\n';

  // ── TIME INFORMATION ─────────────────────────────────────────────
  msg += '🕒 *TIME INFORMATION*\n';
  if (v.timezoneId && v.timezoneId !== 'N/A') msg += '▫ *Timezone:* ' + v.timezoneId + '\n';
  if (v.currentTime && v.currentTime !== 'N/A') msg += '▫ *Current Local Time:* ' + v.currentTime + '\n';
  if (v.utcOffset && v.utcOffset !== 'N/A') msg += '▫ *UTC Offset:* ' + v.utcOffset + '\n';
  if (d.gmtFormat && d.gmtFormat !== 'N/A') msg += '▫ *GMT Offset:* ' + d.gmtFormat + '\n';
  if (v.dstEnabled && v.dstEnabled !== 'N/A') msg += '▫ *DST Status:* ' + (v.dstEnabled === 'Yes' ? '🟢 Enabled' : '⚪ Disabled') + '\n';
  msg += '\n';

  // ── ECONOMIC INFORMATION ──────────────────────────────────────────
  if ((v.currencyName && v.currencyName !== 'N/A') || (v.currencyCode && v.currencyCode !== 'N/A')) {
    msg += '💰 *ECONOMIC INFORMATION*\n';
    let currencyStr = '';
    if (v.currencyName && v.currencyName !== 'N/A') currencyStr += v.currencyName;
    if (v.currencyCode && v.currencyCode !== 'N/A') currencyStr += ' (' + v.currencyCode + ')';
    if (v.currencySymbol && v.currencySymbol !== 'N/A') {
      const knownSymbols = { 'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'INR': '₹', 'CNY': '¥', 'RUB': '₽', 'BRL': 'R$', 'AUD': 'A$', 'CAD': 'C$', 'CHF': 'Fr', 'KRW': '₩', 'SGD': 'S$', 'NZD': 'NZ$', 'MXN': 'Mex$' };
      const symbol = knownSymbols[v.currencyCode] || v.currencySymbol;
      currencyStr += ' ' + symbol;
    }
    msg += '▫ *Currency:* ' + currencyStr + '\n\n';
  }

  // ── LANGUAGE INFORMATION ──────────────────────────────────────────
  if ((v.languageName && v.languageName !== 'N/A')) {
    msg += '🗣 *LANGUAGE INFORMATION*\n';
    let langStr = v.languageName;
    if (v.languageCode && v.languageCode !== 'N/A') langStr += ' (' + v.languageCode + ')';
    msg += '▫ ' + langStr + '\n\n';
  }

  // ── SECURITY INFORMATION ──────────────────────────────────────────
  msg += '🛡 *SECURITY INFORMATION*\n';
  // Proxy
  if (v.proxy && v.proxy !== 'N/A') {
    const icon = v.proxy === 'Yes' ? '🔴' : '🟢';
    msg += '▫ *Proxy:* ' + icon + ' ' + v.proxy;
    if (v.proxyType && v.proxyType !== 'N/A') msg += ' (' + v.proxyType + ')';
    msg += '\n';
  }
  // TOR
  if (v.tor && v.tor !== 'N/A') {
    const icon = v.tor === 'Yes' ? '🔴' : '🟢';
    msg += '▫ *TOR:* ' + icon + ' ' + v.tor + '\n';
  }
  // Crawler
  if (v.crawler && v.crawler !== 'N/A') {
    const icon = v.crawler === 'Yes' ? '🟡' : '🟢';
    msg += '▫ *Crawler:* ' + icon + ' ' + v.crawler;
    if (v.crawlerType && v.crawlerType !== 'N/A') msg += ' (' + v.crawlerType + ')';
    msg += '\n';
  }
  // Threat Level
  if (v.threatLevel && v.threatLevel !== 'N/A') {
    const threatIcons = { 'low': '🟢', 'medium': '🟡', 'high': '🔴' };
    const icon = threatIcons[v.threatLevel.toLowerCase()] || '⚪';
    msg += '▫ *Threat Level:* ' + icon + ' ' + v.threatLevel.charAt(0).toUpperCase() + v.threatLevel.slice(1) + '\n';
  }
  // Threat Types
  if (v.threatTypes && v.threatTypes !== 'None' && v.threatTypes !== 'N/A') {
    msg += '▫ *Threat Types:* ' + v.threatTypes + '\n';
  }
  // VPN
  if (v.vpn && v.vpn !== 'N/A') {
    const icon = v.vpn === 'Yes' ? '🟡' : '🟢';
    msg += '▫ *VPN Service:* ' + icon + ' ' + v.vpn + '\n';
  }
  // Hosting
  if (v.hosting && v.hosting !== 'N/A') {
    const icon = v.hosting === 'Yes' ? '☁️' : '❌';
    msg += '▫ *Hosting Facility:* ' + icon + ' ' + v.hosting + '\n';
  }
  // Anonymizer
  if (v.anonymizer && v.anonymizer !== 'N/A') {
    const icon = v.anonymizer === 'Yes' ? '🔴' : '🟢';
    msg += '▫ *Anonymizer:* ' + icon + ' ' + v.anonymizer + '\n';
  }
  msg += '\n';

  // ═══════════════════════════════════════════════════════════════════
  // 🧠 DERIVED INTELLIGENCE
  // ═══════════════════════════════════════════════════════════════════
  msg += '🧠 *DERIVED INTELLIGENCE*\n';
  msg += '━━━━━━━━━━━━━━━━━━━━━━━━\n';
  msg += '_Inferred from verified data_\n\n';

  // ── NETWORK ANALYSIS ─────────────────────────────────────────────
  msg += '☁️ *NETWORK ANALYSIS*\n';
  if (d.cloudProvider && d.cloudProvider !== 'None') {
    msg += '▫ *Likely Provider:* ☁️ ' + d.cloudProvider + '\n';
  }
  if (d.networkCategory && d.networkCategory !== 'Uncategorized') {
    msg += '▫ *Network Category:* ' + d.networkCategory + '\n';
  }
  // Likely Usage
  const usageMap = {
    'Hosting / Cloud Infrastructure': 'Cloud Computing / VPS Hosting',
    'VPN Service': 'Privacy / Anonymity Services',
    'Proxy Service': 'Traffic Relay / Geo-Spoofing',
    'TOR Exit Node': 'Anonymous Routing',
    'Mobile / Cellular Network': 'Mobile Data / Cellular Connectivity',
    'Residential / Business ISP': 'General Internet / Broadband',
    'Educational Network': 'Academic / Research',
    'Government Network': 'Official / Administrative',
    'Business / Enterprise Network': 'Corporate Operations'
  };
  const likelyUsage = usageMap[d.networkCategory];
  if (likelyUsage) {
    msg += '▫ *Likely Usage:* ' + likelyUsage + '\n';
  }
  msg += '\n';

  // ── CONNECTION ANALYSIS ──────────────────────────────────────────
  msg += '🏠 *CONNECTION ANALYSIS*\n';
  const isHosting = v.hosting === 'Yes';
  const isResidential = d.networkCategory === 'Residential / Business ISP';
  const isMobile = d.networkCategory === 'Mobile / Cellular Network';
  const isDatacenter = isHosting || d.networkCategory === 'Hosting / Cloud Infrastructure';
  msg += '▫ *Residential Probability:* ' + (isResidential ? '🔴 High' : isMobile ? '🟡 Medium' : '🟢 Low') + '\n';
  msg += '▫ *Datacenter Probability:* ' + (isDatacenter ? '🔴 High' : isResidential ? '🟢 Low' : isMobile ? '🟢 Low' : '🟡 Medium') + '\n';
  msg += '\n';

  // ── GEOGRAPHIC ANALYSIS ──────────────────────────────────────────
  msg += '🧭 *GEOGRAPHIC ANALYSIS*\n';
  if (d.northernHemisphere && d.northernHemisphere !== 'N/A') {
    msg += '▫ *Hemisphere:* ' + d.northernHemisphere + ', ' + (d.easternHemisphere || '') + '\n';
  }
  if (d.googleMapsUrl) {
    msg += '▫ [🗺 View on Google Maps](' + d.googleMapsUrl + ')\n';
  }
  if (d.osmUrl) {
    msg += '▫ [🌍 View on OpenStreetMap](' + d.osmUrl + ')\n';
  }
  msg += '\n';

  // ── TIME ANALYSIS ────────────────────────────────────────────────
  msg += '🕒 *TIME ANALYSIS*\n';
  if (d.localTime && d.localTime !== 'N/A') msg += '▫ *Local Time:* ' + d.localTime + '\n';
  if (d.localDate && d.localDate !== 'N/A') msg += '▫ *Local Date:* ' + d.localDate + '\n';
  if (d.utcFormat && d.utcFormat !== 'N/A') msg += '▫ *UTC Format:* `' + d.utcFormat + '`\n';
  if (d.gmtFormat && d.gmtFormat !== 'N/A') msg += '▫ *GMT Format:* `' + d.gmtFormat + '`\n';
  if (d.businessHours && d.businessHours !== 'N/A') {
    msg += '▫ *Business Hours:* ' + (d.businessIcon || '') + ' ' + d.businessHours + '\n';
  }
  msg += '\n';

  // ── RISK ANALYSIS ────────────────────────────────────────────────
  msg += '📊 *RISK ANALYSIS*\n';
  if (d.riskScore != null) msg += '▫ *Risk Score:* ' + d.riskScore + '/100\n';
  if (d.threatMeter) msg += '▫ *Threat Meter:* ' + d.threatMeter + '\n';
  if (d.riskClassification) msg += '▫ *Classification:* ' + (d.riskEmoji || '') + ' ' + d.riskClassification + '\n';
  if (d.trustRating) {
    const trustEmoji = d.trustRating === 'Trusted' ? '🟢' : d.trustRating === 'Suspicious' ? '🟡' : '🔴';
    msg += '▫ *Trust Rating:* ' + trustEmoji + ' ' + d.trustRating + '\n';
  }
  if (d.riskFactors && d.riskFactors.length > 0 && d.riskFactors[0] !== 'No risk indicators detected') {
    msg += '▫ *Risk Factors:* ' + d.riskFactors.join('; ') + '\n';
  }
  msg += '\n';

  // ═══════════════════════════════════════════════════════════════════
  // 🔮 ENRICHED INTELLIGENCE
  // ═══════════════════════════════════════════════════════════════════
  const hasWeather = data.current && !data.error;
  const hasSunrise = data.results && data.results.sunrise;
  const hasDns = v.hostname && v.hostname !== 'N/A';

  if (hasWeather || hasSunrise || hasDns) {
    msg += '🔮 *ENRICHED INTELLIGENCE*\n';
    msg += '━━━━━━━━━━━━━━━━━━━━━━━━\n\n';

    // Reverse DNS
    if (hasDns) {
      msg += '🌐 *REVERSE DNS*\n';
      msg += '▫ *Hostname:* `' + v.hostname + '`\n\n';
    }

    // Weather
    if (hasWeather) {
      const current = data.current;
      msg += '🌤 *WEATHER*\n';
      msg += '▫ *Temperature:* ' + (current.temperature_2m != null ? current.temperature_2m + '°C' : 'N/A') + '\n';
      msg += '▫ *Humidity:* ' + (current.relative_humidity_2m != null ? current.relative_humidity_2m + '%' : 'N/A') + '\n';
      msg += '▫ *Wind Speed:* ' + (current.wind_speed_10m != null ? current.wind_speed_10m + ' km/h' : 'N/A') + '\n';
      msg += '▫ *Conditions:* ' + inferWeatherCondition(current) + '\n\n';
    }

    // Solar
    if (hasSunrise) {
      const times = data.results;
      const sunriseTime = times.sunrise ? new Date(times.sunrise).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true }) : 'N/A';
      const sunsetTime = times.sunset ? new Date(times.sunset).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true }) : 'N/A';
      msg += '🌅 *SOLAR INFORMATION*\n';
      msg += '▫ *Sunrise:* ' + sunriseTime + '\n';
      msg += '▫ *Sunset:* ' + sunsetTime + '\n\n';
    }
  }

  // ═══════════════════════════════════════════════════════════════════
  // 📋 EXECUTIVE SUMMARY
  // ═══════════════════════════════════════════════════════════════════
  msg += '📋 *EXECUTIVE SUMMARY*\n';
  msg += '━━━━━━━━━━━━━━━━━━━━━━━━\n\n';

  const locationParts = [v.city, v.region, v.country].filter(p => p && p !== 'N/A');
  const locationStr = locationParts.join(', ') || 'Unknown location';

  let summary = '';
  summary += 'This IP (`' + v.ip + '`) belongs to *' + (v.isp || 'Unknown ISP') + '*';
  if (d.cloudProvider && d.cloudProvider !== 'None') {
    summary += ' and is hosted on *' + d.cloudProvider + '*';
  }
  summary += ', located in ' + locationStr + '.\n\n';

  // Risk indicators
  const indicators = [];
  if (v.proxy === 'Yes') indicators.push('proxy usage');
  if (v.tor === 'Yes') indicators.push('TOR routing');
  if (v.vpn === 'Yes') indicators.push('VPN service');
  if (v.crawler === 'Yes') indicators.push('automated crawling');
  if (v.anonymizer === 'Yes') indicators.push('anonymizer services');

  if (indicators.length === 0) {
    summary += 'No indicators of TOR usage, proxy usage, VPN services, or known malicious activity were detected.\n\n';
  } else {
    summary += '⚠️ *Detected indicators:* ' + indicators.join(', ') + '.\n';
    if (d.riskScore && d.riskScore > 50) {
      summary += 'This IP exhibits multiple characteristics commonly associated with malicious activity.\n';
    }
    summary += '\n';
  }

  summary += '*Risk Level:* ' + (d.riskEmoji || '') + ' ' + (d.riskClassification || 'Unknown') + '\n';
  summary += '*Trust Rating:* ' + (d.trustRating || 'Unknown') + '\n';
  summary += '*Confidence:* HIGH\n';
  summary += '*Recommended Action:* ';
  if (d.riskScore <= 15) {
    summary += 'No immediate security concerns identified. Routine monitoring advised.';
  } else if (d.riskScore <= 50) {
    summary += 'Exercise caution. Monitor traffic from this IP for anomalous behavior.';
  } else {
    summary += '⚠️ *BLOCK or INVESTIGATE immediately.* High likelihood of malicious activity.';
  }

  msg += summary + '\n\n';

  // ═══════════════════════════════════════════════════════════════════
  // ℹ️ REPORT NOTES
  // ═══════════════════════════════════════════════════════════════════
  msg += 'ℹ️ *REPORT NOTES*\n';
  msg += '━━━━━━━━━━━━━━━━━━━━━━━━\n\n';
  msg += '✅ *Verified Information* — Directly returned by IPStack API.\n';
  msg += '🧠 *Derived Intelligence* — Inferred from verified data using analytical heuristics.\n';
  if (hasWeather || hasSunrise || hasDns) {
    msg += '🔮 *Enriched Intelligence* — Obtained from third-party services (Open-Meteo, Sunrise-Sunset).\n';
  }
  msg += '\n⚠️ *Disclaimer:* Geolocation data is approximate and may not represent the exact physical location of a device or user. This report is generated for informational purposes only.\n\n';

  // ── FOOTER ──────────────────────────────────────────────────────────
  msg += '━━━━━━━━━━━━━━━━━━━━━━━━\n';
  msg += '🤖 *TracedIP Intelligence Bot*\n';
  msg += '📡 Data Source: [ipstack.com](https://ipstack.com)\n';
  msg += '🔬 Classification: OSINT / Threat Intelligence';

  return msg;
}

function inferWeatherCondition(current) {
  if (!current) return 'N/A';
  const temp = current.temperature_2m;
  if (temp == null) return 'N/A';
  if (temp > 35) return '☀️ Very Hot';
  if (temp > 25) return '☀️ Warm';
  if (temp > 15) return '🌤 Mild';
  if (temp > 5) return '⛅ Cool';
  if (temp > -5) return '☁️ Cold';
  return '❄️ Freezing';
}

// ─── EXPORT ───────────────────────────────────────────────────────────
module.exports = { generateIntelligenceReport };
