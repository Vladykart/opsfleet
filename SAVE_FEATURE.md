# 💾 Save Feature - Data Export with Pandas

The enhanced CLI now supports saving conversations in multiple formats using pandas.

## Usage

### Method 1: Natural Language (NEW!)
Just ask naturally - the agent will detect and save automatically:
```
save this conversation
save the data as csv
export this to json
download this as excel
can you save this?
please save the conversation as markdown
```

### Method 2: Command
```bash
/save          # Defaults to CSV format
/save csv      # CSV format (Excel-compatible)
/save json     # JSON format
/save excel    # Native Excel (.xlsx)
/save md       # Markdown format
/save txt      # Plain text format
```

## Export Formats

### 1. CSV (Comma-Separated Values)
**Best for:** Excel, data analysis, spreadsheets

```bash
💬 You › /save csv
```

**Output:** `sessions/conversation_20251111_233045.csv`

**Contains:**
- time
- query
- response
- success
- elapsed

### 2. JSON (JavaScript Object Notation)
**Best for:** APIs, web applications, data interchange

```bash
💬 You › /save json
```

**Output:** `sessions/conversation_20251111_233045.json`

**Format:**
```json
[
  {
    "time": "23:30:45",
    "query": "How many users?",
    "response": "There are 100,000 users",
    "success": true,
    "elapsed": 2.34
  }
]
```

### 3. Excel (Native .xlsx)
**Best for:** Business reports, data analysis, presentations

```bash
💬 You › /save excel
```

**Output:** `sessions/conversation_20251111_233045.xlsx`

**Features:**
- Native Excel format
- Preserves data types
- Ready for pivot tables
- Compatible with Excel, Google Sheets

### 4. Markdown (.md)
**Best for:** Documentation, GitHub, wikis

```bash
💬 You › /save md
```

**Output:** `sessions/conversation_20251111_233045.md`

**Format:**
```markdown
# OpsFleet Conversation - 20251111_233045

## Query 1 (23:30:45)

**User:** How many users are in the database?

**Assistant:**

There are 100,000 users in the database.

*Time: 2.34s | Status: ✅*

---
```

### 5. Plain Text (.txt)
**Best for:** Simple logs, email, basic documentation

```bash
💬 You › /save txt
```

**Output:** `sessions/conversation_20251111_233045.txt`

**Format:**
```
OpsFleet Conversation - 20251111_233045
======================================================================

[23:30:45] Query #1
User: How many users are in the database?
