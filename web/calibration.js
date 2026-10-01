// These thresholds describe a visible 2D movement, not a medical range of motion.
export function calibratedCycle(base, start, end, feature) {
 if (!base || !Number.isFinite(start) || !Number.isFinite(end)) throw new Error('先记录清晰的起始和终点姿势');
 const distance = base.increasing ? end - start : start - end;
 const minimum = feature === 'jack' ? .12 : feature === 'curl' ? 8 : 12;
 if (distance < minimum) throw new Error('两次姿势的变化太小，或记录顺序相反；请调整机位并重新记录');
 const margin = feature === 'jack' ? Math.max(.015, Math.min(.05, distance * .12)) : Math.max(2, Math.min(7, distance * .12));
 const low = base.increasing ? start + margin : end + margin;
 const high = base.increasing ? end - margin : start - margin;
 return {...base, low, high, hysteresis: Math.min(base.hysteresis, (high - low) * .18), minimum_cycle: Math.max(base.minimum_cycle, .4)};
}

export function stableReading(samples, now, feature) {
 const recent = samples.filter(([t, name, v]) => name === feature && now - t <= 1.1 && Number.isFinite(v)).map(row => row[2]);
 if (recent.length < 3) throw new Error('关键关节尚未连续识别；请让完整身体进入画面并保持姿势一秒');
 const ordered = recent.sort((a,b) => a-b);
 const spread = ordered.at(-1)-ordered[0];
 if (spread > (feature === 'jack' ? .18 : 13)) throw new Error('角度仍在变化；请保持这个姿势约一秒后再记录');
 return ordered[Math.floor(ordered.length / 2)];
}
