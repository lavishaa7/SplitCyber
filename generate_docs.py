import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_styled_heading(doc, text, level):
    h = doc.add_heading(text, level=level)
    run = h.runs[0]
    run.font.name = "Arial"
    if level == 1:
        run.font.size = Pt(18)
        run.font.bold = True
        run.font.color.rgb = RGBColor(30, 41, 59) # Slate 800
        h.paragraph_format.space_before = Pt(18)
        h.paragraph_format.space_after = Pt(6)
    elif level == 2:
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(79, 70, 229) # Indigo 600
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)
    elif level == 3:
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = RGBColor(51, 65, 85) # Slate 700
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(2)
    return h

def add_callout(doc, title, text, bg_hex="F1F5F9", border_hex="4F46E5"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="24" w:space="0" w:color="{border_hex}"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    r_title = p.add_run(f"📌 {title}\n")
    r_title.bold = True
    r_title.font.name = "Arial"
    r_title.font.size = Pt(10.5)
    r_title.font.color.rgb = RGBColor(79, 70, 229)
    
    r_text = p.add_run(text)
    r_text.font.name = "Arial"
    r_text.font.size = Pt(10)
    r_text.font.color.rgb = RGBColor(51, 65, 85)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def format_table(table, col_widths, headers, data):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    header_row = table.rows[0]
    for i, title in enumerate(headers):
        cell = header_row.cells[i]
        cell.width = col_widths[i]
        cell.text = title
        set_cell_background(cell, "1E293B") # Dark slate
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p.runs:
            r.font.name = "Arial"
            r.font.bold = True
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(255, 255, 255)

    for row_idx, row_data in enumerate(data):
        row = table.add_row()
        bg = "F8FAFC" if row_idx % 2 == 0 else "FFFFFF"
        for i, val in enumerate(row_data):
            cell = row.cells[i]
            cell.width = col_widths[i]
            cell.text = str(val)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            p = cell.paragraphs[0]
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(9)
                r.font.color.rgb = RGBColor(51, 65, 85)

def build_document(output_path):
    doc = Document()
    
    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # ------------------ TITLE SECTION ------------------
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(20)
    title_p.paragraph_format.space_after = Pt(4)
    run_title = title_p.add_run("SplitCyber — Group Expense Splitter")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(26)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(30, 41, 59)

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(12)
    run_sub = sub_p.add_run("Comprehensive Technical Architecture, Algorithmic Analysis & Step-by-Step Implementation Guide")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(13)
    run_sub.font.color.rgb = RGBColor(79, 70, 229)

    meta_p = doc.add_paragraph()
    meta_p.paragraph_format.space_after = Pt(20)
    meta_run = meta_p.add_run("Author: Lavisha Menghani | Repository: https://github.com/lavishaa7/SplitCyber | Version: 1.0.0")
    meta_run.font.name = "Arial"
    meta_run.font.size = Pt(9.5)
    meta_run.font.italic = True
    meta_run.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ------------------ EXECUTIVE SUMMARY ------------------
    add_styled_heading(doc, "Executive Summary", level=1)
    p = doc.add_paragraph(
        "SplitCyber is an enterprise-grade group expense management and debt simplification platform inspired by Splitwise. "
        "It provides groups of individuals (travelers, roommates, project teams) with a streamlined system to record expenditures, "
        "support diverse financial splitting mechanisms, track direct peer repayments, and calculate the absolute minimal number of "
        "settlement transactions necessary to balance all group debts."
    )
    p.paragraph_format.space_after = Pt(8)

    add_callout(
        doc,
        "Core Value Proposition",
        "Without algorithmic simplification, an N-person group with multiple overlapping expenses can generate up to N * (N - 1) "
        "confusing peer transfers. SplitCyber deploys a Greedy Min-Cash-Flow graph-settlement algorithm that provably resolves all "
        "inter-member debts in at most (N - 1) transactions, saving time and eliminating human calculation error."
    )

    # ------------------ CHAPTER 1: THEORETICAL FOUNDATIONS ------------------
    add_styled_heading(doc, "1. Mathematical & Theoretical Foundations", level=1)

    add_styled_heading(doc, "1.1 Zero-Sum Conservation in Closed Financial Groups", level=2)
    p = doc.add_paragraph(
        "Every group in SplitCyber represents a closed financial network. By financial conservation laws, the total amount of money "
        "disbursed by all group members must exactly equal the total amount of expenses consumed across all members:"
    )
    doc.add_paragraph("   ∑ (Total Paid by Member i) = ∑ (Total Share Consumed by Member i)   for all i ∈ [1, N]")
    
    p = doc.add_paragraph(
        "For any individual group member u, their Net Balance is defined by the governing formula:"
    )
    doc.add_paragraph("   Net_Balance(u) = [ Paid(u) + Settlements_Sent(u) ] - [ Share(u) + Settlements_Received(u) ]")
    
    p = doc.add_paragraph(
        "Financial interpretation of Net Balance:\n"
        "• Net > 0 (Creditor): The member has fronted more cash than their consumption. They are owed money.\n"
        "• Net < 0 (Debtor): The member has consumed more value than they paid for. They owe money.\n"
        "• Net = 0 (Balanced): The member is completely square with the group.\n"
        "Across the entire group, the sum of all net balances is strictly zero: ∑ Net_Balance(u) = 0."
    )

    add_styled_heading(doc, "1.2 The Greedy Min-Cash-Flow Debt Simplification Algorithm", level=2)
    p = doc.add_paragraph(
        "The core service of SplitCyber (located in backend/app/services/balance.py) implements the Greedy Min-Cash-Flow algorithm. "
        "The mathematical execution proceeds through the following four steps:"
    )

    algo_steps = [
        ("Step 1: Partitioning", "Split all group members into two disjoint subsets based on their net balance: Debtors (net < -0.01) and Creditors (net > +0.01). Members within ±0.01 are discarded as settled."),
        ("Step 2: Priority Sorting", "Sort Debtors in descending order of absolute debt. Sort Creditors in descending order of credit. This ensures the largest cash liabilities are matched first."),
        ("Step 3: Greedy Settlement Matching", "Take debtor D with debt A_D and creditor C with credit A_C. Settle amount S = min(A_D, A_C). Record transaction 'D pays C amount $S'. Update remaining balances: A_D = A_D - S, and A_C = A_C - S."),
        ("Step 4: Convergence & Advance", "If D's remaining balance is ≤ 0.01, advance to next debtor. If C's remaining credit is ≤ 0.01, advance to next creditor. Repeat until all participants are fully settled.")
    ]
    t = doc.add_table(rows=1, cols=2)
    format_table(t, [Inches(2.2), Inches(4.3)], ["Phase", "Algorithmic Operation"], algo_steps)

    p = doc.add_paragraph(
        "\nComplexity Analysis:\n"
        "• Time Complexity: O(N log N) where N is the number of members, dominated by the dual sorting of debtors and creditors.\n"
        "• Space Complexity: O(N) auxiliary memory to store sorted queues and transactions.\n"
        "• Theoretical Bound: The maximum number of generated settlement transactions is strictly bounded by (N - 1)."
    )

    add_styled_heading(doc, "1.3 Floating-Point Precision & Penny-Rounding Handling", level=2)
    p = doc.add_paragraph(
        "Standard IEEE-754 floating-point arithmetic introduces rounding anomalies when dividing currency (e.g., $100.00 / 3 = 33.333333...). "
        "A naive split generates $33.33 for three members, causing a 1-cent leak ($99.99 total). "
        "SplitCyber resolves this in backend/app/routers/expenses.py through an Uneven Penny Distributor: "
        "it calculates per_user_amount = round(total / count, 2), computes difference = round(total - (per_user_amount * count), 2), "
        "and injects the difference into the first member's split. Total is strictly preserved to the penny."
    )

    # ------------------ CHAPTER 2: SYSTEM ARCHITECTURE ------------------
    add_styled_heading(doc, "2. System Architecture & Tech Stack", level=1)
    
    stack_data = [
        ("Backend Framework", "FastAPI (Python 3.8+)", "High-throughput asynchronous ASGI web framework offering native OpenAPI/Swagger docs and strict Pydantic contract validation."),
        ("ORM & Data Layer", "SQLAlchemy 2.0", "Enterprise Object-Relational Mapping providing clean relational models, connection pooling, and cross-database query abstraction."),
        ("Primary Database", "MySQL 8.0", "ACID-compliant relational database management system running via PyMySQL driver in containerized production."),
        ("Resilient Fallback", "SQLite 3", "Zero-configuration local database that automatically activates if MySQL is unreachable, ensuring high system fault tolerance."),
        ("Frontend Architecture", "Vanilla HTML5 / CSS3 / ES6", "Lightweight, zero-build Single Page Application featuring Cyber Glassmorphism UI, SVG icons, and dynamic asynchronous DOM binding."),
        ("Testing Suite", "unittest + HTTPX", "Full integration and unit test coverage utilizing FastAPI TestClient for automated contract and balance verification."),
        ("Containerization", "Docker & Docker Compose", "Multi-stage container orchestration bundling application service and database with integrated healthchecks.")
    ]
    t = doc.add_table(rows=1, cols=3)
    format_table(t, [Inches(1.5), Inches(1.8), Inches(3.2)], ["Tier", "Technology", "Architectural Role"], stack_data)

    # ------------------ CHAPTER 3: DATABASE DESIGN ------------------
    add_styled_heading(doc, "3. Database Design & Entity Relationships", level=1)
    p = doc.add_paragraph(
        "The relational schema defined in backend/app/models.py consists of 6 primary entities linked through relational constraints:"
    )

    db_entities = [
        ("users", "id (PK), name, email (UK), avatar_color, created_at", "Stores user identities. Unique index on email prevents duplicate registrations."),
        ("groups", "id (PK), name, category, description, created_at", "Represents an isolated financial group (e.g. Trips, Roommates, Office Expenses)."),
        ("group_members", "id (PK), group_id (FK), user_id (FK), joined_at", "Join entity linking users to groups. Features composite UniqueConstraint('group_id', 'user_id') and ondelete='CASCADE'."),
        ("expenses", "id (PK), group_id (FK), paid_by_id (FK), title, amount, category, split_type, created_at", "Master expense header. Tracks total expenditure, payer, category, and splitting strategy (EQUAL, EXACT, PERCENTAGE)."),
        ("expense_splits", "id (PK), expense_id (FK), user_id (FK), amount, percentage", "Detailed breakdown specifying exactly what each individual participant owes for a given expense."),
        ("settlements", "id (PK), group_id (FK), payer_id (FK), payee_id (FK), amount, notes, created_at", "Records direct cash repayments made outside the platform to reduce outstanding debts between members.")
    ]
    t = doc.add_table(rows=1, cols=3)
    format_table(t, [Inches(1.2), Inches(2.3), Inches(3.0)], ["Table Name", "Columns & Keys", "Business Rules & Relationships"], db_entities)

    add_callout(
        doc,
        "Fault-Tolerant Database Engine Initializer",
        "In backend/app/database.py, the engine attempts to establish a live connection to MySQL. If an OperationalError (such as "
        "wrong password or server offline) is caught, the system logs a warning and seamlessly instantiates an engine connected to "
        "sqlite:///./expense_db.db. The application never crashes on DB connection failure."
    )

    # ------------------ CHAPTER 4: STEP-BY-STEP FLOW ------------------
    add_styled_heading(doc, "4. Step-by-Step Transaction Lifecycle", level=1)
    
    p = doc.add_paragraph(
        "The following operational steps illustrate how data progresses through the application from creation to settlement:"
    )

    steps_list = [
        ("Step 1: User & Group Onboarding", "A user is registered via POST /api/users with their name, unique email, and custom avatar color. A group is formed via POST /api/groups with an initial array of member IDs. The backend populates the group_members associative table."),
        ("Step 2: Adding an Expense with EQUAL Split", "Alice pays $800 for group housing. The system divides $800 across 4 members ($200 each). It commits 1 master record in expenses and 4 detail rows in expense_splits within an atomic database transaction."),
        ("Step 3: Adding an Expense with EXACT Split", "Bob pays $240 for dinner. The request provides an exact split array: [Alice: $60, Bob: $60, Charlie: $60, Diana: $60]. The backend validates |sum(splits) - total| <= 0.05 before committing."),
        ("Step 4: Adding an Expense with PERCENTAGE Split", "Charlie pays $400 for transit passes. Each member is assigned 25%. The backend validates |sum(pct) - 100| <= 0.1, computes amount = total * (pct / 100), and records splits of $100 each."),
        ("Step 5: Querying Balances & Debt Simplification", "Client requests GET /api/groups/{id}/balances. The server queries all expenses and settlements, computes each member's net position, and executes the Greedy Min-Cash-Flow algorithm."),
        ("Step 6: Recording Settlements", "A debtor transfers funds to a creditor and logs it via POST /api/groups/{id}/settlements. The settlement is factored into subsequent balance calculations, reducing remaining debt.")
    ]
    t = doc.add_table(rows=1, cols=2)
    format_table(t, [Inches(2.2), Inches(4.3)], ["Step", "Technical Execution"], steps_list)

    # Concrete Mathematical Walkthrough
    add_styled_heading(doc, "4.1 Concrete Mathematical Simulation", level=2)
    p = doc.add_paragraph(
        "Consider the Tokyo Trip scenario with 4 participants: Alice, Bob, Charlie, and Diana.\n"
        "• Expense 1 (Alice): $800 (Villa, Equal split) -> Alice pays $800, each owes $200.\n"
        "• Expense 2 (Bob): $240 (Banquet, Exact split) -> Bob pays $240, each owes $60.\n"
        "• Expense 3 (Charlie): $400 (Train passes, 25% split) -> Charlie pays $400, each owes $100."
    )

    math_data = [
        ("Alice", "$800.00", "$200 + $60 + $100 = $360.00", "+$440.00", "Creditor"),
        ("Bob", "$240.00", "$200 + $60 + $100 = $360.00", "-$120.00", "Debtor"),
        ("Charlie", "$400.00", "$200 + $60 + $100 = $360.00", "+$40.00", "Creditor"),
        ("Diana", "$0.00", "$200 + $60 + $100 = $360.00", "-$360.00", "Debtor"),
        ("TOTAL", "$1,440.00", "$1,440.00", "$0.00", "Conservation Verified")
    ]
    t = doc.add_table(rows=1, cols=5)
    format_table(t, [Inches(1.0), Inches(1.1), Inches(1.8), Inches(1.2), Inches(1.4)], ["Member", "Total Paid", "Total Share", "Net Balance", "Status"], math_data)

    p = doc.add_paragraph(
        "\nAlgorithmic Resolution of Debts:\n"
        "1. Max Debtor Diana (-$360) matched with Max Creditor Alice (+$440):\n"
        "   -> Diana pays Alice $360.00. (Diana is now fully settled; Alice remaining credit = +$80.00).\n"
        "2. Next Debtor Bob (-$120) matched with Creditor Alice (+$80):\n"
        "   -> Bob pays Alice $80.00. (Alice is now fully settled; Bob remaining debt = -$40.00).\n"
        "3. Remaining Debtor Bob (-$40) matched with Creditor Charlie (+$40):\n"
        "   -> Bob pays Charlie $40.00. (Both Bob and Charlie are now fully settled).\n\n"
        "Result: Entire group settled with exactly 3 transactions instead of 12 pairwise transfers!"
    )

    # ------------------ CHAPTER 5: API SPECIFICATION ------------------
    add_styled_heading(doc, "5. REST API Specification", level=1)
    
    api_data = [
        ("GET", "/api/health", "None", "{ status: 'ok', version: '1.0.0' }", "Health check & uptime probe"),
        ("POST", "/api/users", "{ name, email, avatar_color }", "User object (id, name, email)", "Registers new user profile"),
        ("GET", "/api/users", "None", "List of User objects", "Lists all registered users"),
        ("POST", "/api/groups", "{ name, category, initial_member_ids }", "Group object with member details", "Creates an expense group"),
        ("GET", "/api/groups", "None", "List of Group objects", "Lists all active groups"),
        ("POST", "/api/groups/{id}/members", "{ user_id: int }", "Membership confirmation", "Adds member to existing group"),
        ("POST", "/api/groups/{id}/expenses", "{ title, amount, paid_by_id, split_type, splits }", "Expense object with splits", "Creates expense with split strategy"),
        ("GET", "/api/groups/{id}/expenses", "None", "List of Expense objects", "Retrieves expense history"),
        ("GET", "/api/groups/{id}/balances", "None", "GroupBalanceSummary object", "Calculates net balances & debts"),
        ("POST", "/api/groups/{id}/settlements", "{ payer_id, payee_id, amount, notes }", "Settlement record object", "Logs debt settlement between members")
    ]
    t = doc.add_table(rows=1, cols=5)
    format_table(t, [Inches(0.8), Inches(1.6), Inches(1.4), Inches(1.4), Inches(1.3)], ["Method", "Endpoint", "Request Body", "Response", "Description"], api_data)

    # ------------------ CHAPTER 6: DOCKER DEPLOYMENT ------------------
    add_styled_heading(doc, "6. Containerization & Deployment with Docker", level=1)
    p = doc.add_paragraph(
        "SplitCyber is fully containerized using Docker and Docker Compose for production and local environments:\n"
        "• Dockerfile: Multi-stage build based on python:3.11-slim. It sets unbuffered output (PYTHONUNBUFFERED=1), "
        "configures the Python path (/app/backend), installs dependencies, and incorporates an automated HEALTHCHECK targeting /api/health.\n"
        "• docker-compose.yml: Orchestrates a multi-container environment containing:\n"
        "    1. db Service: Official mysql:8.0 image with persistent volume (mysql_data) and mysqladmin healthchecks.\n"
        "    2. app Service: FastAPI web app mapped to port 8000, configured to wait for db to be healthy before boot."
    )

    add_callout(
        doc,
        "Port Conflict Resolution Architecture",
        "Because developer machines often run a local MySQL service on port 3306, SplitCyber's Docker Compose maps the host port "
        "to 3307:3306. The containerized app interacts with MySQL internally over the Docker network (db:3306), eliminating any "
        "host-level port collisions."
    )

    p = doc.add_paragraph(
        "Docker Command Reference:\n"
        "• Start all services: docker compose up -d\n"
        "• View container logs: docker compose logs -f\n"
        "• Seed demo data inside container: docker exec -it splitcyber_app python seed.py\n"
        "• Stop and tear down services: docker compose down"
    )

    # ------------------ CHAPTER 7: QUALITY ASSURANCE ------------------
    add_styled_heading(doc, "7. Quality Assurance & Automated Testing", level=1)
    p = doc.add_paragraph(
        "The project includes an integration test suite in tests/test_api.py executed via Python's built-in unittest framework:\n"
        "• Test 1 (Health Check): Validates that GET /api/health returns HTTP 200 with service metadata.\n"
        "• Test 2 (End-to-End Financial Flow): Programmatically provisions 3 users, registers an apartment group, records a shared "
        "utility expense ($150 with EQUAL split), validates that net balances correctly show +$100 for the payer and -$50 for each roommate, "
        "records a settlement payment, and verifies that the debts update properly."
    )
    doc.add_paragraph("Command to run tests:\n   python -m unittest tests/test_api.py")

    # ------------------ CHAPTER 8: DIRECTORY BREAKDOWN ------------------
    add_styled_heading(doc, "8. Project File Structure & Responsibilities", level=1)

    files_data = [
        ("backend/app/main.py", "Application root; mounts API routers, configures CORS, and serves static frontend assets."),
        ("backend/app/config.py", "Application settings; loads environment variables for database credentials."),
        ("backend/app/database.py", "SQLAlchemy engine, connection pool, and auto-fallback between MySQL and SQLite."),
        ("backend/app/models.py", "SQLAlchemy ORM models for Users, Groups, GroupMembers, Expenses, Splits, and Settlements."),
        ("backend/app/schemas.py", "Pydantic request and response models enforcing data validation and contract serialization."),
        ("backend/app/services/balance.py", "Core business logic: Net balance computation and Greedy Min-Cash-Flow debt simplification."),
        ("backend/app/routers/", "REST endpoint handlers: users.py, groups.py, expenses.py, balances.py, settlements.py."),
        ("frontend/index.html", "Single-page dashboard interface with stats, group navigation, and expense/debt modals."),
        ("frontend/css/styles.css", "Modern Cyber Glassmorphism stylesheet with responsive breakpoints and custom CSS tokens."),
        ("frontend/js/app.js", "Client-side controller managing state, API fetch requests, modal interactions, and DOM updates."),
        ("Dockerfile & docker-compose.yml", "Container definition and multi-service orchestration for production deployment."),
        ("seed.py", "Utility script to populate sample users, groups, and expenses with diverse split types."),
        ("run.py", "Convenience startup script configuring Python path and launching Uvicorn on port 8000.")
    ]
    t = doc.add_table(rows=1, cols=2)
    format_table(t, [Inches(2.4), Inches(4.1)], ["File / Directory", "Primary Responsibility"], files_data)

    doc.save(output_path)
    print(f"[+] Document successfully generated at: {output_path}")

if __name__ == "__main__":
    out_file = os.path.abspath("SplitCyber_Project_Documentation.docx")
    build_document(out_file)
