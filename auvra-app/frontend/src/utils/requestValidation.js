// Client-side preflight validation to catch issues before submitting to API

const allowed = {
  period_pattern: new Set(['regular', 'irregular', 'occasional_skips', 'no_periods', 'not_sure']),
  birth_control: new Set(['hormonal_pills', 'hormonal_iud', 'copper_iud', 'none']),
  cycle_length: new Set(['<21', '21-25', '26-30', '31-35', '35+', 'not_sure']),
  period: new Set(['irregular_periods', 'painful_periods', 'light_periods', 'heavy_periods']),
  body: new Set(['bloating', 'hot_flashes', 'nausea', 'weight_difficulty', 'recent_weight_gain', 'menstrual_headaches']),
  skin_hair: new Set(['hirsutism', 'hair_thinning', 'adult_acne']),
  mental: new Set(['mood_swings', 'stress', 'fatigue']),
  diagnoses: new Set(['pcos','pcod','endometriosis','dysmenorrhea','amenorrhea','menorrhagia','metrorrhagia','pms','pmdd','hashimotos','hypothyroidism'])
};

export function validateRequest(data) {
  const errors = [];

  // Basic Info
  if (!data?.basic_info?.name || String(data.basic_info.name).trim().length === 0) {
    errors.push({ field: 'basic_info.name', message: 'Name is required' });
  }
  const age = Number(data?.basic_info?.age);
  if (!Number.isInteger(age) || age < 18 || age > 40) {
    errors.push({ field: 'basic_info.age', message: 'Age must be between 18 and 40' });
  }

  // Period Pattern
  const pp = data?.period_pattern?.period_pattern;
  if (!allowed.period_pattern.has(pp)) {
    errors.push({ field: 'period_pattern.period_pattern', message: 'Select a valid period pattern' });
  }
  const bc = data?.period_pattern?.birth_control;
  if (!allowed.birth_control.has(bc)) {
    errors.push({ field: 'period_pattern.birth_control', message: 'Choose a valid birth control option' });
  }

  // Cycle Details
  const cl = data?.cycle_details?.cycle_length;
  if (!allowed.cycle_length.has(cl)) {
    errors.push({ field: 'cycle_details.cycle_length', message: 'Choose a valid cycle length' });
  }

  // Health Concerns arrays must be subsets of allowed
  const checkSubset = (arr, set, field) => {
    if (!Array.isArray(arr)) return;
    for (const item of arr) if (!set.has(item)) errors.push({ field, message: `Invalid value: ${item}` });
  };
  checkSubset(data?.health_concerns?.period_concerns, allowed.period, 'health_concerns.period_concerns');
  checkSubset(data?.health_concerns?.body_concerns, allowed.body, 'health_concerns.body_concerns');
  checkSubset(data?.health_concerns?.skin_hair_concerns, allowed.skin_hair, 'health_concerns.skin_hair_concerns');
  checkSubset(data?.health_concerns?.mental_health_concerns, allowed.mental, 'health_concerns.mental_health_concerns');

  // Diagnoses
  if (Array.isArray(data?.diagnosed_conditions?.conditions)) {
    for (const d of data.diagnosed_conditions.conditions) {
      if (!allowed.diagnoses.has(d)) errors.push({ field: 'diagnosed_conditions.conditions', message: `Invalid diagnosis: ${d}` });
    }
  }

  return { ok: errors.length === 0, errors };
}
