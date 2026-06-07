// ─── Test IP Intelligence Report Formatter ──────────────────────────
const { generateIntelligenceReport } = require('./formatter.js');

// Mock Transform & Derive output (simulating what the Code node produces)
const sampleData = {
  chatId: 12345,
  ip: '3.95.197.167',
  verified: {
    ip: '3.95.197.167',
    hostname: 'ec2-3-95-197-167.compute-1.amazonaws.com',
    ipVersion: 'IPv4',
    asn: 'AS14618',
    isp: 'Amazon.com Inc.',
    organization: 'Amazon Web Services',
    organizationType: 'business',
    country: 'United States',
    countryCode: 'US',
    region: 'Virginia',
    regionCode: 'VA',
    city: 'Ashburn',
    zip: '20149',
    latitude: 39.0438,
    longitude: -77.4879,
    capital: 'Washington D.C.',
    continent: 'North America',
    continentCode: 'NA',
    countryFlag: '🇺🇸',
    callingCode: '+1',
    isEu: 'No',
    timezoneId: 'America/New_York',
    currentTime: '2026-06-08T14:30:00-04:00',
    utcOffset: '-04:00',
    dstEnabled: 'Yes',
    currencyName: 'US Dollar',
    currencyCode: 'USD',
    currencySymbol: '$',
    languageName: 'English',
    languageCode: 'en',
    languageNative: 'English',
    proxy: 'No',
    proxyType: 'N/A',
    tor: 'No',
    crawler: 'No',
    crawlerType: 'N/A',
    threatLevel: 'low',
    threatTypes: 'None',
    vpn: 'No',
    hosting: 'Yes',
    anonymizer: 'No'
  },
  derived: {
    cloudProvider: 'Amazon Web Services (AWS)',
    networkCategory: 'Hosting / Cloud Infrastructure',
    northernHemisphere: 'Northern Hemisphere',
    easternHemisphere: 'Western Hemisphere',
    googleMapsUrl: 'https://www.google.com/maps?q=39.0438,-77.4879',
    osmUrl: 'https://www.openstreetmap.org/?mlat=39.0438&mlon=-77.4879',
    localTime: '02:30:00 PM',
    localDate: 'Monday, June 8, 2026',
    businessHours: 'Active Business Hours',
    businessIcon: '🟢',
    utcFormat: 'Mon, 08 Jun 2026 18:30:00 GMT',
    gmtFormat: '2026-06-08T18:30:00.000+00:00',
    riskScore: 10,
    riskFactors: ['No risk indicators detected'],
    threatMeter: '🟩⬜⬜⬜⬜⬜⬜⬜⬜⬜',
    riskClassification: 'Low Risk',
    riskEmoji: '🟢',
    trustRating: 'Trusted'
  },
  // Mock enrichment data (merged from parallel branches)
  current: {
    temperature_2m: 24.5,
    relative_humidity_2m: 55,
    wind_speed_10m: 12.3
  },
  results: {
    sunrise: '2026-06-08T10:45:00-04:00',
    sunset: '2026-06-08T20:35:00-04:00'
  }
};

// Generate and print the report
const report = generateIntelligenceReport(sampleData);
console.log(report);
console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('Report length: ' + report.length + ' characters');
console.log('Telegram limit: 4096 characters');
console.log('Status: ' + (report.length <= 4096 ? '✅ Within limit' : '❌ Exceeds limit'));
