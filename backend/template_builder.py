def build_landing_page_html(variation_data: dict, tone: str, context: dict, colors: dict) -> str:
    hero = variation_data.get("hero", {})
    benefits = variation_data.get("benefits", [])
    social_proof = variation_data.get("social_proof", {})
    pricing = variation_data.get("pricing_or_value", {})
    features = variation_data.get("product_features", {})
    final_cta = variation_data.get("final_cta", {})
    
    primary_color = colors.get("primary", "#4f46e5")
    bg_color = colors.get("bg", "#ffffff")
    
    # Tone-based styling extraction
    is_luxury = "luxury" in tone.lower()
    is_urgent = "urgent" in tone.lower()
    is_friendly = "conversational" in tone.lower()

    # Theme Overrides
    if is_luxury:
        primary_color = "#d4af37" # Gold
        bg_color = "#000000"
        text_heading = "#ffffff"
        text_body = "#a3a3a3"
        card_bg = "#111111"
        font_family = "'Playfair Display', serif"
        border_radius = "0px"
        button_radius = "0px"
        font_import = "family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Lato:wght@300;400"
        body_font = "'Lato', sans-serif"
    elif is_urgent:
        primary_color = "#ef4444" # Red
        bg_color = "#ffffff"
        text_heading = "#111827"
        text_body = "#374151"
        card_bg = "#fef2f2"
        font_family = "'Impact', 'Arial Black', sans-serif"
        border_radius = "8px"
        button_radius = "4px"
        font_import = "family=Oswald:wght@500;700&family=Roboto:wght@400;700"
        body_font = "'Roboto', sans-serif"
        font_family = "'Oswald', sans-serif"
    elif is_friendly:
        primary_color = "#10b981" # Green
        bg_color = "#fefce8"      # Light yellow/cream
        text_heading = "#064e3b"
        text_body = "#047857"
        card_bg = "#ffffff"
        font_family = "'Nunito', sans-serif"
        border_radius = "32px"
        button_radius = "32px"
        font_import = "family=Nunito:wght@400;700;800&family=Quicksand:wght@500;700"
        body_font = "'Quicksand', sans-serif"
    else: # Professional
        primary_color = "#2563eb" # Blue
        bg_color = "#ffffff"
        text_heading = "#0f172a"
        text_body = "#475569"
        card_bg = "#f8fafc"
        font_family = "'Outfit', sans-serif"
        border_radius = "16px"
        button_radius = "8px"
        font_import = "family=Outfit:wght@400;600;800&family=Inter:wght@400;500"
        body_font = "'Inter', sans-serif"

    # HTML Blocks
    badge_html = f'<div class="urgency-badge">{hero.get("badge", "")}</div>' if hero.get("badge") else ""
    if is_urgent and not badge_html:
        badge_html = '<div class="urgency-badge">⚠️ ENDING SOON ⚠️</div>'
        
    keyword = hero.get("image_keyword", "business")
    
    # Benefits
    benefits_html = ""
    for benefit in benefits:
        benefits_html += f"""
        <div class="benefit-card">
            <div class="icon-wrap">⭐️</div>
            <h3>{benefit.get("title", "")}</h3>
            <p>{benefit.get("description", "")}</p>
        </div>
        """
        
    # Social Proof
    sp_type = social_proof.get("type", "b2c")
    if sp_type == "b2b":
        logos = "".join([f'<div class="logo-box">{l}</div>' for l in social_proof.get("logos", ["Acme Corp"])])
        sp_html = f"""
        <h2>Trusted by {social_proof.get("metrics", "Top Brands")}</h2>
        <div class="logos-grid">{logos}</div>
        """
    else:
        tests = social_proof.get("testimonials", [{"author":"Satisfied Customer", "text":"Great experience!"}])
        test_html = "".join([f'<div class="test-card"><p>"{t.get("text", "")}"</p><h4> {t.get("author", "")}</h4></div>' for t in tests])
        sp_html = f"""
        <h2>What People Are Saying</h2>
        <div class="tests-grid">{test_html}</div>
        """

    # Pricing
    price_type = pricing.get("type", "service_outcome")
    if price_type == "discount":
        price_html = f"""
        <div class="pricing-card">
            <h3>Exclusive Offer</h3>
            <div class="price">
                <span class="old-price">{pricing.get("old_price", "Regular Price")}</span>
                <span class="new-price">{pricing.get("new_price", "Discount Price")}</span>
            </div>
            <a href="#" class="cta-button">{hero.get("cta", "Buy Now")}</a>
        </div>
        """
    elif price_type == "saas_plan":
        feats = "".join([f'<li>✓ {f}</li>' for f in pricing.get("plan_features", ["Full Access"])])
        price_html = f"""
        <div class="pricing-card">
            <h3>{pricing.get("plan_name", "Pro Plan")}</h3>
            <div class="price"><span class="new-price">{pricing.get("plan_price", "Pricing")}</span></div>
            <ul class="plan-features">{feats}</ul>
            <a href="#" class="cta-button">Start Free Trial</a>
        </div>
        """
    else:
        price_html = f"""
        <div class="value-card">
            <h3>{pricing.get("outcome_title", "Transform Your Results")}</h3>
            <p>{pricing.get("outcome_desc", "Take the next step today.")}</p>
        </div>
        """

    # Features
    feat_type = features.get("type", "feature_blocks")
    items_html = ""
    for item in features.get("items", [{"title": "Feature", "desc": "Details"}]):
        items_html += f"""
        <div class="feature-item">
            <h4>{item.get("title", "")}</h4>
            <p>{item.get("desc", "")}</p>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?{font_import}&display=swap" rel="stylesheet">
    <title>{hero.get("headline", "Landing Page")}</title>
    <style>
        :root {{
            --primary: {primary_color};
            --bg: {bg_color};
            --text-heading: {text_heading};
            --text-body: {text_body};
            --card-bg: {card_bg};
            --spacing: 80px;
            --border-rad: {border_radius};
            --btn-rad: {button_radius};
            --font-head: {font_family};
            --font-body: {body_font};
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: var(--font-body); }}
        body {{ background-color: var(--bg); color: var(--text-body); line-height: 1.6; overflow-x: hidden; }}
        h1, h2, h3, h4 {{ font-family: var(--font-head); color: var(--text-heading); }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 5%; }}
        
        .hero {{ padding: 120px 0 60px; text-align: center; border-bottom: 1px solid rgba(0,0,0,0.05); }}
        .urgency-badge {{ display: inline-block; background: var(--primary); color: var(--bg); padding: 8px 20px; border-radius: var(--btn-rad); font-size: 14px; font-weight: bold; margin-bottom: 24px; letter-spacing: 1px; text-transform: uppercase; }}
        .hero h1 {{ font-size: clamp(40px, 5vw, 68px); line-height: 1.1; margin-bottom: 24px; }}
        .hero p {{ font-size: 22px; max-width: 700px; margin: 0 auto 40px; opacity: 0.9; }}
        .cta-button {{ display: inline-block; background: var(--primary); color: {bg_color}; padding: 18px 45px; border-radius: var(--btn-rad); font-size: 18px; font-weight: bold; text-decoration: none; transition: transform 0.3s; font-family: var(--font-head); text-transform: uppercase; letter-spacing: 1px; border: 2px solid var(--primary); }}
        .cta-button:hover {{ transform: translateY(-3px); filter: brightness(1.2); }}
        
        .hero-image-wrap {{ max-width: 900px; margin: 50px auto 0; border-radius: var(--border-rad); overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.3); border: 2px solid var(--card-bg); }}
        .hero-image-wrap img {{ width: 100%; display: block; }}

        .benefits {{ padding: var(--spacing) 0; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 32px; margin-top: 48px; }}
        .benefit-card {{ background: var(--card-bg); padding: 40px 32px; border-radius: var(--border-rad); text-align: center; border: 1px solid rgba(0,0,0,0.05); }}
        .icon-wrap {{ font-size: 40px; margin-bottom: 20px; }}
        .benefit-card h3 {{ font-size: 24px; margin-bottom: 15px; }}
        
        .features {{ padding: var(--spacing) 0; background: var(--card-bg); border-top: 1px solid rgba(0,0,0,0.05); border-bottom: 1px solid rgba(0,0,0,0.05); }}
        .feature-item {{ background: var(--bg); padding: 35px; border-radius: var(--border-rad); box-shadow: 0 4px 15px rgba(0,0,0,0.03); }}
        .feature-item h4 {{ font-size: 20px; margin-bottom: 12px; color: var(--primary); font-family: var(--font-head); }}

        .pricing-section {{ padding: var(--spacing) 0; text-align: center; }}
        .pricing-card {{ max-width: 400px; margin: 0 auto; background: var(--bg); padding: 40px; border-radius: var(--border-rad); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); border: 4px solid var(--primary); }}
        .old-price {{ text-decoration: line-through; color: var(--text-body); font-size: 24px; margin-right: 15px; opacity: 0.6; }}
        .new-price {{ font-size: 56px; font-weight: bold; color: var(--text-heading); }}
        .plan-features {{ list-style: none; margin: 30px 0; text-align: left; }}
        .plan-features li {{ margin-bottom: 15px; font-size: 18px; border-bottom: 1px solid rgba(0,0,0,0.05); padding-bottom: 10px; }}

        .value-card {{ max-width: 600px; margin: 0 auto; background: var(--primary); color: {bg_color}; padding: 50px; border-radius: var(--border-rad); }}
        .value-card h3 {{ color: {bg_color}; font-size: 32px; margin-bottom: 20px; }}
        .value-card p {{ color: {bg_color}; opacity: 0.9; font-size: 20px; }}

        .social-proof {{ padding: var(--spacing) 0; background: var(--text-heading); color: var(--bg); text-align: center; }}
        .social-proof h2 {{ color: var(--bg); margin-bottom: 50px; font-size: 36px; }}
        .logos-grid {{ display: flex; justify-content: center; gap: 50px; flex-wrap: wrap; opacity: 0.7; }}
        .logo-box {{ font-size: 28px; font-weight: bold; letter-spacing: 2px; text-transform: uppercase; }}
        .tests-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 32px; }}
        .test-card {{ background: rgba(255,255,255,0.05); padding: 40px; border-radius: var(--border-rad); text-align: left; border: 1px solid rgba(255,255,255,0.1); }}
        .test-card p {{ font-style: italic; margin-bottom: 20px; font-size: 18px; line-height: 1.8; }}
        .test-card h4 {{ color: var(--primary); font-size: 18px; }}

        .final-cta {{ padding: calc(var(--spacing) * 1.5) 0; text-align: center; }}
        .final-cta h2 {{ font-size: 54px; margin-bottom: 24px; }}
        
        @media (max-width: 768px) {{ :root {{ --spacing: 60px; }} .hero h1 {{ font-size: 40px; }} }}
    </style>
</head>
<body>

    <section class="hero">
        <div class="container">
            {badge_html}
            <h1>{hero.get("headline", "")}</h1>
            <p>{hero.get("subheadline", "")}</p>
            <a href="#" class="cta-button">{hero.get("cta", "Get Started")}</a>
            <div class="hero-image-wrap">
                <img src="{hero.get('hero_image_url') if hero.get('hero_image_url') and hero.get('hero_image_url').startswith('http') else f'https://source.unsplash.com/1200x600/?{keyword}'}" alt="Hero Image">
            </div>
        </div>
    </section>

    <section class="benefits">
        <div class="container">
            <h2 style="text-align: center; font-size: 42px;">Why Choose Us</h2>
            <div class="grid">
                {benefits_html}
            </div>
        </div>
    </section>

    <section class="features">
        <div class="container">
            <h2 style="text-align: center; margin-bottom: 50px; font-size: 42px;">Key Advantages</h2>
            <div class="grid">
                {items_html}
            </div>
        </div>
    </section>

    <section class="social-proof">
        <div class="container">
            {sp_html}
        </div>
    </section>

    <section class="pricing-section">
        <div class="container">
            {price_html}
        </div>
    </section>

    <section class="final-cta">
        <div class="container">
            <h2>{final_cta.get("headline", "Take Action Now")}</h2>
            <p style="margin-bottom: 40px; font-size: 22px; opacity: 0.8;">Join thousands of others taking action today.</p>
            <a href="#" class="cta-button">{final_cta.get("cta", "Get Started")}</a>
        </div>
    </section>

</body>
</html>"""
    return html
