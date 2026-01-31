import streamlit as st
from generator.site_builder import SiteBuilder
from generator.sanitizer import clean_html, clean_iframe, validate_url
from datetime import datetime
import io
import json
import hashlib
import traceback

st.set_page_config(
    page_title="Kaydiem Titan v25.5",
    layout="wide",
    page_icon="💎",
    initial_sidebar_state="expanded",
)

# ---------- Admin CSS (premium, light) ----------
st.markdown(
    """
    <style>
    :root{ --bg:#f8fafc; --card:#ffffff; --muted:#64748b; --accent:#0f172a; --accent-2:#06b6d4; --radius:12px; }
    body, .main { background: var(--bg) !important; color: var(--accent) !important; font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; }
    .block-container { max-width: 1200px; padding-top: 24px; padding-bottom: 32px; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg,var(--card), #fbfdff) !important; border-right:1px solid #e6eef5; padding:18px; width:340px; }
    .stExpander { background:var(--card) !important; border-radius:12px !important; padding:12px !important; box-shadow:0 8px 24px rgba(16,24,40,0.04); }
    .stButton>button { border-radius:10px; padding:10px 16px; font-weight:700; }
    input, textarea, select { border-radius:8px; border:1px solid #e6eef5 !important; padding:10px !important; }
    .helper { background:#f1fbfb; border-left:3px solid rgba(6,182,212,0.12); padding:8px; border-radius:8px; }
    .device-pill { display:inline-block; padding:6px 10px; border-radius:999px; background:#fff; border:1px solid #eef4f8; cursor:pointer; }
    .device-pill.selected { box-shadow:0 6px 18px rgba(6,182,212,0.08); border-color: rgba(6,182,212,0.12); }
    .stComponents iframe { border-radius:12px; border:1px solid #eef4f8; box-shadow:0 10px 30px rgba(16,24,40,0.06); }
    .premium-badge { display:inline-block; color:white; background:linear-gradient(90deg,var(--accent),var(--accent-2)); padding:6px 10px; border-radius:8px; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar controls ----------
with st.sidebar:
    st.image(
        "https://www.gstatic.com/images/branding/product/2x/business_profile_96dp.png",
        width=56,
    )
    st.title("Titan v25.5 Studio")
    st.caption("Fulfilling 1,000+ Assets Daily")
    st.markdown('<div class="premium-badge">Premium</div>')
    st.divider()

    with st.expander("🎭 1. Architecture DNA", expanded=True):
        layout_dna = st.selectbox(
            "Select Site DNA",
            [
                "Industrial Titan",
                "Classic Royal",
                "Glass-Tech SaaS",
                "The Bento Grid",
                "Brutalist Bold",
                "Corporate Elite",
                "Minimalist Boutique",
                "Midnight Stealth",
                "Vivid Creative",
                "Clean Health",
            ],
            help="Layout template for the generated site.",
        )
        col1, col2 = st.columns(2)
        with col1:
            p_color = st.color_picker("Primary Color", "#0f172a")
        with col2:
            s_color = st.color_picker("Accent (CTA)", "#06b6d4")
        border_rad = st.select_slider(
            "Corner Sharpness",
            options=["0px", "4px", "12px", "24px", "40px", "60px"],
            value="24px",
        )

    with st.expander("✍️ 2. Typography Studio", expanded=True):
        h_font = st.selectbox(
            "Heading Font",
            ["Montserrat", "Playfair Display", "Oswald", "Syncopate", "Space Grotesk"],
            index=0,
        )
        b_font = st.selectbox(
            "Body Text Font", ["Inter", "Roboto", "Open Sans", "Work Sans", "Lora"], index=0
        )
        h_weight = st.select_slider(
            "Heading Weight", options=["300", "400", "700", "900"], value="900"
        )
        ls = st.select_slider(
            "Letter Spacing", options=["-0.05em", "-0.02em", "0em", "0.05em", "0.1em"], value="-0.02em"
        )

    with st.expander("⚙️ 3. Technical Verification"):
        gsc_tag_input = st.text_input("GSC Meta Tag Content", placeholder="google-site-verification=...")
        canonical_check = st.checkbox("Force Canonical Mapping", value=True)

    st.divider()
    st.info("Technical Lead: Kiran Deb Mondal\nwww.kaydiemscriptlab.com")

# ---------- Main UI inputs ----------
st.title("🏗️ Kaydiem Titan Supreme Engine v25.5")
st.caption("Precision Engineering for Local SEO Dominance")

tabs = st.tabs(["📍 Identity", "🏗️ Content & SEO", "🖼️ Assets", "⚡ Live E-com", "🌟 Social Proof", "⚖️ Legal"])

with tabs[0]:
    st.subheader("Core Business Identity (NAP Compliance)")
    c1, c2 = st.columns(2)
    with c1:
        biz_name = st.text_input("Business Name", "Red Hippo (The Planners)")
        biz_phone = st.text_input("Verified Phone", "+91 84540 02711")
        biz_email = st.text_input("Business Email", "events@redhippoplanners.in")
    with c2:
        biz_cat = st.text_input("Primary Category", "Luxury Wedding Planner")
        biz_hours = st.text_input("Operating Hours", "Mon-Sun: 10:00 - 19:00")
        prod_url = st.text_input("Production URL", "https://kani201012.github.io/site/")
    biz_logo = st.text_input("Logo Image URL", help="Direct link to a PNG/SVG file.")
    biz_addr = st.text_area("Full Maps Physical Address")
    biz_areas = st.text_area("Service Areas (Comma separated)", "Vasant Kunj, Chhatarpur, South Delhi, Riyadh")
    map_iframe_raw = st.text_area(
        "Map Embed HTML Code (paste Google Maps iframe only)", placeholder="Paste the <iframe> from Google Maps here."
    )

with tabs[1]:
    st.subheader("AI-Search Content & Meta Layer")
    hero_h = st.text_input(
        "Main Hero Headline", "Crafting Dream Weddings: New Delhi's Premier Luxury Decorators"
    )
    seo_d = st.text_input("Meta Description (160 Chars)", "Verified 2026 AI-Ready Industrial Assets.")
    biz_key = st.text_input("Target SEO Keywords", help="Separate by commas")
    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        biz_serv_text = st.text_area("Services Listing (One per line)", "Floral Decor\nThematic Lighting\nVenue Sourcing")
    with col_s2:
        st.markdown('<div class="helper">💡 Pro Tip: Services are wrapped in H3 for semantics.</div>', unsafe_allow_html=True)
    about_txt = st.text_area("Our Authority Story (E-E-A-T Content)", height=250)

with tabs[2]:
    st.header("📸 High-Ticket Asset Manager")
    custom_hero = st.text_input("Hero Background URL", "")
    custom_feat = st.text_input("Feature Section Image URL", "")
    custom_gall = st.text_input("About Section Image URL", "")

    # Hero image preview and fallback info (admin-side)
    if custom_hero:
        try:
            st.markdown("**Hero image preview (admin):**")
            st.image(custom_hero, caption="custom_hero (input)", use_column_width=True)
        except Exception as e:
            st.warning("Hero image failed to load in admin preview. Check URL. " + str(e))

    # Show the fallback the builder will use (helpful to understand final site)
    try:
        builder_for_preview = SiteBuilder()
        fallback_hero = builder_for_preview._sanitize_context(
            {
                "custom_hero": custom_hero,
                "custom_feat": custom_feat,
                "custom_gall": custom_gall,
                "p_color": p_color,
                "s_color": s_color,
                "border_rad": border_rad,
                "h_font": h_font,
                "b_font": b_font,
                "h_weight": h_weight,
                "ls": ls,
            }
        ).get("custom_hero")
        st.caption("Final hero (fallback applied if empty): " + (fallback_hero or "none"))
    except Exception:
        pass

with tabs[3]:
    st.header("🛒 Headless E-commerce Bridge")
    sheet_url = st.text_input("Published CSV Link (Google Sheets export?format=csv)", "")
    st.info("Publish your Google Sheet (File → Publish to web → CSV) and paste the export link here.")
    # quick server-side CSV parse test
    if st.button("Test CSV Parsing", key="test_csv_btn"):
        try:
            builder_test = SiteBuilder()
            tmp_ctx = dict(context if "context" in globals() else {})
            tmp_ctx.update({"sheet_url": sheet_url})
            sanitized = builder_test._sanitize_context(tmp_ctx)
            products = sanitized.get("products", [])
            if products:
                st.success(f"Found {len(products)} products")
                st.dataframe(products)
            else:
                st.warning("No products returned. Check sheet URL and publish settings.")
        except Exception as e:
            st.error("CSV parse failed: " + str(e))
            st.text(traceback.format_exc())

with tabs[4]:
    st.header("🌟 Trust & Social Proof")
    testi_raw = st.text_area("Testimonials (Name | Quote)", "Aramco | Reliable Partner.\nNEOM | Best in class.")
    faq_raw = st.text_area("F.A.Q. (Question? ? Answer)", "Are you certified? ? Yes, we are ISO 2026 compliant.")

with tabs[5]:
    st.header("⚖️ Authoritative Legal Hub")
    priv_body = st.text_area("Full Privacy Policy Content", height=200)
    terms_body = st.text_area("Full Terms & Conditions Content", height=200)

# ---------- Sanitize & build context ----------
map_iframe = clean_iframe(map_iframe_raw)
about_txt_clean = clean_html(about_txt)
service_list = [s.strip() for s in (biz_serv_text or "").splitlines() if s.strip()]
area_list = [a.strip() for a in (biz_areas or "").split(",") if a.strip()]
if prod_url and not validate_url(prod_url):
    st.warning("Production URL looks invalid — ensure https://")

context = {
    "biz_name": biz_name or "Business Name",
    "biz_phone": biz_phone or "",
    "biz_email": biz_email or "",
    "biz_cat": biz_cat or "",
    "biz_hours": biz_hours or "",
    "prod_url": prod_url or "",
    "biz_logo": biz_logo or "",
    "biz_addr": biz_addr or "",
    "area_list": area_list,
    "hero_h": hero_h or "",
    "seo_d": seo_d or "",
    "biz_key": biz_key or "",
    "biz_serv": service_list,
    "about_txt": about_txt_clean,
    "custom_hero": custom_hero or "",
    "custom_feat": custom_feat or "",
    "custom_gall": custom_gall or "",
    "sheet_url": sheet_url or "",
    "testi_raw": testi_raw or "",
    "faq_raw": faq_raw or "",
    "priv_body": priv_body or "",
    "terms_body": terms_body or "",
    "p_color": p_color,
    "s_color": s_color,
    "border_rad": border_rad,
    "h_font": h_font,
    "b_font": b_font,
    "h_weight": h_weight,
    "ls": ls,
    "layout_dna": layout_dna,
    "gsc_tag_input": gsc_tag_input,
    "map_iframe": map_iframe or "",
}

# ---------- Helper: fingerprint to detect context changes ----------
def context_fingerprint(ctx: dict) -> str:
    # pick the fields that affect generated site; safe dump
    pick = {
        "biz_name": ctx.get("biz_name"),
        "sheet_url": ctx.get("sheet_url"),
        "about_txt": ctx.get("about_txt"),
        "priv_body": ctx.get("priv_body"),
        "terms_body": ctx.get("terms_body"),
        "hero_h": ctx.get("hero_h"),
        "custom_hero": ctx.get("custom_hero"),
    }
    raw = json.dumps(pick, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ---------- Ensure builder in scope ----------
try:
    builder
except NameError:
    builder = SiteBuilder()

# ---------- Instant Preview (robust) ----------
st.markdown("## ⚡ Instant Preview")
st.markdown("Select Page to Preview")

preview_page = st.radio("", ("Home", "About", "Contact", "Privacy", "Terms"), horizontal=True, label_visibility="collapsed")
device = st.radio("Preview device", ["Desktop", "Tablet", "Mobile"], horizontal=True)
height_map = {"Desktop": 800, "Tablet": 700, "Mobile": 600}
preview_height = height_map.get(device, 800)

# Render safely
preview_html = "<div style='padding:18px'>Preview not available</div>"
try:
    if preview_page == "Home":
        preview_html = builder.render_home(context, is_home=True)
    elif preview_page == "About":
        preview_html = builder.render_about(context)
    elif preview_page == "Contact":
        preview_html = builder.render_about(context)
    elif preview_page == "Privacy":
        preview_html = builder._wrap_basic("Privacy Policy", context.get("priv_body", ""))
    elif preview_page == "Terms":
        preview_html = builder._wrap_basic("Terms & Conditions", context.get("terms_body", ""))
except Exception as e:
    st.error("Preview rendering error: " + str(e))
    st.text(traceback.format_exc())
    preview_html = "<div style='padding:24px;color:#b91c1c;'>Error rendering preview (see details above).</div>"

# Render preview
st.components.v1.html(preview_html, height=preview_height, scrolling=True)

# ---------- Premium Export (single source of truth, unique keys) ----------
# Use session_state to cache generated zip and fingerprint to avoid duplicate widgets / re-builds
if "generated_zip" not in st.session_state:
    st.session_state["generated_zip"] = None
if "generated_zip_fp" not in st.session_state:
    st.session_state["generated_zip_fp"] = None

current_fp = context_fingerprint(context)

if st.button("🚀 PREPARE ZIP FOR DEPLOY", key="deploy_prepare_btn"):
    try:
        z_b = io.BytesIO()
        builder.build_zip(context, z_b)
        st.session_state["generated_zip"] = z_b.getvalue()
        st.session_state["generated_zip_fp"] = current_fp
        st.success("ZIP prepared successfully. Use the download button below.")
    except Exception as e:
        st.error("Export failed: " + str(e))
        st.text(traceback.format_exc())

# Only show download if zip prepared and fingerprint matches
if st.session_state.get("generated_zip") and st.session_state.get("generated_zip_fp") == current_fp:
    filename = f"{(context.get('biz_name') or 'site').lower().replace(' ','_')}_final.zip"
    st.download_button(
        label="📥 DOWNLOAD PLATINUM ASSET",
        data=st.session_state["generated_zip"],
        file_name=filename,
        mime="application/zip",
        key="download_zip_btn",
    )
else:
    st.info("Prepare the ZIP to enable download (ZIP is cached during this session).")

# ---------- Footer note ----------
st.caption("Auto-saved: " + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ"))
