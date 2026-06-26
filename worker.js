/**
 * WC2026 Results + Odds Proxy — Cloudflare Worker
 *
 * Fetches match results from football-data.org and live odds from the-odds-api.com
 * in parallel, merges them into a single JSON response.
 *
 * Secrets (set in Cloudflare dashboard → Settings → Variables and Secrets):
 *   ODDS_API_KEY — from the-odds-api.com
 */

const API_KEY      = 'b1a8d37382384535a219a1c245fe658a';
const COMPETITION  = 'WC';
const API_URL      = `https://api.football-data.org/v4/competitions/${COMPETITION}/matches`;
const ODDS_SPORT   = 'soccer_fifa_world_cup';
const CACHE_TTL    = 90;

const CORS = {
  'Access-Control-Allow-Origin':  '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Max-Age':       '86400',
  'Content-Type':                 'application/json',
};

export default {
  async fetch(request, env, ctx) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS });
    }

    const cache    = caches.default;
    const cacheKey = new Request(API_URL + '?v=4');
    const cached   = await cache.match(cacheKey);
    if (cached) {
      const body = await cached.text();
      return new Response(body, { headers: CORS });
    }

    const oddsKey = env.ODDS_API_KEY || '';
    const oddsUrl = `https://api.the-odds-api.com/v4/sports/${ODDS_SPORT}/odds/?apiKey=${oddsKey}&regions=us&markets=h2h,totals&oddsFormat=american`;

    // Fetch results and odds in parallel
    const [apiRes, oddsRes] = await Promise.allSettled([
      fetch(API_URL, {
        headers: { 'X-Auth-Token': API_KEY },
        cf: { cacheTtl: 0 }
      }),
      oddsKey
        ? fetch(oddsUrl, { cf: { cacheTtl: 0 } })
        : Promise.resolve(null)
    ]);

    // Process results
    let slim = { fetched: new Date().toISOString(), matches: [], odds: [] };

    if (apiRes.status === 'fulfilled' && apiRes.value.ok) {
      const raw = await apiRes.value.json();
      slim.matches = (raw.matches || [])
        .filter(m => m.stage === 'GROUP_STAGE')
        .map(m => ({
          home:    m.homeTeam.name,
          away:    m.awayTeam.name,
          status:  m.status,
          hg:      m.score?.fullTime?.home ?? null,
          ag:      m.score?.fullTime?.away ?? null,
          hgHT:    m.score?.halfTime?.home ?? null,
          agHT:    m.score?.halfTime?.away ?? null,
          utcDate: m.utcDate,
        }));
    } else {
      slim.resultsError = apiRes.status === 'rejected'
        ? apiRes.reason?.message
        : `HTTP ${apiRes.value?.status}`;
    }

    // Process odds
    if (oddsRes.status === 'fulfilled' && oddsRes.value && oddsRes.value.ok) {
      const oddsRaw = await oddsRes.value.json();
      slim.odds = (oddsRaw || []).map(ev => {
        const toProb = v => v > 0 ? 100/(v+100) : -v/(-v+100);
        const toDec = v => v > 0 ? 1 + v/100 : 1 + 100/(-v);
        let sumH = 0, sumD = 0, sumA = 0, n = 0;
        let sumU25 = 0, nU25 = 0;
        for (const bm of (ev.bookmakers || [])) {
          const mk = bm.markets?.find(m => m.key === 'h2h');
          if (mk) {
            const prices = {};
            mk.outcomes.forEach(o => { prices[o.name] = o.price; });
            const h = prices[ev.home_team], d = prices['Draw'], a = prices[ev.away_team];
            if (h != null && d != null && a != null) {
              const pH = toProb(h), pD = toProb(d), pA = toProb(a);
              const s = pH + pD + pA;
              sumH += pH/s; sumD += pD/s; sumA += pA/s; n++;
            }
          }
          const tot = bm.markets?.find(m => m.key === 'totals');
          if (tot) {
            const u = tot.outcomes?.find(o => o.name === 'Under' && o.point === 2.5);
            if (u) { sumU25 += toDec(u.price); nU25++; }
          }
        }
        if (!n) return null;
        const avgH = sumH/n, avgD = sumD/n, avgA = sumA/n;
        const toAmer = p => p >= 0.5 ? Math.round(-p/(1-p)*100) : Math.round((1-p)/p*100);
        const out = {
          home: ev.home_team,
          away: ev.away_team,
          bookmaker: `consensus (${n})`,
          homeOdds: toAmer(avgH),
          drawOdds: toAmer(avgD),
          awayOdds: toAmer(avgA),
          commence: ev.commence_time,
        };
        if (nU25) out.u25Dec = Math.round(sumU25/nU25 * 100) / 100;
        return out;
      }).filter(Boolean);
    }

    const body = JSON.stringify(slim);
    const toCache = new Response(body, {
      headers: { ...CORS, 'Cache-Control': `public, max-age=${CACHE_TTL}` }
    });
    ctx.waitUntil(cache.put(cacheKey, toCache.clone()));

    return new Response(body, { headers: CORS });
  }
};
