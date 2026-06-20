export const DISTRICTS = [
  "Bajali", "Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar",
  "Charaideo", "Chirang", "Darrang", "Dhemaji", "Dhubri", "Dibrugarh",
  "Dima Hasao", "Goalpara", "Golaghat", "Hailakandi", "Hojai", "Jorhat",
  "Kamrup", "Kamrup Metropolitan", "Karbi Anglong", "Karimganj",
  "Kokrajhar", "Lakhimpur", "Majuli", "Morigaon", "Nagaon", "Nalbari",
  "Sivasagar", "Sonitpur", "South Salmara-Mankachar", "Tamulpur",
  "Tinsukia", "Udalguri", "West Karbi Anglong",
];

export const CATEGORIES = [
  { key: 'govt', label: 'Government' },
  { key: 'private', label: 'Private' },
  { key: 'defence', label: 'Defence' },
  { key: 'banking', label: 'Banking' },
  { key: 'railway', label: 'Railway' },
  { key: 'teaching', label: 'Teaching' },
  { key: 'police', label: 'Police' },
];

// Public-facing sections — each routes to a single ListPage filtered by `type`.
export const SECTIONS = [
  { key: 'job', label: 'Jobs', path: '/jobs', plural: 'Job Notifications' },
  { key: 'admit_card', label: 'Admit Card', path: '/admit-card', plural: 'Admit Cards' },
  { key: 'result', label: 'Result', path: '/result', plural: 'Results' },
  { key: 'answer_key', label: 'Answer Key', path: '/answer-key', plural: 'Answer Keys' },
];

export const SECTION_BY_TYPE = Object.fromEntries(SECTIONS.map(s => [s.key, s]));
