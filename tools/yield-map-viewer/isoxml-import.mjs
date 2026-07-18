// isoxml-import.mjs — C1.2: client-side ISOXML (ISO 11783-10) TASKDATA import for yield-map-viewer.
// Parses binary TLG timelogs via the vendored isoxml bundle and returns yield points + a diagnostic
// report. Design law (2026-07-17 ruling): unparseable channels get a graceful diagnostic, NEVER a
// blank map. No "works with John Deere harvest data" claim until the operator's Gen4/G5 export passes
// the acceptance fixture — this module is store/brand-agnostic and says exactly what it found.

const BUNDLE = './vendor/isoxml/isoxml-timelog.bundle.mjs'
let _mgrCtor = null
async function getISOXML() {                       // lazy-load the ~200KB(gz) parser only on demand
    if (!_mgrCtor) _mgrCtor = (await import(BUNDLE)).ISOXMLManager
    return _mgrCtor
}

const YIELD_RE = /yield/i   // Mass/Volume/Count/Dry-Mass Per Area Yield etc. (DDEntityName from the DD dict)

// Parse a TASKDATA zip (ArrayBuffer) -> { ok, timelogs:[{name, channel, points:[{lat,lon,value,time}]}],
//   channelsSeen, warnings, errors, diagnostic }. Never throws for a farmer — returns a report.
export async function parseTaskData(arrayBuffer, filename = 'TASKDATA.zip') {
    const report = { ok: false, timelogs: [], channelsSeen: [], warnings: [], errors: [], diagnostic: '' }
    let ISOXMLManager
    try { ISOXMLManager = await getISOXML() }
    catch (e) { report.errors.push('Could not load the ISOXML parser: ' + e.message); report.diagnostic = 'Parser failed to load. Try again or use a CSV export.'; return report }

    let mgr
    try {
        mgr = new ISOXMLManager({ version: 4 })
        await mgr.parseISOXMLFile(new Uint8Array(arrayBuffer), 'application/zip')
    } catch (e) {
        report.errors.push('This does not look like an ISOXML TASKDATA export: ' + e.message)
        report.diagnostic = `Couldn't read "${filename}" as ISOXML. Export from your display as ISOXML (a TASKDATA folder with TLG*.BIN files) and drop the zipped folder here.`
        return report
    }
    report.warnings = (mgr.getWarnings && mgr.getWarnings()) || []

    const tasks = mgr.rootElement?.attributes?.Task || []
    const allTimeLogs = []
    for (const t of tasks) for (const tl of (t.attributes?.TimeLog || [])) allTimeLogs.push(tl)
    if (!allTimeLogs.length) {
        report.diagnostic = 'No timelogs found in this TASKDATA. It may be a task plan without recorded field data (no TLG*.BIN).'
        return report
    }

    for (const tl of allTimeLogs) {
        let info
        try { info = tl.parseBinaryFile() }
        catch (e) { report.errors.push(`Timelog ${tl.attributes?.Filename}: ${e.message}`); continue }
        if (tl.parsingErrors?.length) report.errors.push(...tl.parsingErrors.slice(0, 3))

        const channels = (info.valuesInfo || []).map(v => ({
            ddi: v.DDIString, name: v.DDEntityName || `DDI ${v.DDIString}`, unit: v.unit || '',
            min: v.minValue, max: v.maxValue, key: v.valueKey, scale: v.scale ?? 1, offset: v.offset ?? 0,
            isYield: YIELD_RE.test(v.DDEntityName || '')
        }))
        channels.forEach(c => report.channelsSeen.push(`${c.name}${c.unit ? ' (' + c.unit + ')' : ''}`))
        if (!channels.length) continue

        // choose the yield channel; if none, fall back to the first channel so the map is never blank
        const chosen = channels.find(c => c.isYield) || channels[0]

        const filled = tl.getFilledTimeLogs ? tl.getFilledTimeLogs() : info.timeLogs
        const points = []
        for (const rec of filled) {
            if (!rec.isValidPosition) continue
            const raw = rec.values?.[chosen.key]
            if (raw === undefined) continue
            points.push({
                lat: rec.position.PositionNorth, lon: rec.position.PositionEast,
                value: raw * chosen.scale + chosen.offset, time: rec.time
            })
        }
        report.timelogs.push({ name: tl.attributes?.Filename || 'TLG', channel: chosen, points, fellBack: !chosen.isYield })
    }

    const withPoints = report.timelogs.filter(t => t.points.length)
    if (!withPoints.length) {
        report.diagnostic = report.channelsSeen.length
            ? `Parsed the file, but no channel had mappable GPS points. Channels found: ${[...new Set(report.channelsSeen)].join(', ')}.`
            : 'Parsed the file, but found no recorded data values.'
        return report
    }
    report.ok = true
    const anyYield = withPoints.some(t => !t.fellBack)
    report.diagnostic = anyYield
        ? `Loaded ${withPoints.reduce((n, t) => n + t.points.length, 0)} yield points.`
        : `No yield channel found in this export — showing "${withPoints[0].channel.name}" instead. Channels: ${[...new Set(report.channelsSeen)].join(', ')}.`
    return report
}

// Render points to a canvas, colored by value (min->max). Never blanks: caller shows report.diagnostic.
export function renderYieldCanvas(canvas, timelogs, opts = {}) {
    const ctx = canvas.getContext('2d')
    const W = canvas.width, H = canvas.height, pad = 24
    ctx.clearRect(0, 0, W, H)
    const pts = timelogs.flatMap(t => t.points)
    if (!pts.length) return { rendered: 0 }
    const lats = pts.map(p => p.lat), lons = pts.map(p => p.lon), vals = pts.map(p => p.value)
    const minLat = Math.min(...lats), maxLat = Math.max(...lats)
    const minLon = Math.min(...lons), maxLon = Math.max(...lons)
    const minV = Math.min(...vals), maxV = Math.max(...vals)
    const spanLat = (maxLat - minLat) || 1e-6, spanLon = (maxLon - minLon) || 1e-6
    // keep aspect roughly correct (lon compressed by cos(lat))
    const cosLat = Math.cos((minLat + maxLat) / 2 * Math.PI / 180) || 1
    const sx = (W - 2 * pad) / (spanLon * cosLat), sy = (H - 2 * pad) / spanLat
    const s = Math.min(sx, sy)
    const ramp = (t) => { // yield ramp: brown(low) -> yellow -> green(high)
        t = Math.max(0, Math.min(1, t))
        const c = t < 0.5
            ? [Math.round(150 + t * 2 * 90), Math.round(90 + t * 2 * 130), 40]
            : [Math.round(240 - (t - 0.5) * 2 * 180), Math.round(220 - (t - 0.5) * 2 * 40), Math.round(40 + (t - 0.5) * 2 * 30)]
        return `rgb(${c[0]},${c[1]},${c[2]})`
    }
    const r = Math.max(2, opts.dot || Math.min(6, 260 / Math.sqrt(pts.length)))
    for (const p of pts) {
        const x = pad + (p.lon - minLon) * cosLat * s
        const y = H - pad - (p.lat - minLat) * s
        ctx.fillStyle = ramp(maxV === minV ? 0.5 : (p.value - minV) / (maxV - minV))
        ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fill()
    }
    return { rendered: pts.length, minV, maxV, bbox: [minLon, minLat, maxLon, maxLat] }
}
