"""Generate 4 customer demo PowerPoint slide decks for AI Gateway labs."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

# ── Brand colors ──
DARK_BLUE = "003366"
ACCENT_BLUE = "0078D4"  # Microsoft blue
ACCENT_TEAL = "00B294"
LIGHT_BG = "F5F5F5"
WHITE = "FFFFFF"
DARK_TEXT = "333333"
GRAY_TEXT = "666666"
ORANGE = "FF8C00"
RED_ACCENT = "E81123"
GREEN = "107C10"

OUTPUT_DIR = r"c:\git\AI-Gateway\slides"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def hex_to_rgb(hex_color):
    return RGBColor(int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))


def set_slide_bg(slide, hex_color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = hex_to_rgb(hex_color)


def add_shape_box(slide, left, top, width, height, fill_color, text="", font_size=12, font_color=WHITE, bold=False):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb(fill_color)
    shape.line.fill.background()
    if text:
        tf = shape.text_frame
        tf.word_wrap = True
        tf.auto_size = None
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = Pt(font_size)
        p.font.color.rgb = hex_to_rgb(font_color)
        p.font.bold = bold
        p.alignment = PP_ALIGN.CENTER
        tf.paragraphs[0].space_before = Pt(0)
        tf.paragraphs[0].space_after = Pt(0)
    return shape


def add_title_slide(prs, title, subtitle):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    set_slide_bg(slide, DARK_BLUE)
    # Accent bar
    slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(0.08))
    bar = slide.shapes[-1]
    bar.fill.solid()
    bar.fill.fore_color.rgb = hex_to_rgb(ACCENT_BLUE)
    bar.line.fill.background()
    # Title
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(8.4), Inches(1.5))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(36)
    p.font.color.rgb = hex_to_rgb(WHITE)
    p.font.bold = True
    p.alignment = PP_ALIGN.LEFT
    # Subtitle
    txBox2 = slide.shapes.add_textbox(Inches(0.8), Inches(3.6), Inches(8.4), Inches(1.0))
    tf2 = txBox2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = subtitle
    p2.font.size = Pt(18)
    p2.font.color.rgb = hex_to_rgb(ACCENT_TEAL)
    p2.alignment = PP_ALIGN.LEFT
    # Footer
    txBox3 = slide.shapes.add_textbox(Inches(0.8), Inches(6.5), Inches(8.4), Inches(0.5))
    tf3 = txBox3.text_frame
    p3 = tf3.paragraphs[0]
    p3.text = "Azure API Management  |  AI Gateway Pattern"
    p3.font.size = Pt(11)
    p3.font.color.rgb = hex_to_rgb(GRAY_TEXT)
    p3.alignment = PP_ALIGN.LEFT
    return slide


def add_section_slide(prs, title, subtitle=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, ACCENT_BLUE)
    txBox = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(8), Inches(1.5))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(32)
    p.font.color.rgb = hex_to_rgb(WHITE)
    p.font.bold = True
    p.alignment = PP_ALIGN.CENTER
    if subtitle:
        txBox2 = slide.shapes.add_textbox(Inches(1), Inches(4.0), Inches(8), Inches(0.8))
        tf2 = txBox2.text_frame
        tf2.word_wrap = True
        p2 = tf2.paragraphs[0]
        p2.text = subtitle
        p2.font.size = Pt(16)
        p2.font.color.rgb = hex_to_rgb(WHITE)
        p2.alignment = PP_ALIGN.CENTER
    return slide


def add_content_slide(prs, title, bullets, sub_bullets=None):
    """Add a slide with title and bullet points. sub_bullets is dict mapping bullet index to list of sub-items."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    # Top accent bar
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(0.06))
    bar.fill.solid()
    bar.fill.fore_color.rgb = hex_to_rgb(ACCENT_BLUE)
    bar.line.fill.background()
    # Title
    txBox = slide.shapes.add_textbox(Inches(0.6), Inches(0.3), Inches(8.8), Inches(0.7))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(26)
    p.font.color.rgb = hex_to_rgb(DARK_BLUE)
    p.font.bold = True
    # Bullets
    txBox2 = slide.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(8.4), Inches(5.5))
    tf2 = txBox2.text_frame
    tf2.word_wrap = True
    if sub_bullets is None:
        sub_bullets = {}
    for i, bullet in enumerate(bullets):
        if i == 0:
            p = tf2.paragraphs[0]
        else:
            p = tf2.add_paragraph()
        p.text = bullet
        p.font.size = Pt(16)
        p.font.color.rgb = hex_to_rgb(DARK_TEXT)
        p.space_before = Pt(8)
        p.space_after = Pt(2)
        p.level = 0
        # Add sub-bullets
        if i in sub_bullets:
            for sub in sub_bullets[i]:
                sp = tf2.add_paragraph()
                sp.text = sub
                sp.font.size = Pt(14)
                sp.font.color.rgb = hex_to_rgb(GRAY_TEXT)
                sp.space_before = Pt(2)
                sp.space_after = Pt(2)
                sp.level = 1
    return slide


def add_table_slide(prs, title, headers, rows):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    # Top accent bar
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(0.06))
    bar.fill.solid()
    bar.fill.fore_color.rgb = hex_to_rgb(ACCENT_BLUE)
    bar.line.fill.background()
    # Title
    txBox = slide.shapes.add_textbox(Inches(0.6), Inches(0.3), Inches(8.8), Inches(0.7))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(26)
    p.font.color.rgb = hex_to_rgb(DARK_BLUE)
    p.font.bold = True
    # Table
    num_rows = len(rows) + 1
    num_cols = len(headers)
    tbl_width = Inches(8.6)
    col_width = tbl_width // num_cols
    table = slide.shapes.add_table(num_rows, num_cols, Inches(0.7), Inches(1.3), tbl_width, Inches(0.45 * num_rows)).table
    # Header row
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = hex_to_rgb(DARK_BLUE)
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(13)
            paragraph.font.color.rgb = hex_to_rgb(WHITE)
            paragraph.font.bold = True
            paragraph.alignment = PP_ALIGN.CENTER
    # Data rows
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = table.cell(r + 1, c)
            cell.text = str(val)
            if r % 2 == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = hex_to_rgb("F0F4F8")
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = hex_to_rgb(WHITE)
            for paragraph in cell.text_frame.paragraphs:
                paragraph.font.size = Pt(12)
                paragraph.font.color.rgb = hex_to_rgb(DARK_TEXT)
                paragraph.alignment = PP_ALIGN.CENTER
    return slide


def add_diagram_slide(prs, title, boxes_and_arrows):
    """boxes_and_arrows: list of (left, top, width, height, color, text) tuples + arrows handled separately."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(0.06))
    bar.fill.solid()
    bar.fill.fore_color.rgb = hex_to_rgb(ACCENT_BLUE)
    bar.line.fill.background()
    txBox = slide.shapes.add_textbox(Inches(0.6), Inches(0.3), Inches(8.8), Inches(0.7))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(26)
    p.font.color.rgb = hex_to_rgb(DARK_BLUE)
    p.font.bold = True
    for box in boxes_and_arrows:
        left, top, width, height, color, text = box
        add_shape_box(slide, Inches(left), Inches(top), Inches(width), Inches(height), color, text, font_size=11, font_color=WHITE, bold=True)
    return slide


def add_closing_slide(prs, title="Thank You", lines=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, DARK_BLUE)
    txBox = slide.shapes.add_textbox(Inches(1), Inches(2.2), Inches(8), Inches(1.2))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(36)
    p.font.color.rgb = hex_to_rgb(WHITE)
    p.font.bold = True
    p.alignment = PP_ALIGN.CENTER
    if lines:
        txBox2 = slide.shapes.add_textbox(Inches(1), Inches(3.8), Inches(8), Inches(2.5))
        tf2 = txBox2.text_frame
        tf2.word_wrap = True
        for i, line in enumerate(lines):
            if i == 0:
                p2 = tf2.paragraphs[0]
            else:
                p2 = tf2.add_paragraph()
            p2.text = line
            p2.font.size = Pt(14)
            p2.font.color.rgb = hex_to_rgb(ACCENT_TEAL)
            p2.alignment = PP_ALIGN.CENTER
            p2.space_before = Pt(6)
    return slide


# ════════════════════════════════════════════════════════════════
# 1. FINOPS FRAMEWORK (1-2 summary slides)
# ════════════════════════════════════════════════════════════════
def create_finops_deck():
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    add_title_slide(prs,
        "FinOps Framework for AI",
        "Cost Management, Chargeback & Automated Governance with Azure APIM")

    # Slide 1: Architecture + product tiers (diagram left, table right)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(0.06))
    bar.fill.solid(); bar.fill.fore_color.rgb = hex_to_rgb(ACCENT_BLUE); bar.line.fill.background()
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(9), Inches(0.6))
    p = txBox.text_frame.paragraphs[0]
    p.text = "Architecture & Chargeback Model"; p.font.size = Pt(24); p.font.color.rgb = hex_to_rgb(DARK_BLUE); p.font.bold = True
    # Left: architecture flow boxes
    for (l, t, w, h, c, txt) in [
        (0.3, 1.2, 1.4, 0.65, ACCENT_BLUE, "Client Apps"),
        (2.0, 1.2, 1.6, 0.65, DARK_BLUE, "Azure APIM"),
        (3.9, 1.2, 1.6, 0.65, ACCENT_TEAL, "Azure OpenAI"),
        (2.0, 2.2, 1.6, 0.65, ORANGE, "App Insights"),
        (3.9, 2.2, 1.6, 0.65, "7B2D8B", "Log Analytics"),
        (2.0, 3.2, 1.6, 0.65, RED_ACCENT, "Query Alert"),
        (3.9, 3.2, 1.6, 0.65, GREEN, "Logic App"),
    ]:
        add_shape_box(slide, Inches(l), Inches(t), Inches(w), Inches(h), c, txt, font_size=9, font_color=WHITE, bold=True)
    # Right: product tiers table
    tbl = slide.shapes.add_table(4, 4, Inches(5.8), Inches(1.2), Inches(3.9), Inches(1.8)).table
    for i, h in enumerate(["Product", "TPM", "Quota", "Cost"]):
        cell = tbl.cell(0, i); cell.text = h; cell.fill.solid(); cell.fill.fore_color.rgb = hex_to_rgb(DARK_BLUE)
        for pg in cell.text_frame.paragraphs: pg.font.size = Pt(10); pg.font.color.rgb = hex_to_rgb(WHITE); pg.font.bold = True; pg.alignment = PP_ALIGN.CENTER
    for r, row in enumerate([["Platinum","2,000","1M","$15"],["Gold","1,000","1M","$10"],["Silver","500","1M","$5"]]):
        for c, val in enumerate(row):
            cell = tbl.cell(r+1, c); cell.text = val; cell.fill.solid(); cell.fill.fore_color.rgb = hex_to_rgb("F0F4F8" if r%2==0 else WHITE)
            for pg in cell.text_frame.paragraphs: pg.font.size = Pt(10); pg.font.color.rgb = hex_to_rgb(DARK_TEXT); pg.alignment = PP_ALIGN.CENTER
    # Bottom: key flow summary
    txBox2 = slide.shapes.add_textbox(Inches(0.5), Inches(4.2), Inches(9), Inches(3.0))
    tf2 = txBox2.text_frame; tf2.word_wrap = True
    for i, line in enumerate([
        "emit-token-metric policy \u2192 App Insights (dimension: Product ID)",
        "KQL: (PromptTokens \u00d7 InputPrice + CompletionTokens \u00d7 OutputPrice) / 1000",
        "Scheduled Alert \u2192 Logic App auto-disables subscription exceeding CostQuota",
        "Models: gpt-4.1-mini, gpt-4.1, DeepSeek-V3.2 (all GlobalStandard)",
        "Per-product rate limiting: azure-openai-token-limit + counter-key per subscription",
        "Zero code changes \u2014 all cost tracking & governance at the gateway layer",
    ]):
        p = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
        p.text = "\u2022 " + line; p.font.size = Pt(12); p.font.color.rgb = hex_to_rgb(DARK_TEXT); p.space_before = Pt(4)

    path = os.path.join(OUTPUT_DIR, "01-FinOps-Framework.pptx")
    prs.save(path)
    print(f"  Created: {path}")


# ════════════════════════════════════════════════════════════════
# 2. AI AGENT SERVICE V3 (1-2 summary slides)
# ════════════════════════════════════════════════════════════════
def create_agent_service_deck():
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    add_title_slide(prs,
        "AI Agent Service with APIM",
        "Multi-Agent Orchestration through Azure API Management Model Gateway")

    # Slide 1: Architecture + agents table
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(0.06))
    bar.fill.solid(); bar.fill.fore_color.rgb = hex_to_rgb(ACCENT_BLUE); bar.line.fill.background()
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(9), Inches(0.6))
    p = txBox.text_frame.paragraphs[0]
    p.text = "Architecture & Agents"; p.font.size = Pt(24); p.font.color.rgb = hex_to_rgb(DARK_BLUE); p.font.bold = True
    # Left: architecture boxes
    for (l, t, w, h, c, txt) in [
        (0.3, 1.2, 1.5, 0.6, ACCENT_BLUE, "AI Foundry Hub"),
        (2.1, 1.2, 1.6, 0.6, "7B2D8B", "Agent Service"),
        (4.0, 1.2, 1.8, 0.6, DARK_BLUE, "APIM Gateway"),
        (4.0, 2.1, 1.8, 0.6, ORANGE, "Tool APIs"),
        (0.3, 2.1, 1.5, 0.6, "555555", "Bing Search"),
        (2.1, 2.1, 1.6, 0.6, GREEN, "Logic App"),
    ]:
        add_shape_box(slide, Inches(l), Inches(t), Inches(w), Inches(h), c, txt, font_size=9, font_color=WHITE, bold=True)
    # Right: agents table
    tbl = slide.shapes.add_table(5, 3, Inches(6.1), Inches(1.1), Inches(3.6), Inches(2.1)).table
    for i, h in enumerate(["Agent", "Tool", "Backend"]):
        cell = tbl.cell(0, i); cell.text = h; cell.fill.solid(); cell.fill.fore_color.rgb = hex_to_rgb(DARK_BLUE)
        for pg in cell.text_frame.paragraphs: pg.font.size = Pt(10); pg.font.color.rgb = hex_to_rgb(WHITE); pg.font.bold = True; pg.alignment = PP_ALIGN.CENTER
    for r, row in enumerate([["Math Tutor","Code Interpreter","Sandbox"],["Bing Assistant","Bing Grounding","Bing API"],["Weather","OpenAPI Tool","APIM mock"],["Orders","OpenAPI Tool","Logic App"]]):
        for c, val in enumerate(row):
            cell = tbl.cell(r+1, c); cell.text = val; cell.fill.solid(); cell.fill.fore_color.rgb = hex_to_rgb("F0F4F8" if r%2==0 else WHITE)
            for pg in cell.text_frame.paragraphs: pg.font.size = Pt(10); pg.font.color.rgb = hex_to_rgb(DARK_TEXT); pg.alignment = PP_ALIGN.CENTER
    # Bottom: key points
    txBox2 = slide.shapes.add_textbox(Inches(0.5), Inches(3.5), Inches(9), Inches(3.5))
    tf2 = txBox2.text_frame; tf2.word_wrap = True
    for i, line in enumerate([
        "V3 Pattern: Agents use ai-gateway Foundry connection for all LLM inference through APIM",
        "Model path: ai-gateway/gpt-4.1-mini \u2014 agents never call Azure OpenAI directly",
        "APIM converts subscription key \u2192 managed identity Bearer token (RBAC)",
        "emit-token-metric: 3 dimensions (Subscription ID, Client IP, API ID)",
        "Tool APIs (Weather, Orders, Catalog) also routed through APIM with subscription keys",
        "Single control plane: rate limiting, token tracking, logging, caching \u2014 zero agent code changes",
    ]):
        p = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
        p.text = "\u2022 " + line; p.font.size = Pt(12); p.font.color.rgb = hex_to_rgb(DARK_TEXT); p.space_before = Pt(4)

    path = os.path.join(OUTPUT_DIR, "02-AI-Agent-Service.pptx")
    prs.save(path)
    print(f"  Created: {path}")


# ════════════════════════════════════════════════════════════════
# 3. TOKEN RATE LIMITING (1-2 summary slides)
# ════════════════════════════════════════════════════════════════
def create_rate_limiting_deck():
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    add_title_slide(prs,
        "Token Rate Limiting",
        "Protecting AI Resources with Per-Subscription Token Budgets")

    # Slide 1: Architecture + policy + comparison
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(0.06))
    bar.fill.solid(); bar.fill.fore_color.rgb = hex_to_rgb(ACCENT_BLUE); bar.line.fill.background()
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(9), Inches(0.6))
    p = txBox.text_frame.paragraphs[0]
    p.text = "How It Works"; p.font.size = Pt(24); p.font.color.rgb = hex_to_rgb(DARK_BLUE); p.font.bold = True
    # Architecture boxes
    for (l, t, w, h, c, txt) in [
        (0.3, 1.2, 1.6, 0.7, ACCENT_BLUE, "Client (Key A)"),
        (0.3, 2.2, 1.6, 0.7, "7B2D8B", "Client (Key B)"),
        (2.4, 1.5, 2.2, 1.1, DARK_BLUE, "APIM\nllm-token-limit"),
        (5.0, 1.5, 2.0, 0.9, ACCENT_TEAL, "Azure OpenAI\ngpt-4.1-mini"),
    ]:
        add_shape_box(slide, Inches(l), Inches(t), Inches(w), Inches(h), c, txt, font_size=9, font_color=WHITE, bold=True)
    # Right: comparison table
    tbl = slide.shapes.add_table(5, 3, Inches(5.5), Inches(1.1), Inches(4.2), Inches(2.0)).table
    for i, h in enumerate(["Feature", "APIM Limit", "Platform Limit"]):
        cell = tbl.cell(0, i); cell.text = h; cell.fill.solid(); cell.fill.fore_color.rgb = hex_to_rgb(DARK_BLUE)
        for pg in cell.text_frame.paragraphs: pg.font.size = Pt(9); pg.font.color.rgb = hex_to_rgb(WHITE); pg.font.bold = True; pg.alignment = PP_ALIGN.CENTER
    for r, row in enumerate([["Granularity","Per sub/key","Per deployment"],["Isolation","Per counter-key","Global"],["Custom tiers","Yes (Products)","No"],["Pre-flight","Yes (estimate)","No"]]):
        for c, val in enumerate(row):
            cell = tbl.cell(r+1, c); cell.text = val; cell.fill.solid(); cell.fill.fore_color.rgb = hex_to_rgb("F0F4F8" if r%2==0 else WHITE)
            for pg in cell.text_frame.paragraphs: pg.font.size = Pt(9); pg.font.color.rgb = hex_to_rgb(DARK_TEXT); pg.alignment = PP_ALIGN.CENTER
    # Bottom: key points
    txBox2 = slide.shapes.add_textbox(Inches(0.5), Inches(3.5), Inches(9), Inches(3.5))
    tf2 = txBox2.text_frame; tf2.word_wrap = True
    for i, line in enumerate([
        "Policy: llm-token-limit \u2014 self-contained, no App Insights required",
        "counter-key: context.Subscription.Id \u2014 isolates each subscription\u2019s token budget",
        "tokens-per-minute: configurable per deployment (demo: 100 TPM/subscription)",
        "HTTP 429 + Retry-After when budget exceeded \u2014 request never hits backend",
        "Counter resets every 60s \u2014 no manual intervention needed",
        "Combinable with emit-token-metric for cost visibility, or Products for tiered limits",
    ]):
        p = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
        p.text = "\u2022 " + line; p.font.size = Pt(12); p.font.color.rgb = hex_to_rgb(DARK_TEXT); p.space_before = Pt(4)

    path = os.path.join(OUTPUT_DIR, "03-Token-Rate-Limiting.pptx")
    prs.save(path)
    print(f"  Created: {path}")


# ════════════════════════════════════════════════════════════════
# 4. AI FOUNDRY MODEL GATEWAY (1-2 summary slides)
# ════════════════════════════════════════════════════════════════
def create_model_gateway_deck():
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    add_title_slide(prs,
        "AI Foundry Model Gateway",
        "Centralized AI Access with Enterprise-Grade Security & Reliability")

    # Slide 1: Architecture + auth chain + capabilities
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(0.06))
    bar.fill.solid(); bar.fill.fore_color.rgb = hex_to_rgb(ACCENT_BLUE); bar.line.fill.background()
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(9), Inches(0.6))
    p = txBox.text_frame.paragraphs[0]
    p.text = "Architecture & Authentication"; p.font.size = Pt(24); p.font.color.rgb = hex_to_rgb(DARK_BLUE); p.font.bold = True
    # Architecture boxes
    for (l, t, w, h, c, txt) in [
        (0.3, 1.2, 1.5, 0.65, "7B2D8B", "AI Foundry\nAgents"),
        (2.2, 1.2, 2.0, 0.65, DARK_BLUE, "APIM\nModel Gateway"),
        (4.6, 1.0, 1.8, 0.55, ACCENT_TEAL, "models-foundry\n(wt: 1)"),
        (4.6, 1.7, 1.8, 0.55, ORANGE, "agents-foundry\n(wt: 0)"),
        (6.8, 1.2, 1.5, 0.65, GREEN, "gpt-4o-mini\ngpt-4.1-mini"),
    ]:
        add_shape_box(slide, Inches(l), Inches(t), Inches(w), Inches(h), c, txt, font_size=9, font_color=WHITE, bold=True)
    # Right: Auth chain
    txBox3 = slide.shapes.add_textbox(Inches(0.5), Inches(2.3), Inches(5.0), Inches(1.4))
    tf3 = txBox3.text_frame; tf3.word_wrap = True
    p3 = tf3.paragraphs[0]; p3.text = "3-Hop Authentication Chain"; p3.font.size = Pt(13); p3.font.color.rgb = hex_to_rgb(DARK_BLUE); p3.font.bold = True
    for step in ["1. Agent \u2192 APIM via ai-gateway connection (ApiKey)", "2. APIM validates sub key \u2192 managed identity token", "3. APIM \u2192 Cognitive Services via Bearer (RBAC)"]:
        sp = tf3.add_paragraph(); sp.text = step; sp.font.size = Pt(11); sp.font.color.rgb = hex_to_rgb(DARK_TEXT); sp.space_before = Pt(2)
    # Right: capabilities
    txBox4 = slide.shapes.add_textbox(Inches(5.5), Inches(2.3), Inches(4.2), Inches(1.6))
    tf4 = txBox4.text_frame; tf4.word_wrap = True
    p4 = tf4.paragraphs[0]; p4.text = "Enterprise Capabilities"; p4.font.size = Pt(13); p4.font.color.rgb = hex_to_rgb(DARK_BLUE); p4.font.bold = True
    for cap in ["\u2705 Managed identity (zero keys)", "\u2705 Monitoring (App Insights)", "\u2705 Rate limiting per subscription", "\u2705 Semantic caching", "\u2705 Circuit breaker & retry"]:
        sp = tf4.add_paragraph(); sp.text = cap; sp.font.size = Pt(11); sp.font.color.rgb = hex_to_rgb(DARK_TEXT); sp.space_before = Pt(1)
    # Bottom: key points
    txBox2 = slide.shapes.add_textbox(Inches(0.5), Inches(4.2), Inches(9), Inches(3.0))
    tf2 = txBox2.text_frame; tf2.word_wrap = True
    for i, line in enumerate([
        "ai-gateway connection: type ApiManagement, isSharedToAll \u2014 all agents use APIM as inference endpoint",
        "Backend pool: weight-based routing across Foundry instances (active/standby failover)",
        "Models: gpt-4o-mini (cap 10) + gpt-4.1-mini (cap 12) on models-foundry",
        "Agents reference models as ai-gateway/gpt-4.1-mini \u2014 transparent APIM routing",
        "IaC (Bicep): fully reproducible \u2014 add models/backends without client changes",
    ]):
        p = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
        p.text = "\u2022 " + line; p.font.size = Pt(12); p.font.color.rgb = hex_to_rgb(DARK_TEXT); p.space_before = Pt(4)

    path = os.path.join(OUTPUT_DIR, "04-Model-Gateway.pptx")
    prs.save(path)
    print(f"  Created: {path}")


# ═══════════════════════════════
# Generate all decks
# ═══════════════════════════════
if __name__ == "__main__":
    print("Generating customer demo slides...")
    create_finops_deck()
    create_agent_service_deck()
    create_rate_limiting_deck()
    create_model_gateway_deck()
    print(f"\nAll 4 decks saved to: {OUTPUT_DIR}")
