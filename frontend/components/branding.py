import base64
import os
from pathlib import Path

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def get_logo_src():
    assets_dir = Path(__file__).resolve().parents[2] / "assets"
    logo_svg = assets_dir / "logo.svg"
    logo_png = assets_dir / "logo.png"

    logo_data = None
    mime_type = "image/svg+xml"

    if logo_svg.exists():
        logo_data = get_base64_of_bin_file(logo_svg)
    elif logo_png.exists():
        logo_data = get_base64_of_bin_file(logo_png)
        mime_type = "image/png"

    if logo_data:
        return f"data:{mime_type};base64,{logo_data}"
    return None

def get_branding_html():
    img_src = get_logo_src()
    if img_src:
        return f"""
        <div class='brand-row' style='display:flex; align-items:center; gap: 15px; margin-bottom: 20px;'>
            <img src='{img_src}' alt='CivicMind AI Logo' style='width: 48px; height: 48px; object-fit: contain; background: transparent;' />
            <div>
                <h3 style='margin: 0; font-size: 1.25rem; background: linear-gradient(135deg, #5EE7FF, #8B5CF6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>CivicMind AI</h3>
                <p style='margin: 0; font-size: 0.8rem; color: #A5B6D6;'>Enterprise Operations</p>
            </div>
        </div>
        """
    else:
        # Fallback if no logo found
        return """
        <div class='brand-row' style='display:flex; align-items:center; gap: 15px; margin-bottom: 20px;'>
            <div class='brand-orb' style='width:40px; height:40px; border-radius:50%; background: linear-gradient(135deg, #5EE7FF, #8B5CF6); display:flex; align-items:center; justify-content:center; color:white; font-weight:bold; font-size:1.2rem;'>✦</div>
            <div>
                <h3 style='margin: 0; font-size: 1.25rem; background: linear-gradient(135deg, #5EE7FF, #8B5CF6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>CivicMind AI</h3>
                <p style='margin: 0; font-size: 0.8rem; color: #A5B6D6;'>Enterprise Operations</p>
            </div>
        </div>
        """
