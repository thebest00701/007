import os
from datetime import datetime
from io import BytesIO

import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="JARVIS MAX | AI Creative Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root { --bg:#080b12; --panel:#101521; --line:#252d3e; --muted:#8d9ab2; --cyan:#6ce5e8; }
.stApp { background: radial-gradient(ellipse at 80% 0%, #15263a 0%, #080b12 42%); color:#edf3ff; font-family:'DM Sans',sans-serif; }
h1,h2,h3 { font-family:'Space Grotesk',sans-serif !important; letter-spacing:-.04em; }
[data-testid="stSidebar"] { background:#0b0f18; border-right:1px solid #202838; }
[data-testid="stMetric"] { background:#111725; border:1px solid #273246; padding:16px 18px; border-radius:16px; }
.stButton>button { border-radius:11px; border:1px solid #394b63; background:linear-gradient(135deg,#b7fbf5,#75c8ec); color:#08111a; font-weight:700; min-height:44px; }
.stTextInput input,.stTextArea textarea,.stSelectbox div[data-baseweb="select"] { background:#0c111b; border-color:#2b3547; border-radius:10px; }
hr { border-color:#263044; }
.hero { padding:28px 30px; border:1px solid #28364b; border-radius:22px; background:linear-gradient(120deg,rgba(25,43,63,.9),rgba(13,18,29,.88)); margin-bottom:22px; }
.eyebrow { color:#6ce5e8; font-size:12px; font-weight:700; letter-spacing:.18em; text-transform:uppercase; }
.hero-title { font-size:44px; line-height:1.05; font-weight:700; margin:10px 0; color:#f4f7ff; }
.subtle { color:#9ba9c0; }
.module { padding:18px; border:1px solid #293347; background:rgba(16,21,33,.8); border-radius:16px; min-height:120px; }
.module-icon { font-size:24px; }
.small-label { color:#9aa9c0; font-size:12px; text-transform:uppercase; letter-spacing:.12em; }
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.markdown("## ✦ JARVIS **MAX**")
    st.caption("AI CREATIVE STUDIO")
    st.divider()
    page = st.radio("WORKSPACE", ["Overview", "Product Studio", "AI Assistant", "Project History"], label_visibility="visible")
    st.divider()
    st.markdown('<div class="small-label">SYSTEM STATUS</div>', unsafe_allow_html=True)
    st.success("Interface online")
    if os.getenv("OPENAI_API_KEY") or (hasattr(st, "secrets") and st.secrets.get("OPENAI_API_KEY", "")):
        st.success("AI key detected")
    else:
        st.warning("AI key not configured")
    st.caption("Local preview • Cloud-ready")

def add_history(kind, title, details):
    st.session_state.history.insert(0, {
        "time": datetime.now().strftime("%d %b %Y, %H:%M"),
        "type": kind,
        "title": title,
        "details": details,
    })

def get_api_key():
    key = os.getenv("OPENAI_API_KEY", "")
    try:
        key = key or st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        pass
    return key

def call_text_ai(prompt):
    key = get_api_key()
    if not key:
        return None, "Add OPENAI_API_KEY in Streamlit Cloud → App settings → Secrets to enable AI generation."
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )
        return response.output_text, None
    except Exception as exc:
        return None, f"AI request failed: {exc}"

if page == "Overview":
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">Your creative command center</div>
      <div class="hero-title">Make ideas look<br>like the future.</div>
      <div class="subtle">A focused workspace for product visuals, marketing copy, and AI-assisted creative workflows.</div>
    </div>
    """, unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    c1.metric("Projects this session", len(st.session_state.history))
    c2.metric("Creative modules", "03")
    c3.metric("Workspace", "Ready")
    st.markdown("### Choose your workspace")
    a,b,c = st.columns(3)
    with a:
        st.markdown('<div class="module"><div class="module-icon">◈</div><h3>Product Studio</h3><p class="subtle">Upload a product photo and prepare a premium infographic brief.</p></div>', unsafe_allow_html=True)
        if st.button("Open Product Studio", use_container_width=True):
            st.session_state.nav_target = "Product Studio"
            st.rerun()
    with b:
        st.markdown('<div class="module"><div class="module-icon">✧</div><h3>AI Assistant</h3><p class="subtle">Draft product descriptions, campaigns, and creative concepts.</p></div>', unsafe_allow_html=True)
        if st.button("Open AI Assistant", use_container_width=True):
            st.session_state.nav_target = "AI Assistant"
            st.rerun()
    with c:
        st.markdown('<div class="module"><div class="module-icon">◷</div><h3>Project History</h3><p class="subtle">Review work created during this session.</p></div>', unsafe_allow_html=True)
        if st.button("View History", use_container_width=True):
            st.session_state.nav_target = "Project History"
            st.rerun()
    if "nav_target" in st.session_state:
        target = st.session_state.pop("nav_target")
        st.info(f"Choose **{target}** from the Workspace menu in the sidebar to open it.")

elif page == "Product Studio":
    st.markdown("## ◈ Product Studio")
    st.caption("Turn a product photo into a structured creative brief for a premium marketplace infographic.")
    left, right = st.columns([1, 1], gap="large")
    with left:
        upload = st.file_uploader("Upload product photo", type=["png","jpg","jpeg","webp"])
        product_name = st.text_input("Product name", placeholder="e.g. Minimal leather sneakers")
        audience = st.text_input("Target audience", placeholder="e.g. Urban professionals, 18–35")
        style = st.selectbox("Visual direction", ["Luxury minimal", "High-conversion marketplace", "Editorial studio", "Tech premium", "Natural lifestyle"])
        language = st.selectbox("Copy language", ["English", "Russian", "Uzbek"])
        benefits = st.text_area("Key features / benefits", placeholder="Materials, dimensions, benefits, differentiators…", height=110)
        generate = st.button("✦ Build infographic brief", use_container_width=True)
    with right:
        if upload:
            try:
                image = Image.open(upload)
                st.image(image, caption=f"{image.width} × {image.height}px", use_container_width=True)
            except Exception:
                st.error("Could not preview this image.")
        else:
            st.markdown('<div class="module"><div class="module-icon">↥</div><h3>Drop in your product</h3><p class="subtle">PNG, JPG, or WEBP. Your original image will be used as the reference for the brief.</p></div>', unsafe_allow_html=True)
        st.markdown("#### Recommended layout")
        st.markdown("1. Hero product image\n2. Three clear benefit callouts\n3. Material / feature close-up\n4. Trust detail or specification strip\n5. Clean brand-consistent footer")
    if generate:
        if not product_name.strip():
            st.warning("Enter a product name first.")
        else:
            prompt = f"""Act as a senior e-commerce art director and conversion copywriter. Create a precise infographic creative brief for this product.
Product: {product_name}
Audience: {audience or 'General online shoppers'}
Visual style: {style}
Output language: {language}
Known features (do not invent facts): {benefits or 'Not provided'}
Return: 1) visual concept, 2) composition and hierarchy, 3) 5-slide/card plan, 4) short headline and benefit copy, 5) palette and typography direction, 6) image-generation prompt. Clearly label any missing product facts and never fabricate specifications."""
            with st.spinner("Building your creative brief…"):
                result, error = call_text_ai(prompt)
            if error:
                st.warning(error)
                st.info("The interface is ready. Configure your API key in the cloud settings to generate the brief.")
            else:
                st.markdown("### Your creative brief")
                st.markdown(result)
                add_history("Product brief", product_name, result[:350])
                st.download_button("Download brief (.md)", result, file_name="jarvis_product_brief.md", mime="text/markdown")
                st.success("Brief generated.")

elif page == "AI Assistant":
    st.markdown("## ✧ AI Assistant")
    st.caption("Your creative copilot for marketing, design direction, and product storytelling.")
    task = st.selectbox("What do you want to create?", ["Product description", "Ad campaign concept", "Social media captions", "Creative direction", "Marketplace listing", "General question"])
    language = st.selectbox("Response language", ["English", "Russian", "Uzbek"], key="assistant_language")
    context = st.text_area("Describe the task", placeholder="Give JARVIS the product, goal, audience, tone, and any constraints…", height=180)
    if st.button("✦ Ask JARVIS", use_container_width=True):
        if not context.strip():
            st.warning("Describe what you want JARVIS to do.")
        else:
            prompt = f"You are JARVIS MAX, a practical expert creative assistant. Task type: {task}. Respond in {language}. Be specific, useful, polished, and honest. Do not invent factual product claims. User request: {context}"
            with st.spinner("JARVIS is thinking…"):
                result, error = call_text_ai(prompt)
            if error:
                st.warning(error)
            else:
                st.markdown("### JARVIS")
                st.markdown(result)
                add_history(task, context[:70], result[:350])
                st.download_button("Download response (.md)", result, file_name="jarvis_response.md", mime="text/markdown")

elif page == "Project History":
    st.markdown("## ◷ Project History")
    st.caption("Recent work from this browser session.")
    if not st.session_state.history:
        st.info("No projects yet. Create a brief or ask JARVIS to start your history.")
    else:
        for i, item in enumerate(st.session_state.history):
            with st.expander(f"{item['type']} · {item['title']} · {item['time']}"):
                st.write(item["details"])
        if st.button("Clear session history"):
            st.session_state.history = []
            st.rerun()

st.divider()
st.markdown('<p class="subtle" style="text-align:center;font-size:12px">JARVIS MAX · AI CREATIVE STUDIO · Built for ideas in motion</p>', unsafe_allow_html=True)
