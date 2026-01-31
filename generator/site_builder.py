import os
import io
import zipfile
import csv
import re
import requests
from functools import lru_cache
from urllib.parse import quote_plus
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .sanitizer import clean_html, clean_iframe, ensure_trailing_slash

# Determine templates path (repo templates/ folder)
TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), "templates")
if not os.path.isdir(TEMPLATES_PATH):
    TEMPLATES_PATH = os.path.join(os.getcwd(), "templates")

env = Environment(
    loader=FileSystemLoader(TEMPLATES_PATH), autoescape=select_autoescape(["html", "xml"])
)
# url_encode filter for building WA links safely in templates
env.filters["url_encode"] = lambda v: quote_plus(str(v)) if v is not None else ""


@lru_cache(maxsize=32)
def _fetch_text(url: str) -> str:
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text


class SiteBuilder:
    def __init__(self):
        self.env = env

    # --- rendering helpers ---
    def render_home(self, context: dict, is_home: bool = False) -> str:
        ctx = self._sanitize_context(context)
        tpl = self.env.get_template("index.html.j2")
        return tpl.render(**ctx)

    def render_about(self, context: dict) -> str:
        """
        Render the about page. Falls back to index if about template missing.
        """
        ctx = self._sanitize_context(context)
        try:
            tpl = self.env.get_template("about.html.j2")
        except Exception:
            tpl = self.env.get_template("index.html.j2")
        return tpl.render(**ctx)

    def render_contact(self, context: dict) -> str:
        """
        Render a contact page. If a contact template doesn't exist, fall back to the about template.
        """
        ctx = self._sanitize_context(context)
        try:
            tpl = self.env.get_template("contact.html.j2")
        except Exception:
            # fall back
            tpl = self.env.get_template("about.html.j2")
        return tpl.render(**ctx)

    # --- sanitize and context building ---
    def _sanitize_context(self, context: dict) -> dict:
        out = dict(context)

        # Clean free-text fields
        for k in [
            "about_txt",
            "seo_d",
            "hero_h",
            "biz_name",
            "biz_addr",
            "biz_email",
            "biz_cat",
            "priv_body",
            "terms_body",
        ]:
            if out.get(k):
                out[k] = clean_html(str(out.get(k)))

        # sanitize iframe
        out["map_iframe"] = clean_iframe(out.get("map_iframe", ""))

        # ensure prod_url trailing slash
        out["prod_url"] = ensure_trailing_slash(out.get("prod_url", ""))

        # service list
        out["biz_serv"] = [clean_html(s) for s in out.get("biz_serv", [])]

        # default image fallbacks
        out.setdefault(
            "custom_hero",
            out.get("custom_hero")
            or "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&q=80&w=1600",
        )
        out.setdefault(
            "custom_feat",
            out.get("custom_feat")
            or "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&q=80&w=800",
        )
        out.setdefault(
            "custom_gall",
            out.get("custom_gall")
            or "https://images.unsplash.com/photo-1532712938310-34cb3982ef74?auto=format&fit=crop&q=80&w=1600",
        )

        # normalized WA phone (digits only, no leading '+')
        biz_phone = (out.get("biz_phone") or "").strip()
        out["biz_phone_wa"] = re.sub(r"[^\d+]", "", biz_phone).lstrip("+")

        # server-side product parsing (if sheet_url provided)
        sheet_url = out.get("sheet_url") or ""
        out["products"] = []
        if sheet_url:
            try:
                out["products"] = self._fetch_products_from_sheet(sheet_url)
            except Exception:
                out["products"] = []

        out["privacy_html"] = out.get("priv_body", "")
        out["terms_html"] = out.get("terms_body", "")
        out["layout_dna"] = out.get("layout_dna", "Default")

        return out

    # --- CSV product fetcher (robust) ---
    def _fetch_products_from_sheet(self, sheet_url: str):
        """
        Fetch CSV from a Google Sheets link or any CSV/pipe-delimited link.
        Returns a list of product dicts with keys: name, price, desc, img.
        """
        url = sheet_url.strip()
        # Convert Google Sheets edit URL to CSV export link
        if "docs.google.com/spreadsheets" in url:
            url = re.sub(r"/edit.*$", "/export?format=csv", url)

        text = _fetch_text(url)

        # auto-detect delimiter
        delim = ","
        try:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(text.splitlines()[0])
            delim = dialect.delimiter
        except Exception:
            chunk = "\n".join(text.splitlines()[:5])
            delim = "|" if "|" in chunk and chunk.count("|") >= 1 else ","

        reader = csv.reader(text.splitlines(), delimiter=delim)
        rows = [r for r in reader if any(cell.strip() for cell in r)]

        start = 0
        if rows:
            header = [c.strip().lower() for c in rows[0]]
            if any(h in ("name", "service_name", "product", "title") for h in header):
                start = 1

        products = []
        for r in rows[start:]:
            name = r[0].strip() if len(r) > 0 else ""
            price = r[1].strip() if len(r) > 1 else ""
            desc = r[2].strip() if len(r) > 2 else ""
            img = r[3].strip() if len(r) > 3 else ""
            products.append({"name": name, "price": price, "desc": desc, "img": img})

        return products

    # --- zip / export ---
    def build_zip(self, context: dict, output_io: io.BytesIO):
        ctx = self._sanitize_context(context)
        with zipfile.ZipFile(output_io, "w", zipfile.ZIP_DEFLATED) as zf:
            index = self.env.get_template("index.html.j2").render(**ctx)
            # about and contact templates
            try:
                about = self.env.get_template("about.html.j2").render(**ctx)
            except Exception:
                about = index
            try:
                contact = self.env.get_template("contact.html.j2").render(**ctx)
            except Exception:
                contact = about

            zf.writestr("index.html", index)
            zf.writestr("about.html", about)
            zf.writestr("contact.html", contact)
            zf.writestr("privacy.html", self._wrap_basic("Privacy Policy", ctx.get("privacy_html", "")))
            zf.writestr("terms.html", self._wrap_basic("Terms & Conditions", ctx.get("terms_html", "")))
            zf.writestr("404.html", self._wrap_basic("404 - Not Found", "<h1>404</h1><p>Not Found</p>"))
            zf.writestr("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {ctx.get('prod_url', '')}sitemap.xml")
            zf.writestr(
                "sitemap.xml",
                f"<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'><url><loc>{ctx.get('prod_url','')}index.html</loc></url><url><loc>{ctx.get('prod_url','')}about.html</loc></url></urlset>",
            )

    def _wrap_basic(self, title: str, body_html: str) -> str:
        body_safe = clean_html(body_html or "")
        return f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title></head><body><main><h1>{title}</h1><div>{body_safe}</div></main></body></html>"
