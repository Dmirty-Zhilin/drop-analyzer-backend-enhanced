"""
Wayback Machine analyzer service
Enhanced version of the original way2_fixed.py script
"""
import asyncio
import aiohttp
import json
import statistics
from datetime import datetime
from typing import Dict, List, Optional

class WaybackAnalyzer:
    def __init__(self):
        self.cdx_api = "https://web.archive.org/cdx/search/cdx"
        self.avail_api = "https://archive.org/wayback/available"
        self.timemap_url = "http://web.archive.org/web/timemap/link/{url}"
        self.request_timeout = 30
        self.retry_delay = 2
        self.retry_count = 3
    
    async def analyze_domain(self, domain: str, use_test_data: bool = False) -> Dict:
        """Analyze a single domain using Wayback Machine APIs"""
        if use_test_data:
            return self._generate_test_data(domain)
        
        info = {"domain_name": domain}
        start_time = datetime.utcnow()
        
        async with aiohttp.ClientSession() as session:
            # Availability API
            avail_data = await self._safe_request(
                session, "GET", self.avail_api, params={"url": domain}
            )
            
            if avail_data and isinstance(avail_data, dict):
                closest = avail_data.get("archived_snapshots", {}).get("closest")
                if closest:
                    info["has_snapshot"] = bool(closest.get("available"))
                    info["availability_ts"] = closest.get("timestamp")
                else:
                    info["has_snapshot"] = False
                    info["availability_ts"] = None
            else:
                info["has_snapshot"] = False
                info["availability_ts"] = None
            
            # CDX API for detailed analysis
            records = await self._get_cdx_records(session, domain)
            info["total_snapshots"] = len(records)
            
            # Timemap count
            timemap_text = await self._safe_request(
                session, "GET", self.timemap_url.format(url=domain)
            )
            info["timemap_count"] = (
                timemap_text.count("web/") if timemap_text and isinstance(timemap_text, str) else 0
            )
            
            # Process snapshot metrics
            if records:
                self._process_snapshot_metrics(info, records)
            else:
                self._set_empty_metrics(info)
            
            # Calculate quality flags
            self._calculate_quality_flags(info)
            
            info["analysis_time_sec"] = round(
                (datetime.utcnow() - start_time).total_seconds(), 2
            )
        
        return info
    
    async def _get_cdx_records(self, session: aiohttp.ClientSession, domain: str) -> List[Dict]:
        """Get CDX records for domain"""
        records = []
        offset = 0
        limit = 1000
        
        base_params = {
            "url": domain,
            "matchType": "exact",
            "output": "json",
            "fl": "timestamp,original,digest",
            "limit": limit,
            "collapse": "digest"
        }
        
        while True:
            params = {**base_params, "offset": offset}
            batch = await self._safe_request(session, "GET", self.cdx_api, params=params)
            
            if not batch or not isinstance(batch, list) or len(batch) < 1:
                break
            
            # Process batch data
            current_records = []
            if isinstance(batch[0], list):  # Headers present
                if len(batch) < 2:
                    break
                cols = batch[0]
                for row in batch[1:]:
                    if isinstance(row, list) and len(row) == len(cols):
                        records.append(dict(zip(cols, row)))
                        current_records.append(dict(zip(cols, row)))
            elif isinstance(batch[0], dict):  # Data without headers
                for item in batch:
                    if isinstance(item, dict):
                        records.append(item)
                        current_records.append(item)
            else:
                break
            
            if len(current_records) < limit:
                break
            
            offset += limit
            if offset > 50000:  # Prevent infinite loops
                break
        
        return records
    
    def _process_snapshot_metrics(self, info: Dict, records: List[Dict]):
        """Process snapshot records to extract metrics"""
        try:
            times = sorted([r["timestamp"] for r in records if "timestamp" in r and r["timestamp"]])
            dates = []
            
            for ts in times:
                if len(ts) == 14:  # Valid timestamp format
                    try:
                        dates.append(datetime.strptime(ts, "%Y%m%d%H%M%S"))
                    except ValueError:
                        continue
            
            if dates:
                info["first_snapshot"] = dates[0]
                info["last_snapshot"] = dates[-1]
                
                # Calculate intervals
                gaps = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
                info["avg_interval_days"] = round(statistics.mean(gaps), 2) if gaps else 0
                info["max_gap_days"] = max(gaps) if gaps else 0
                
                # Years coverage
                years = {d.year for d in dates}
                info["years_covered"] = len(years)
                info["snapshots_per_year"] = json.dumps({
                    str(y): sum(1 for d in dates if d.year == y) for y in sorted(years)
                })
                
                # Unique versions
                info["unique_versions"] = len({r["digest"] for r in records if "digest" in r})
            else:
                self._set_empty_metrics(info)
                
        except Exception as e:
            print(f"Error processing snapshot metrics: {e}")
            self._set_empty_metrics(info)
    
    def _set_empty_metrics(self, info: Dict):
        """Set empty values for metrics when no data available"""
        for key in ["first_snapshot", "last_snapshot", "avg_interval_days", 
                   "max_gap_days", "years_covered", "snapshots_per_year", "unique_versions"]:
            info[key] = None
    
    def _calculate_quality_flags(self, info: Dict):
        """Calculate quality flags based on metrics"""
        total_snapshots = info.get("total_snapshots", 0)
        max_gap_days = info.get("max_gap_days")
        avg_interval_days = info.get("avg_interval_days")
        
        info["is_good"] = (
            total_snapshots >= 1 and 
            max_gap_days is not None and 
            max_gap_days < 365
        )
        
        info["recommended"] = (
            total_snapshots >= 200 and 
            avg_interval_days is not None and 
            avg_interval_days < 30
        )
    
    def _generate_test_data(self, domain: str) -> Dict:
        """Generate test data for demonstration"""
        import random
        
        return {
            "domain_name": domain,
            "has_snapshot": True,
            "availability_ts": "20231201120000",
            "total_snapshots": random.randint(50, 500),
            "timemap_count": random.randint(100, 1000),
            "first_snapshot": datetime(2015, 1, 1),
            "last_snapshot": datetime(2023, 12, 1),
            "avg_interval_days": round(random.uniform(10, 90), 2),
            "max_gap_days": random.randint(30, 200),
            "years_covered": random.randint(3, 8),
            "snapshots_per_year": json.dumps({"2023": 45, "2022": 52, "2021": 48}),
            "unique_versions": random.randint(20, 100),
            "is_good": True,
            "recommended": random.choice([True, False]),
            "analysis_time_sec": round(random.uniform(1, 5), 2)
        }
    
    async def _safe_request(self, session: aiohttp.ClientSession, method: str, url: str, **kwargs):
        """Safe request with retries and error handling"""
        for attempt in range(1, self.retry_count + 1):
            try:
                async with session.request(method, url, timeout=self.request_timeout, **kwargs) as resp:
                    resp.raise_for_status()
                    
                    if kwargs.get("params", {}).get("output") == "json" or \
                       "application/json" in resp.headers.get("Content-Type", ""):
                        text_content = await resp.text()
                        if not text_content.strip():
                            return None
                        try:
                            return json.loads(text_content)
                        except json.JSONDecodeError:
                            return None
                    else:
                        return await resp.text()
                        
            except aiohttp.ClientResponseError as e:
                if e.status == 429:  # Rate limit
                    await asyncio.sleep(self.retry_delay * attempt * 2)
                elif e.status >= 500:  # Server errors
                    await asyncio.sleep(self.retry_delay * attempt)
                elif attempt == self.retry_count:
                    return None
            except asyncio.TimeoutError:
                if attempt == self.retry_count:
                    return None
            except Exception:
                if attempt == self.retry_count:
                    return None
            
            if attempt < self.retry_count:
                await asyncio.sleep(self.retry_delay * attempt)
        
        return None

