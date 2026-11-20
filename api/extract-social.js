const crypto = require('crypto');

function decodeEntities(str) {
  if (!str) return '';
  return str
    .replace(/&#x([0-9a-f]+);/gi, (_, h) => {
      try { return String.fromCodePoint(parseInt(h, 16)); } catch(e){ return ''; }
    })
    .replace(/&#([0-9]+);/g, (_, d) => {
      try { return String.fromCodePoint(parseInt(d, 10)); } catch(e){ return ''; }
    })
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>');
}

function extractMeta(html, prop) {
  let m = html.match(new RegExp(`<meta\\s+(?:property|name)=["']${prop}["']\\s+content=["'](.*?)["']`, 'is'));
  if (!m) m = html.match(new RegExp(`<meta\\s+content=["'](.*?)["']\\s+(?:property|name)=["']${prop}["']`, 'is'));
  return m ? decodeEntities(m[1].trim()) : '';
}

async function handleFacebook(url) {
  let html = '';
  let finalUrl = url;

  // 1. Try Desktop Chrome fetch first (contains creation_time and full GraphQL payload)
  try {
    const desktopRes = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'th,en-US;q=0.9,en;q=0.8',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1'
      },
      redirect: 'follow'
    });
    if (desktopRes.ok) {
      html = await desktopRes.text();
      finalUrl = desktopRes.url;
    }
  } catch (e) {}

  // 2. Fallback to Facebook External Hit crawler if desktop fetch blocked or too small
  let crawlerHtml = '';
  if (!html || html.length < 5000 || !extractMeta(html, 'og:description')) {
    try {
      const crawlerRes = await fetch(url, {
        headers: {
          'User-Agent': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'
        },
        redirect: 'follow'
      });
      if (crawlerRes.ok) {
        crawlerHtml = await crawlerRes.text();
        if (!finalUrl || finalUrl === url) finalUrl = crawlerRes.url;
      }
    } catch (e) {}
  }

  const combinedHtml = (html || '') + ' ' + (crawlerHtml || '');

  const titleTag = combinedHtml.match(/<title>(.*?)<\/title>/is);
  let rawTitle = titleTag ? decodeEntities(titleTag[1].trim()) : '';
  let cleanTitle = rawTitle.replace(/^(สมาร์ทกรีน\s*[-·]\s*)|(\s*\|\s*Facebook.*)$/g, '').trim();

  let descOg = extractMeta(combinedHtml, 'og:description');
  let descMeta = extractMeta(combinedHtml, 'description');
  let descTw = extractMeta(combinedHtml, 'twitter:description');
  let candidates = [descOg, descMeta, descTw].filter(Boolean);
  let desc = candidates.length ? candidates.reduce((a, b) => a.length >= b.length ? a : b) : '';

  if (desc && (cleanTitle.endsWith('...') || cleanTitle.length < 5 || cleanTitle.toLowerCase() === 'facebook' || cleanTitle === 'สมาร์ทกรีน')) {
    let lines = desc.split('\n').map(l => l.trim()).filter(Boolean);
    if (lines.length) cleanTitle = lines[0];
  } else if (!cleanTitle || cleanTitle.toLowerCase() === 'facebook') {
    cleanTitle = extractMeta(combinedHtml, 'og:title') || 'โพสต์จากเพจ สมาร์ทกรีน';
  }

  const imgUrl = extractMeta(combinedHtml, 'og:image') || extractMeta(combinedHtml, 'twitter:image');

  // Extract date from creation_time / publish_time
  let postDate = '';
  const ctimes = combinedHtml.match(/["'](?:creation_time|publish_time|story_time)["']\s*:\s*(\d+)/);
  if (ctimes) {
    try {
      const ts = parseInt(ctimes[1]);
      const dt = new Date((ts + 7 * 3600) * 1000);
      if (dt.getFullYear() >= 2020 && dt.getFullYear() <= 2035) {
        postDate = dt.toISOString().slice(0, 10);
      }
    } catch (e) {}
  }
  if (!postDate) {
    postDate = new Date().toISOString().slice(0, 10);
  }

  let imageDataUrl = null;
  let imageId = null;
  if (imgUrl) {
    try {
      const imgRes = await fetch(imgUrl, {
        headers: { 'User-Agent': 'facebookexternalhit/1.1' }
      });
      if (imgRes.ok) {
        const buf = Buffer.from(await imgRes.arrayBuffer());
        if (buf.length > 500) {
          imageId = crypto.createHash('md5').update(buf).digest('hex');
          const mime = imgRes.headers.get('content-type') || 'image/jpeg';
          imageDataUrl = `data:${mime};base64,${buf.toString('base64')}`;
        }
      }
    } catch (e) {}
  }

  return {
    ok: true,
    ch: 'Facebook',
    title: cleanTitle.slice(0, 90),
    caption: desc || cleanTitle,
    date: postDate,
    link: url,
    isReel: /\/(reel|watch|videos)\//i.test(url),
    images: imageId ? [imageId] : [],
    imageDataUrl,
    imgUrl
  };
}

async function handleTikTok(url) {
  let targetUrl = url;
  let vidId = '';
  const vidMatch = url.match(/\/video\/(\d+)/);
  if (vidMatch) {
    vidId = vidMatch[1];
  } else {
    try {
      const r = await fetch(url, {
        headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0' },
        redirect: 'follow'
      });
      if (r.url) {
        targetUrl = r.url;
        const m = r.url.match(/\/video\/(\d+)/);
        if (m) vidId = m[1];
      }
    } catch (e) {}
  }

  let title = '';
  let caption = '';
  let imgUrl = '';
  let embedHtml = '';
  let createTime = null;

  // 1. Try Direct Desktop Firefox Fetch (Extracts __UNIVERSAL_DATA_FOR_REHYDRATION__)
  try {
    const pageRes = await fetch(targetUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'th,en-US;q=0.9,en;q=0.8',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1'
      },
      redirect: 'follow'
    });
    if (pageRes.ok) {
      const html = await pageRes.text();
      // Try __UNIVERSAL_DATA_FOR_REHYDRATION__
      const uMatch = html.match(/<script[^>]+id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)<\/script>/s);
      if (uMatch) {
        try {
          const uData = JSON.parse(uMatch[1]);
          const defaultScope = uData['__DEFAULT_SCOPE__'] || {};
          const videoDetail = defaultScope['webapp.video-detail'] || {};
          const itemStruct = videoDetail.itemInfo?.itemStruct;
          if (itemStruct) {
            if (itemStruct.desc) caption = decodeEntities(itemStruct.desc);
            if (itemStruct.createTime) createTime = parseInt(itemStruct.createTime);
            if (itemStruct.video?.cover) imgUrl = itemStruct.video.cover;
            else if (itemStruct.video?.originCover) imgUrl = itemStruct.video.originCover;
          }
        } catch (e) {}
      }

      // Try SIGI_STATE
      if (!caption) {
        const sigiMatch = html.match(/<script[^>]+id="SIGI_STATE"[^>]*>(.*?)<\/script>/s);
        if (sigiMatch) {
          try {
            const sigi = JSON.parse(sigiMatch[1]);
            const item = (sigi.ItemModule && vidId) ? sigi.ItemModule[vidId] : Object.values(sigi.ItemModule || {})[0];
            if (item) {
              if (item.desc) caption = decodeEntities(item.desc);
              if (item.createTime) createTime = parseInt(item.createTime);
              if (item.video?.cover) imgUrl = item.video.cover;
            }
          } catch (e) {}
        }
      }

      // Try JSON-LD
      if (!caption) {
        const ldMatches = html.matchAll(/<script[^>]+type="application\/ld\+json"[^>]*>(.*?)<\/script>/gs);
        for (const m of ldMatches) {
          try {
            const ld = JSON.parse(m[1]);
            if (ld.description) caption = decodeEntities(ld.description);
            if (ld.name && !caption) caption = decodeEntities(ld.name);
            if (ld.thumbnailUrl && !imgUrl) imgUrl = ld.thumbnailUrl;
            if (ld.uploadDate && !createTime) {
              const dt = new Date(ld.uploadDate);
              if (!isNaN(dt.getTime())) createTime = Math.floor(dt.getTime() / 1000);
            }
          } catch (e) {}
        }
      }

      // Fallback meta
      if (!caption) {
        const metaDesc = extractMeta(html, 'og:description') || extractMeta(html, 'description');
        if (metaDesc && !metaDesc.startsWith('TikTok ·')) caption = metaDesc;
      }
      if (!imgUrl) {
        imgUrl = extractMeta(html, 'og:image') || extractMeta(html, 'twitter:image');
      }
    }
  } catch (e) {}

  // 2. Fallback to TikWM public API if caption is still missing or generic
  if (!caption || caption.startsWith('TikTok ·') || caption.length < 5) {
    try {
      const tikRes = await fetch(`https://www.tikwm.com/api/?url=${encodeURIComponent(targetUrl)}`);
      if (tikRes.ok) {
        const tikData = await tikRes.json();
        if (tikData.code === 0 && tikData.data) {
          const d = tikData.data;
          if (d.title) caption = d.title;
          else if (d.content_desc) caption = d.content_desc;
          if (d.create_time && !createTime) createTime = parseInt(d.create_time);
          if (!imgUrl && d.cover) imgUrl = d.cover;
          else if (!imgUrl && d.origin_cover) imgUrl = d.origin_cover;
        }
      }
    } catch (e) {}
  }

  // 3. Fallback to oEmbed for thumbnail / iframe
  if (!imgUrl || !caption) {
    try {
      const oembedUrl = `https://www.tiktok.com/oembed?url=${encodeURIComponent(targetUrl)}`;
      const oRes = await fetch(oembedUrl, {
        headers: { 'User-Agent': 'Mozilla/5.0' }
      });
      if (oRes.ok) {
        const data = await oRes.json();
        if (data.title && (!caption || caption.startsWith('TikTok ·'))) {
          caption = data.title;
        }
        if (!imgUrl && data.thumbnail_url) imgUrl = data.thumbnail_url;
        if (!embedHtml && data.html) embedHtml = data.html;
      }
    } catch (e) {}
  }

  // 4. Fallback to OpenGraph Crawler
  if (!imgUrl) {
    try {
      const cRes = await fetch(targetUrl, {
        headers: {
          'User-Agent': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'
        },
        redirect: 'follow'
      });
      if (cRes.ok) {
        const html = await cRes.text();
        const ogImg = extractMeta(html, 'og:image') || extractMeta(html, 'lark:url:video_cover_image_url') || extractMeta(html, 'twitter:image');
        if (ogImg) imgUrl = ogImg;
      }
    } catch (e) {}
  }

  // 5. Derive Clean Title from Caption
  if (caption && (!title || title.startsWith('TikTok ·') || title === 'คลิป TikTok · สมาร์ทกรีน')) {
    const firstLine = caption.split('\n').map(l => l.trim()).filter(Boolean)[0] || '';
    if (firstLine) {
      title = firstLine.slice(0, 90);
    } else {
      title = caption.slice(0, 90);
    }
  }

  if (!title) title = 'คลิป TikTok · สมาร์ทกรีน';
  if (!caption) caption = title;

  // 6. Calculate Bangkok Post Date (GMT+7)
  let postDate = '';
  if (createTime) {
    try {
      const dt = new Date((createTime + 7 * 3600) * 1000);
      if (dt.getFullYear() >= 2020 && dt.getFullYear() <= 2035) {
        postDate = dt.toISOString().slice(0, 10);
      }
    } catch (e) {}
  }
  if (!postDate && vidId) {
    try {
      const ts = Number(BigInt(vidId) >> 32n);
      const dt = new Date((ts + 7 * 3600) * 1000);
      if (dt.getFullYear() >= 2020 && dt.getFullYear() <= 2035) {
        postDate = dt.toISOString().slice(0, 10);
      }
    } catch (e) {}
  }
  if (!postDate) {
    postDate = new Date().toISOString().slice(0, 10);
  }

  // 7. Download cover image buffer
  let imageId = null;
  let imageDataUrl = null;
  if (imgUrl) {
    try {
      const imgRes = await fetch(imgUrl, {
        headers: { 'User-Agent': 'Mozilla/5.0' }
      });
      if (imgRes.ok) {
        const buf = Buffer.from(await imgRes.arrayBuffer());
        if (buf.length > 500) {
          imageId = crypto.createHash('md5').update(buf).digest('hex');
          const mime = imgRes.headers.get('content-type') || 'image/jpeg';
          imageDataUrl = `data:${mime};base64,${buf.toString('base64')}`;
        }
      }
    } catch (e) {}
  }

  return {
    ok: true,
    ch: 'TikTok',
    title: title.slice(0, 90),
    caption: caption,
    date: postDate,
    link: targetUrl,
    isReel: true,
    videoId: vidId,
    images: imageId ? [imageId] : [],
    imageDataUrl,
    embedHtml,
    imgUrl
  };
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    let body = req.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch (e) {}
    }
    const url = (body?.url || req.query?.url || '').trim();
    if (!url) {
      return res.status(400).json({ ok: false, error: 'กรุณาระบุลิงก์ (URL)' });
    }

    const lower = url.toLowerCase();
    if (lower.includes('tiktok.com')) {
      const data = await handleTikTok(url);
      return res.status(200).json(data);
    } else if (lower.includes('facebook.com') || lower.includes('fb.watch') || lower.includes('fb.com')) {
      const data = await handleFacebook(url);
      return res.status(200).json(data);
    } else {
      return res.status(400).json({ ok: false, error: 'รองรับเฉพาะลิงก์ Facebook หรือ TikTok' });
    }
  } catch (err) {
    console.error('extract-social error:', err);
    return res.status(500).json({ ok: false, error: err.message || 'เกิดข้อผิดพลาดในการดึงข้อมูล' });
  }
};
