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
  const res = await fetch(url, {
    headers: {
      'User-Agent': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'
    },
    redirect: 'follow'
  });
  const html = await res.text();

  const titleTag = html.match(/<title>(.*?)<\/title>/is);
  let rawTitle = titleTag ? decodeEntities(titleTag[1].trim()) : '';
  let cleanTitle = rawTitle.replace(/^(สมาร์ทกรีน\s*[-·]\s*)|(\s*\|\s*Facebook.*)$/g, '').trim();

  let descOg = extractMeta(html, 'og:description');
  let descMeta = extractMeta(html, 'description');
  let descTw = extractMeta(html, 'twitter:description');
  let candidates = [descOg, descMeta, descTw].filter(Boolean);
  let desc = candidates.length ? candidates.reduce((a, b) => a.length >= b.length ? a : b) : '';

  if (desc && (cleanTitle.endsWith('...') || cleanTitle.length < 5 || cleanTitle.toLowerCase() === 'facebook' || cleanTitle === 'สมาร์ทกรีน')) {
    let lines = desc.split('\n').map(l => l.trim()).filter(Boolean);
    if (lines.length) cleanTitle = lines[0];
  } else if (!cleanTitle || cleanTitle.toLowerCase() === 'facebook') {
    cleanTitle = extractMeta(html, 'og:title') || 'โพสต์จากเพจ สมาร์ทกรีน';
  }

  const imgUrl = extractMeta(html, 'og:image') || extractMeta(html, 'twitter:image');

  let postDate = '';
  const ctimes = html.match(/["'](?:creation_time|publish_time|story_time)["']\s*:\s*(\d+)/);
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
  const vidMatch = url.match(/\/video\/(\d+)/);
  const vidId = vidMatch ? vidMatch[1] : '';

  let postDate = '';
  if (vidId) {
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

  let title = '';
  let caption = '';
  let imgUrl = '';
  let embedHtml = '';

  // 1. Try oEmbed
  try {
    const oembedUrl = `https://www.tiktok.com/oembed?url=${encodeURIComponent(url)}`;
    const oRes = await fetch(oembedUrl, {
      headers: { 'User-Agent': 'Mozilla/5.0' }
    });
    if (oRes.ok) {
      const data = await oRes.json();
      title = data.title || '';
      caption = data.title || '';
      imgUrl = data.thumbnail_url || '';
      embedHtml = data.html || '';
    }
  } catch (e) {}

  // 2. Try OpenGraph Crawler
  try {
    const cRes = await fetch(url, {
      headers: {
        'User-Agent': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'
      },
      redirect: 'follow'
    });
    if (cRes.ok) {
      const html = await cRes.text();
      const ogImg = extractMeta(html, 'og:image') || extractMeta(html, 'lark:url:video_cover_image_url') || extractMeta(html, 'twitter:image');
      if (ogImg) imgUrl = ogImg;
      const ogTitle = extractMeta(html, 'lark:url:video_title') || extractMeta(html, 'og:title');
      if (ogTitle && (!title || title.startsWith('TikTok ·'))) title = ogTitle;
      const ogDesc = extractMeta(html, 'og:description');
      if (ogDesc && (!caption || caption.startsWith('TikTok ·'))) caption = ogDesc;
    }
  } catch (e) {}

  if (!title) title = 'คลิป TikTok · สมาร์ทกรีน';
  if (!caption) caption = title;

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
    link: url,
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
