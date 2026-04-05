import streamlit as st


def load_css():
    with open("static/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def metric_card(title, value, description=None):
    desc_html = f'<div class="go-mc-desc">{description}</div>' if description else ''
    st.markdown(f"""
    <div class="go-mc">
        <div class="go-mc-label">{title}</div>
        <div class="go-mc-value" style="font-variant-numeric: tabular-nums;">{value}</div>
        {desc_html}
    </div>
    """, unsafe_allow_html=True)


def page_header(eyebrow: str, title: str, subtitle: str = ""):
    """Consistent sub-page header — editorial style with dark 2px bottom rule."""
    sub_html = f'<p class="go-page-sub">{subtitle}</p>' if subtitle else ''
    st.markdown(f"""
    <div class="go-page-header">
        <p class="go-page-eyebrow">{eyebrow}</p>
        <h1 class="go-page-h1">{title}</h1>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def sep(label: str, small: bool = False):
    """Section separator with tracked uppercase label and horizontal rule."""
    cls = "go-sep go-sep-sm" if small else "go-sep"
    st.markdown(f"""
    <div class="{cls}">
        <span class="go-sep-label">{label}</span>
        <div class="go-sep-line"></div>
    </div>
    """, unsafe_allow_html=True)