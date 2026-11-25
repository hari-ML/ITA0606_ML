import os
import re
import time
import json
import hashlib
import tempfile
from pathlib import Path
import requests
from typing import List, Dict, Optional, Tuple

from androguard.core.apk import APK
from google_play_scraper import app as play_app, search as play_search, permissions as play_permissions

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCAL_PRELOAD_DIR = PROJECT_ROOT / "reference_apks"
TEMP_CACHE_ROOT = Path(os.environ.get("REFERENCE_CACHE_DIR", str(Path(tempfile.gettempdir()) / "malware_detector_ref_cache")))
CACHE_DIR = TEMP_CACHE_ROOT
FDROID_CACHE_FILE = CACHE_DIR / "fdroid_index_cache.json"
FDROID_CACHE_TTL = 24 * 3600  # 24 hours in seconds

FDROID_V2_URL = "https://f-droid.org/repo/index-v2.json"
FDROID_V1_URL = "https://f-droid.org/repo/index-v1.json"
FDROID_REPO_BASE = "https://f-droid.org/repo"

def ensure_cache_dir():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_fdroid_index() -> Tuple[Optional[dict], str]:
    """
    Load F-Droid official index with local 24-hour caching in temp storage.
    Inspects index-v2.json structure, with fallback to index-v1.json.
    """
    ensure_cache_dir()

    # 1. Check temp cache validity (or preloaded local cache if present)
    for cache_candidate in (FDROID_CACHE_FILE, LOCAL_PRELOAD_DIR / "fdroid_index_cache.json"):
        if cache_candidate.exists():
            mtime = cache_candidate.stat().st_mtime
            cache_age = time.time() - mtime
            if cache_age < FDROID_CACHE_TTL and cache_candidate.stat().st_size > 1000:
                try:
                    with cache_candidate.open("r", encoding="utf-8") as f:
                        data = json.load(f)
                        return data, "Cached F-Droid Index (24h valid)"
                except Exception:
                    pass

    # 2. Download from official F-Droid endpoints (v2 with v1 fallback)
    headers = {"User-Agent": "Android-Malware-Capstone/1.0"}
    urls_to_try = [(FDROID_V2_URL, "v2"), (FDROID_V1_URL, "v1")]

    last_error = ""
    for url, version in urls_to_try:
        try:
            r = requests.get(url, headers=headers, timeout=(10, 45))
            if r.status_code == 200:
                data = r.json()
                temp_cache = CACHE_DIR / "fdroid_index_cache.json.tmp"
                with temp_cache.open("w", encoding="utf-8") as f:
                    json.dump(data, f)
                temp_cache.replace(FDROID_CACHE_FILE)
                return data, f"F-Droid official index ({version})"
            else:
                last_error = f"HTTP {r.status_code} from {url}"
        except requests.exceptions.Timeout:
            last_error = f"Connection timed out while fetching {url}"
        except requests.exceptions.ConnectionError:
            last_error = "Network connection failed. Unable to reach F-Droid."
        except Exception as e:
            last_error = f"Error fetching {url}: {str(e)}"

    # 3. Fallback to existing stale cache if offline
    if FDROID_CACHE_FILE.exists() and FDROID_CACHE_FILE.stat().st_size > 1000:
        try:
            with FDROID_CACHE_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return data, "Stale Local Cache (Offline fallback)"
        except Exception:
            pass

    return None, last_error

def _extract_v1_name(a_info: dict) -> str:
    """Extract app title from index-v1 format, checking localized fields."""
    if a_info.get("name"):
        return str(a_info["name"])
    loc = a_info.get("localized", {})
    if isinstance(loc, dict):
        for lang in ["en-US", "en", "en-GB"]:
            if lang in loc and isinstance(loc[lang], dict) and loc[lang].get("name"):
                return str(loc[lang]["name"])
        for val in loc.values():
            if isinstance(val, dict) and val.get("name"):
                return str(val["name"])
    return a_info.get("packageName", "Unknown App")

def search_fdroid_apps(index_data: dict, query: str, limit: int = 5) -> List[dict]:
    """
    Search F-Droid index for matching apps by name or package ID.
    Supports both index-v1 ('apps' list) and index-v2 ('packages' map).
    """
    if not index_data or not query:
        return []

    q = query.strip().lower()
    results = []

    # Format 1: index-v1 ('apps' list + 'packages' dict)
    if "apps" in index_data and isinstance(index_data["apps"], list):
        apps_list = index_data["apps"]
        packages_dict = index_data.get("packages", {})

        for a_info in apps_list:
            pkg_id = a_info.get("packageName", "")
            app_name = _extract_v1_name(a_info)

            pkg_match = q in pkg_id.lower()
            name_match = q in app_name.lower()

            if pkg_match or name_match:
                ver_list = packages_dict.get(pkg_id, [])
                if not ver_list:
                    continue

                latest_v = ver_list[0]
                apk_name = latest_v.get("apkName", "")
                apk_hash = latest_v.get("hash", "").lower()
                ver_name = str(latest_v.get("versionName") or a_info.get("suggestedVersionName") or "Latest")

                q_clean = q.lower()
                name_clean = app_name.lower()
                pkg_clean = pkg_id.lower()

                score = 50
                if q_clean == name_clean or q_clean == pkg_clean:
                    score = 500
                elif name_clean.startswith(q_clean) or pkg_clean.startswith(q_clean):
                    score = 200
                elif q_clean in name_clean:
                    score = 100

                # F-Droid gives full APK capability
                score += 60

                results.append({
                    "name": app_name,
                    "package_id": pkg_id,
                    "source": "F-Droid",
                    "version": ver_name,
                    "developer": a_info.get("authorName", "Open Source (F-Droid)"),
                    "download_info": {
                        "file_name": apk_name,
                        "sha256": apk_hash,
                        "size": latest_v.get("size", 0)
                    },
                    "score": score
                })

    # Format 2: index-v2 ('packages' map with 'metadata' and 'versions')
    elif "packages" in index_data and isinstance(index_data["packages"], dict):
        pkgs = index_data["packages"]
        for pkg_id, p_info in pkgs.items():
            if not isinstance(p_info, dict):
                continue
            meta = p_info.get("metadata", {})
            name_val = meta.get("name", "")
            if isinstance(name_val, dict):
                app_name = name_val.get("en-US", name_val.get("en", ""))
                if not app_name and len(name_val) > 0:
                    app_name = next(iter(name_val.values()))
            else:
                app_name = str(name_val)
            if not app_name:
                app_name = pkg_id

            if q in pkg_id.lower() or q in app_name.lower():
                versions = p_info.get("versions", {})
                if not versions:
                    continue

                sorted_vers = sorted(
                    versions.items(),
                    key=lambda item: item[1].get("added", item[1].get("manifest", {}).get("versionCode", 0)),
                    reverse=True
                )
                latest_v_key, latest_v = sorted_vers[0]
                file_info = latest_v.get("file", {})
                manifest_info = latest_v.get("manifest", {})

                score = 0
                if q == pkg_id.lower():
                    score += 100
                elif q == app_name.lower():
                    score += 90
                elif pkg_id.lower().startswith(q):
                    score += 50

                results.append({
                    "name": app_name,
                    "package_id": pkg_id,
                    "source": "F-Droid",
                    "version": manifest_info.get("versionName", "Latest"),
                    "developer": meta.get("authorName", "Open Source (F-Droid)"),
                    "download_info": {
                        "file_name": file_info.get("name", "").lstrip("/"),
                        "sha256": file_info.get("sha256", "").lower(),
                        "size": file_info.get("size", 0)
                    },
                    "score": score
                })

    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return results[:limit]

def search_google_play_apps(query: str, limit: int = 5) -> List[dict]:
    """
    Search Google Play for app metadata using google-play-scraper.
    Strictly metadata only - NO APK download, no login, no scraping of mirrors.
    """
    candidates = []
    q = query.strip()

    # 1. Direct package lookup if query has dot format
    if "." in q and " " not in q:
        try:
            info = play_app(q, lang="en", country="us")
            if info:
                candidates.append({
                    "name": info.get("title", q),
                    "package_id": q,
                    "source": "Google Play (Metadata Only)",
                    "version": str(info.get("version") or "Varies with device"),
                    "developer": str(info.get("developer") or "Google Play Developer"),
                    "score": 520
                })
        except Exception:
            pass

    # 2. General search query
    try:
        raw_items = play_search(q, n_hits=limit + 3, lang="en", country="us")
        for item in raw_items:
            pkg_id = item.get("appId")
            if not pkg_id:
                for v in item.values():
                    if isinstance(v, str):
                        m = re.search(r'id=([a-zA-Z0-9_\.]+)', v)
                        if m:
                            pkg_id = m.group(1)
                            break
            
            # Specific popular alias fallback
            if not pkg_id and item.get("title", "").lower() == "whatsapp":
                pkg_id = "com.whatsapp"

            if pkg_id and not any(c["package_id"] == pkg_id for c in candidates):
                title = item.get("title", pkg_id)
                t_low = title.lower()
                q_low = q.lower()
                
                score = 30
                if q_low == t_low or q_low == pkg_id.lower():
                    score = 500
                elif t_low.startswith(q_low) or pkg_id.lower().startswith(q_low):
                    score = 180
                elif q_low in t_low:
                    score = 70

                candidates.append({
                    "name": title,
                    "package_id": pkg_id,
                    "source": "Google Play (Metadata Only)",
                    "version": "Varies with device",
                    "developer": item.get("developer", "Google Play Developer"),
                    "score": score
                })
    except Exception:
        pass

    candidates.sort(key=lambda x: x.get("score", 0), reverse=True)
    return candidates[:limit]

def search_all_reference_candidates(query: str, suspect_pkg: Optional[str] = None, limit: int = 5) -> Tuple[List[dict], str]:
    """
    Search local cache, F-Droid, and Google Play metadata for reference app candidates.
    Returns up to 5 best candidates with clear provenance.
    """
    q = (query or suspect_pkg or "").strip()
    if not q:
        return [], "No search query provided."

    all_candidates = []
    seen_packages = set()

    # 1. Local preloaded cache check (read-only) + temp cache check
    ensure_cache_dir()
    search_dirs = [d for d in [LOCAL_PRELOAD_DIR, CACHE_DIR] if d.exists()]
    for cdir in search_dirs:
        for fpath in cdir.iterdir():
            if fpath.is_file() and fpath.name.endswith(".apk") and not fpath.name.endswith(".downloading"):
                cached_pkg = fpath.stem
                if cached_pkg not in seen_packages and q.lower() in cached_pkg.lower():
                    all_candidates.append({
                        "name": cached_pkg,
                        "package_id": cached_pkg,
                        "source": "Local Cache",
                        "version": "Preloaded Local Copy",
                        "developer": "Verified Local Cache",
                        "local_path": str(fpath),
                        "score": 200
                    })
                    seen_packages.add(cached_pkg)

    # 2. F-Droid Search (official index)
    fdroid_data, fdroid_status = get_fdroid_index()
    if fdroid_data:
        fdroid_matches = search_fdroid_apps(fdroid_data, q, limit=limit)
        for m in fdroid_matches:
            if m["package_id"] not in seen_packages:
                for cdir in search_dirs:
                    local_f = cdir / f"{m['package_id']}.apk"
                    if local_f.exists():
                        m["source"] = "Local Cache (F-Droid verified)"
                        m["local_path"] = str(local_f)
                        break
                all_candidates.append(m)
                seen_packages.add(m["package_id"])

    # 3. Google Play Metadata Search
    play_matches = search_google_play_apps(q, limit=limit)
    for m in play_matches:
        if m["package_id"] not in seen_packages:
            all_candidates.append(m)
            seen_packages.add(m["package_id"])

    # Sort candidates by relevance score
    all_candidates.sort(key=lambda c: c.get("score", 0), reverse=True)

    final_list = all_candidates[:limit]
    
    # Format user-facing display label
    for c in final_list:
        c["display_name"] = f"{c['name']}  ({c['package_id']})  [{c['source']}]"

    status_msg = f"Found {len(final_list)} candidates (Indexed via {fdroid_status} & Play metadata)."
    return final_list, status_msg

def download_and_verify_fdroid_apk(candidate: dict, timeout: int = 45) -> Tuple[bool, str, Optional[str]]:
    """
    Download reference APK from official F-Droid repository into temp cache and verify SHA-256 against index.
    Also verifies package name using Androguard before returning the verified temp path.
    """
    ensure_cache_dir()
    pkg_id = candidate["package_id"]
    preloaded_path = LOCAL_PRELOAD_DIR / f"{pkg_id}.apk"
    if preloaded_path.exists() and preloaded_path.stat().st_size > 0:
        return True, f"Using existing preloaded reference APK for '{pkg_id}'.", str(preloaded_path)

    target_apk_path = CACHE_DIR / f"{pkg_id}.apk"

    # If already cached in temp cache, return immediately
    if target_apk_path.exists() and target_apk_path.stat().st_size > 0:
        return True, f"Using cached temp reference APK at '{target_apk_path}'.", str(target_apk_path)

    dl_info = candidate.get("download_info", {})
    file_rel = dl_info.get("file_name", "")
    expected_sha256 = dl_info.get("sha256", "").lower()

    if not file_rel:
        return False, "F-Droid metadata does not specify an APK download file.", None

    download_url = FDROID_REPO_BASE + ("/" if not file_rel.startswith("/") else "") + file_rel.lstrip("/")

    temp_download = CACHE_DIR / f"{pkg_id}.apk.downloading"
    hasher = hashlib.sha256()

    headers = {"User-Agent": "Android-Malware-Capstone/1.0"}
    try:
        r = requests.get(download_url, headers=headers, stream=True, timeout=(10, timeout))
        if r.status_code != 200:
            return False, f"F-Droid server returned HTTP {r.status_code} when downloading APK from {download_url}.", None

        with temp_download.open("wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
                    hasher.update(chunk)

        actual_sha256 = hasher.hexdigest().lower()

        # 1. SHA-256 Verification check
        if expected_sha256 and actual_sha256 != expected_sha256:
            temp_download.unlink(missing_ok=True)
            return False, f"SECURITY ERROR: SHA-256 hash mismatch! Expected {expected_sha256}, got {actual_sha256}. Download rejected.", None

        # 2. Verify package name with Androguard
        try:
            parsed_apk = APK(str(temp_download))
            actual_pkg = parsed_apk.get_package()
            if actual_pkg != pkg_id:
                temp_download.unlink(missing_ok=True)
                return False, f"Package name mismatch: Downloaded APK declares '{actual_pkg}', expected '{pkg_id}'.", None
        except Exception as apk_err:
            temp_download.unlink(missing_ok=True)
            return False, f"Downloaded APK failed static validation: {str(apk_err)}", None

        # Atomically rename to destination inside temp cache
        temp_download.replace(target_apk_path)

        return True, f"Successfully downloaded and verified '{pkg_id}.apk' (SHA-256: {actual_sha256[:16]}...).", str(target_apk_path)

    except requests.exceptions.Timeout:
        temp_download.unlink(missing_ok=True)
        return False, "Download timed out from F-Droid repository. Please check your connection or retry.", None
    except requests.exceptions.ConnectionError:
        temp_download.unlink(missing_ok=True)
        return False, "Network connection error while downloading from F-Droid.", None
    except Exception as e:
        temp_download.unlink(missing_ok=True)
        return False, f"Failed to download reference APK: {str(e)}", None

def fetch_play_metadata(package_id: str) -> Tuple[bool, dict, str]:
    """
    Fetch listed permissions and metadata from Google Play for metadata-only mode.
    """
    try:
        details = play_app(package_id, lang="en", country="us")
    except Exception as e:
        return False, {}, f"Unable to retrieve Google Play metadata for '{package_id}': {str(e)}"

    # Fetch listed permissions
    listed_perms = []
    try:
        perms_dict = play_permissions(package_id, lang="en", country="us")
        if isinstance(perms_dict, dict):
            for cat, plist in perms_dict.items():
                if isinstance(plist, list):
                    for item in plist:
                        listed_perms.append(f"{cat}: {item}")
    except Exception:
        pass

    data = {
        "title": details.get("title", package_id),
        "package_id": package_id,
        "developer": details.get("developer", "Unknown"),
        "version": details.get("version", "Varies with device"),
        "installs": details.get("installs", "N/A"),
        "score": details.get("score", "N/A"),
        "listed_permissions": listed_perms
    }
    return True, data, "Retrieved official Google Play metadata."
