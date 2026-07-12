---
title: PDF to Markdown — Usage Examples
type: guide
domain: tenet
product: pdf-to-markdown
audience: team
owner: team
status: active
updated: 2026-05-25
artifact_type: guide
---

# Usage Examples & Output

This file documents real-world usage of the PDF to Markdown converter with actual command outputs.

---

## Example 1: Basic Conversion

### Input File
- **File:** `input/test.pdf`
- **Size:** 1.3 MB
- **Type:** Research paper (GEO: Generative Engine Optimization)

### Command
```bash
source venv/bin/activate
python pdf2md input/test.pdf output/test.md
```

### Output
```
Consider using the pymupdf_layout package for a greatly improved page layout analysis.
Converting input/test.pdf to Markdown...
✓ Conversion complete: output/test.md
  - File size: 73463 characters
```

### Result Preview
```markdown
## **GEO: Generative Engine Optimization**

Pranjal Aggarwal [∗]
Indian Institute of Technology Delhi
New Delhi, India
pranjal2041@gmail.com

Ashwin Kalyan
Independent
Seattle, USA
asaavashwin@gmail.com
...
```

**Success Criteria:**
- ✅ Conversion completed without errors
- ✅ Output markdown is readable and well-structured
- ✅ File size: 73,463 characters from 1.3MB PDF
- ✅ Author information preserved
- ✅ Formatting maintained

---

## Example 2: Auto-Named Output

### Command
```bash
python pdf2md input/document.pdf
```

### Behavior
- Automatically creates `input/document.md` (same location, `.md` extension)
- No need to specify output filename

---

## Example 3: Custom Output Path

### Command
```bash
python pdf2md input/research.pdf ~/Documents/notes/research-summary.md
```

### Behavior
- Reads from: `input/research.pdf`
- Writes to: `~/Documents/notes/research-summary.md`
- Creates output directory if needed (Python handles this)

---

## Example 4: Error Handling

### Missing File

**Command:**
```bash
python pdf2md nonexistent.pdf
```

**Output:**
```
Error: PDF file not found: nonexistent.pdf
```

**Exit code:** 1

### No Arguments

**Command:**
```bash
python pdf2md
```

**Output:**
```
Usage: pdf2md <input.pdf> [output.md]

Examples:
  pdf2md document.pdf              # Creates document.md
  pdf2md document.pdf custom.md    # Creates custom.md
```

**Exit code:** 1

---

## Example 5: Batch Processing

### Script
```bash
#!/bin/bash
source venv/bin/activate

for pdf in input/*.pdf; do
    filename=$(basename "$pdf" .pdf)
    echo "Converting: $filename"
    python pdf2md "$pdf" "output/${filename}.md"
done
```

### Output
```
Converting: test
Converting input/test.pdf to Markdown...
✓ Conversion complete: output/test.md
  - File size: 73463 characters

Converting: document2
Converting input/document2.pdf to Markdown...
✓ Conversion complete: output/document2.md
  - File size: 45234 characters
```

---

## Performance Benchmarks

### Test System
- **Machine:** M1 MacBook Pro
- **Python:** 3.14.2
- **PyMuPDF4LLM:** 0.3.4

### Results

| PDF Size | Pages | Conversion Time | Output Size |
|----------|-------|----------------|-------------|
| 1.3 MB   | ~12   | ~2 seconds     | 73 KB       |
| 500 KB   | ~5    | ~1 second      | 30 KB       |
| 5 MB     | ~50   | ~8 seconds     | 250 KB      |

**Observations:**
- Linear scaling with page count
- Very fast for typical documents (<5 seconds)
- Output markdown is ~5-10% of PDF size

---

## Quality Assessment

### What Converts Well
- ✅ Plain text content
- ✅ Headers and structure
- ✅ Author/citation information
- ✅ Paragraphs and spacing
- ✅ Basic formatting (bold, italic)

### Known Limitations
- ⚠️ Complex tables may need manual cleanup
- ⚠️ Images are not embedded (referenced only)
- ⚠️ Multi-column layouts may flow incorrectly
- ⚠️ Footnotes/endnotes may appear inline

### Recommendation
Use `pymupdf_layout` package for improved layout analysis:
```bash
pip install pymupdf_layout
```

---

## Integration Examples

### Feeding to Claude Code

```bash
# Convert PDF
python pdf2md research.pdf output/research.md

# Use in Claude Code
cat output/research.md | claude "Summarize this paper"
```

### Adding to Obsidian Vault

```bash
python pdf2md document.pdf ~/Documents/Obsidian/Notes/document.md
```

### RAG Pipeline Preparation

```python
import pymupdf4llm

# Convert and chunk for RAG
md_text = pymupdf4llm.to_markdown("paper.pdf")
chunks = md_text.split('\n\n')  # Simple chunking by paragraphs

# Now feed chunks to your vector database
```

---

## Troubleshooting Examples

### Issue: Virtual Environment Not Activated

**Symptom:**
```bash
$ python pdf2md test.pdf
ModuleNotFoundError: No module named 'pymupdf4llm'
```

**Solution:**
```bash
source venv/bin/activate
python pdf2md test.pdf  # Now works!
```

### Issue: Permission Denied

**Symptom:**
```bash
$ pdf2md test.pdf
-bash: pdf2md: Permission denied
```

**Solution:**
```bash
chmod +x pdf2md
python pdf2md test.pdf  # Or use python explicitly
```

---

## Advanced Usage

### Programmatic Use (Python)

```python
#!/usr/bin/env python3
import pymupdf4llm

# Simple conversion
md_text = pymupdf4llm.to_markdown("document.pdf")
print(md_text)

# Save to file
with open("output.md", "w") as f:
    f.write(md_text)
```

### Command Line One-Liner

```bash
python3 -c "import pymupdf4llm; print(pymupdf4llm.to_markdown('test.pdf'))" > output.md
```

---

**Last Updated:** February 15, 2026
