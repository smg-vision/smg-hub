import urllib.request
import urllib.parse
import re
import json
import hashlib
import os
import html
import time
import datetime
import subprocess

DIRECTORY = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(DIRECTORY, 'images')

CHROME_PATHS = [
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
]

def get_browser_exe():
    for p in CHROME_PATHS:
        if os.path.isfile(p):
            return p
    return None

def download_image(img_url):
    try:
        req = urllib.request.Request(
            img_url,
            headers={'User-Agent': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'}
        )
        with urllib.request.urlopen(req, timeout=10) as res:
            data = res.read()
            if len(data) > 1000:
                fid = hashlib.md5(data).hexdigest()
                os.makedirs(IMAGES_DIR, exist_ok=True)
                path = os.path.join(IMAGES_DIR, fid)
                with open(path, 'wb') as f:
                    f.write(data)
                return fid
    except Exception as e:
        print('download_image error:', e)
    return None

def extract_tiktok_date(url):
    vid_m = re.search(r'/video/(\d+)', url)
    if vid_m:
        vid_id = vid_m.group(1)
        try:
            ts = int(vid_id) >> 32
            # UTC+7 (Asia/Bangkok)
            dt = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc) + datetime.timedelta(hours=7)
            if 2020 <= dt.year <= 2035:
                return dt.strftime('%Y-%m-%d')
        except Exception:
            pass
    return None

def extract_facebook_date(url, dom_content=None):
    if dom_content:
        ctimes = re.findall(r'["\'](?:creation_time|publish_time|story_time)["\']\s*:\s*(\d+)', dom_content)
        if ctimes:
            try:
                ts = int(ctimes[0])
                dt = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc) + datetime.timedelta(hours=7)
                if 2020 <= dt.year <= 2035:
                    return dt.strftime('%Y-%m-%d')
            except Exception:
                pass

    exe = get_browser_exe()
    if not exe:
        return None
    try:
        clean_url = url.split('?')[0]
        proc = subprocess.run(
            [exe, '--headless=new', '--disable-gpu', '--no-sandbox', '--dump-dom', clean_url],
            capture_output=True,
            timeout=10
        )
        if proc.returncode == 0 and len(proc.stdout) > 5000:
            c = proc.stdout.decode('utf-8', errors='ignore')
            ctimes = re.findall(r'["\'](?:creation_time|publish_time|story_time)["\']\s*:\s*(\d+)', c)
            if ctimes:
                ts = int(ctimes[0])
                dt = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc) + datetime.timedelta(hours=7)
                if 2020 <= dt.year <= 2035:
                    return dt.strftime('%Y-%m-%d')
    except Exception as e:
        print("Facebook headless date error:", e)
    return None

def fetch_tiktok_details_via_headless(url):
    exe = get_browser_exe()
    if not exe:
        return None, None, None
    try:
        clean_url = url.split('?')[0]
        proc = subprocess.run(
            [exe, '--headless=new', '--disable-gpu', '--no-sandbox', '--dump-dom', clean_url],
            capture_output=True,
            timeout=10
        )
        if proc.returncode == 0 and len(proc.stdout) > 5000:
            c = proc.stdout.decode('utf-8', errors='ignore')
            
            # 1. __UNIVERSAL_DATA_FOR_REHYDRATION__
            m_univ = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', c)
            if m_univ:
                try:
                    jd = json.loads(m_univ.group(1))
                    scope = jd.get('__DEFAULT_SCOPE__', {})
                    item_info = scope.get('webapp.video-detail', {}).get('itemInfo', {}).get('itemStruct', {})
                    if item_info:
                        desc = item_info.get('desc', '').strip()
                        cover_url = item_info.get('video', {}).get('cover') or item_info.get('video', {}).get('originCover')
                        create_time = item_info.get('createTime')
                        date_str = None
                        if create_time:
                            try:
                                dt = datetime.datetime.fromtimestamp(int(create_time), datetime.timezone.utc) + datetime.timedelta(hours=7)
                                if 2020 <= dt.year <= 2035:
                                    date_str = dt.strftime('%Y-%m-%d')
                            except Exception:
                                pass
                        if desc:
                            lines = [ln.strip() for ln in desc.split('\n') if ln.strip()]
                            title = lines[0] if lines else desc[:90]
                            return title, desc, date_str
                except Exception:
                    pass

            # 2. BreadcrumbList ld+json
            m_json = re.search(r'<script[^>]*id=["\']BreadcrumbList["\'][^>]*>(.*?)</script>', c, re.DOTALL)
            if m_json:
                try:
                    jd = json.loads(m_json.group(1))
                    items = jd.get('itemListElement', [])
                    if len(items) >= 3 and items[2].get('item', {}).get('name'):
                        full_desc = items[2]['item']['name'].strip()
                        lines = [ln.strip() for ln in full_desc.split('\n') if ln.strip()]
                        title = lines[0] if lines else full_desc[:90]
                        return title, full_desc, None
                except Exception:
                    pass

            # 3. video-desc container
            m_desc = re.search(r'data-e2e=["\']video-desc["\'][^>]*>(.*?)</div>', c, re.DOTALL)
            if m_desc:
                desc_clean = re.sub(r'<[^>]+>', '\n', m_desc.group(1))
                lines = [ln.strip() for ln in desc_clean.split('\n') if ln.strip()]
                full_desc = '\n'.join(lines)
                title = lines[0] if lines else full_desc[:90]
                return title, full_desc, None
    except Exception as e:
        print("Headless fetch error:", e)
    return None, None, None

def extract_social_url(url):
    url = url.strip()
    is_tiktok = 'tiktok.com' in url.lower()
    is_fb = any(x in url.lower() for x in ['facebook.com', 'fb.watch', 'fb.com'])

    if is_tiktok:
        img_id = None
        title = ''
        caption = ''
        post_date = extract_tiktok_date(url)

        try:
            crawler_req = urllib.request.Request(
                url,
                headers={'User-Agent': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'}
            )
            with urllib.request.urlopen(crawler_req, timeout=8) as res:
                c_html = res.read().decode('utf-8', errors='ignore')
                def get_c_meta(prop):
                    m = re.search(r'<meta\s+(?:property|name)=["\']' + re.escape(prop) + r'["\']\s+content=["\'](.*?)["\']', c_html, re.DOTALL)
                    if not m:
                        m = re.search(r'<meta\s+content=["\'](.*?)["\']\s+(?:property|name)=["\']' + re.escape(prop) + r'["\']', c_html, re.DOTALL)
                    return html.unescape(m.group(1)).strip() if m else ''
                
                cover_url = get_c_meta('og:image') or get_c_meta('lark:url:video_cover_image_url') or get_c_meta('twitter:image')
                if cover_url:
                    img_id = download_image(cover_url)
                
                title = get_c_meta('lark:url:video_title') or get_c_meta('og:title') or ''
                caption = get_c_meta('og:description') or title
        except Exception as e:
            print('TikTok crawler fetch error:', e)

        vid_m = re.search(r'/video/(\d+)', url)
        vid_id = vid_m.group(1) if vid_m else ''
        embed_html = ''
        try:
            clean_url = f"https://www.tiktok.com/@smartgreen/video/{vid_id}" if vid_id else url
            oembed_url = f"https://www.tiktok.com/oembed?url={urllib.parse.quote(clean_url)}"
            req = urllib.request.Request(oembed_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=6) as res:
                data = json.loads(res.read().decode('utf-8'))
                if not title or title.startswith('TikTok ·'):
                    title = data.get('title') or title
                embed_html = data.get('html', '')
                if not img_id and data.get('thumbnail_url'):
                    img_id = download_image(data['thumbnail_url'])
        except Exception as e:
            print('TikTok oembed fetch error:', e)

        # If title or caption is still generic, fetch via direct Firefox UA or TikWM
        if not title or title.startswith('TikTok ·') or not caption or caption.startswith('TikTok ·'):
            # 1. Try Direct Firefox UA fetch
            try:
                ff_req = urllib.request.Request(
                    url,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'th,en-US;q=0.9,en;q=0.8'
                    }
                )
                with urllib.request.urlopen(ff_req, timeout=8) as ff_res:
                    ff_html = ff_res.read().decode('utf-8', errors='ignore')
                    m_univ = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', ff_html)
                    if m_univ:
                        jd = json.loads(m_univ.group(1))
                        scope = jd.get('__DEFAULT_SCOPE__', {})
                        item_struct = scope.get('webapp.video-detail', {}).get('itemInfo', {}).get('itemStruct', {})
                        if item_struct:
                            desc = item_struct.get('desc', '').strip()
                            if desc:
                                caption = html.unescape(desc)
                                lines = [ln.strip() for ln in caption.split('\n') if ln.strip()]
                                title = lines[0][:90] if lines else caption[:90]
                            c_time = item_struct.get('createTime')
                            if c_time and not post_date:
                                dt = datetime.datetime.fromtimestamp(int(c_time), datetime.timezone.utc) + datetime.timedelta(hours=7)
                                if 2020 <= dt.year <= 2035:
                                    post_date = dt.strftime('%Y-%m-%d')
                            if not img_id:
                                cov = item_struct.get('video', {}).get('cover') or item_struct.get('video', {}).get('originCover')
                                if cov:
                                    img_id = download_image(cov)
            except Exception as e:
                print('Direct Firefox UA fetch error:', e)

            # 2. Try TikWM
            if not title or title.startswith('TikTok ·') or not caption or caption.startswith('TikTok ·'):
                try:
                    tik_url = f"https://www.tikwm.com/api/?url={urllib.parse.quote(url)}"
                    tik_req = urllib.request.Request(tik_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(tik_req, timeout=6) as tik_res:
                        tik_data = json.loads(tik_res.read().decode('utf-8'))
                        if tik_data.get('code') == 0 and tik_data.get('data'):
                            td = tik_data['data']
                            desc = td.get('title') or td.get('content_desc') or ''
                            if desc:
                                caption = desc
                                lines = [ln.strip() for ln in caption.split('\n') if ln.strip()]
                                title = lines[0][:90] if lines else caption[:90]
                            if td.get('create_time') and not post_date:
                                dt = datetime.datetime.fromtimestamp(int(td['create_time']), datetime.timezone.utc) + datetime.timedelta(hours=7)
                                if 2020 <= dt.year <= 2035:
                                    post_date = dt.strftime('%Y-%m-%d')
                            if not img_id:
                                cov = td.get('cover') or td.get('origin_cover')
                                if cov:
                                    img_id = download_image(cov)
                except Exception as e:
                    print('TikWM fetch error:', e)

            # 3. Headless browser fallback
            if not title or title.startswith('TikTok ·') or not caption or caption.startswith('TikTok ·'):
                h_title, h_caption, h_date = fetch_tiktok_details_via_headless(url)
                if h_title:
                    title = h_title
                if h_caption:
                    caption = h_caption
                if not post_date and h_date:
                    post_date = h_date

        if not title:
            title = 'คลิป TikTok · สมาร์ทกรีน'
        if not caption:
            caption = title
        if not post_date:
            post_date = datetime.date.today().strftime('%Y-%m-%d')

        return {
            'ok': True,
            'ch': 'TikTok',
            'title': title[:90],
            'caption': caption,
            'date': post_date,
            'link': url,
            'isReel': True,
            'videoId': vid_id,
            'images': [img_id] if img_id else [],
            'embedHtml': embed_html
        }

    elif is_fb:
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'}
            )
            with urllib.request.urlopen(req, timeout=10) as res:
                content = res.read().decode('utf-8', errors='ignore')
                
                def get_meta(prop):
                    m = re.search(r'<meta\s+(?:property|name)=["\']' + re.escape(prop) + r'["\']\s+content=["\'](.*?)["\']', content, re.DOTALL)
                    if not m:
                        m = re.search(r'<meta\s+content=["\'](.*?)["\']\s+(?:property|name)=["\']' + re.escape(prop) + r'["\']', content, re.DOTALL)
                    return html.unescape(m.group(1)).strip() if m else ''

                title_tag = re.search(r'<title>(.*?)</title>', content)
                raw_title = html.unescape(title_tag.group(1)) if title_tag else ''
                clean_title = re.sub(r'^(สมาร์ทกรีน\s*[-·]\s*)|(\s*\|\s*Facebook.*)$', '', raw_title).strip()

                desc_og = get_meta('og:description')
                desc_meta = get_meta('description')
                desc_tw = get_meta('twitter:description')
                candidates = [d for d in [desc_og, desc_meta, desc_tw] if d]
                desc = max(candidates, key=len) if candidates else ''

                if desc and (clean_title.endswith('...') or len(clean_title) < 5 or clean_title.lower() == 'facebook' or clean_title == 'สมาร์ทกรีน'):
                    lines = [ln.strip() for ln in desc.split('\n') if ln.strip()]
                    if lines:
                        clean_title = lines[0]
                elif not clean_title or clean_title.lower() == 'facebook':
                    clean_title = get_meta('og:title') or 'โพสต์จากเพจ สมาร์ทกรีน'

                img_url = get_meta('og:image') or get_meta('twitter:image')
                img_id = download_image(img_url) if img_url else None

                is_video = any(x in url.lower() for x in ['/reel/', '/watch/', '/videos/'])

                post_date = extract_facebook_date(url, dom_content=content)
                if not post_date:
                    post_date = datetime.date.today().strftime('%Y-%m-%d')

                return {
                    'ok': True,
                    'ch': 'Facebook',
                    'title': clean_title[:90],
                    'caption': desc if desc else clean_title,
                    'date': post_date,
                    'link': url,
                    'isReel': is_video,
                    'images': [img_id] if img_id else []
                }
        except Exception as e:
            return {'ok': False, 'error': f'Facebook fetch error: {e}'}

    return {'ok': False, 'error': 'กรุณาระบุลิงก์ Facebook หรือ TikTok'}

def sync_smartgreen_page(urls=None):
    """
    Check recent posts from Smart Green Facebook Page & TikTok or import provided URLs
    """
    data_path = os.path.join(DIRECTORY, 'data.json')
    if not os.path.exists(data_path):
        return {'ok': False, 'error': 'data.json not found'}
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    existing_links = set(p.get('link') for p in data.get('plan', []) if p.get('link'))
    synced = []

    if urls:
        for u in urls:
            u = u.strip()
            if not u or u in existing_links:
                continue
            item = extract_social_url(u)
            if item.get('ok'):
                p_prefix = 'tt-' if item.get('ch') == 'TikTok' else 'fb-'
                post_id = p_prefix + hashlib.md5(u.encode('utf-8')).hexdigest()[:12]
                new_plan = {
                    'id': post_id,
                    'title': item['title'],
                    'caption': item['caption'],
                    'link': u,
                    'ch': item.get('ch', 'Facebook'),
                    'date': item.get('date') or time.strftime('%Y-%m-%d'),
                    'status': 'live',
                    'images': item.get('images', []),
                    'file': None
                }
                data['plan'].insert(0, new_plan)
                existing_links.add(u)
                synced.append(new_plan)

    if synced:
        data['plan'].sort(key=lambda p: (str(p.get('date', '')), str(p.get('id', ''))), reverse=True)
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    return {'ok': True, 'synced_count': len(synced), 'items': synced}
