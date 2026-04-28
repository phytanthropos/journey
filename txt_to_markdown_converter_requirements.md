# TXT to Markdown Converter Demo — Requirements

## Purpose
Build a small Python demo that converts a plain `.txt` input file into a `.md` output file with readable Markdown formatting applied to simple textual cues.

## Scope
The demo should focus on predictable text-to-Markdown transformations, not full natural-language understanding.

## Expected Input
- Plain UTF-8 text files (`.txt`)
- One note or document per file
- Text may contain simple markers such as:
  - section headers
  - bullet lists
  - numbered lists
  - emphasis cues
  - code snippets
  - quoted text

## Required Markdown Transformations
1. **Title / top-level heading**
   - The first meaningful line may become `# Title` if it is clearly a document title.

2. **Section headers**
   - Lines ending with `:` or lines written in ALL CAPS may become `## Section` or `### Subsection` when they are clearly acting as headings.

3. **Bullet lists**
   - Lines starting with `-`, `*`, or `•` should be normalized to Markdown bullets.

4. **Numbered lists**
   - Lines beginning with `1.`, `2.`, etc. should remain or be normalized to Markdown ordered lists.

5. **Bold emphasis**
   - Text wrapped in double asterisks or surrounded by `**like this**` should render as Markdown bold.
   - If the source uses cues like `BOLD:` or `IMPORTANT:`, the demo may optionally convert the following phrase into bold text.

6. **Italic emphasis**
   - Text wrapped in single asterisks or underscores may render as italic.

7. **Code blocks**
   - Indented blocks or lines explicitly marked as code should be wrapped in fenced code blocks using triple backticks.

8. **Inline code**
   - Short identifiers, commands, or file names may be wrapped in backticks when clearly marked in the source.

9. **Block quotes**
   - Lines beginning with `>` should remain Markdown block quotes.

10. **Paragraph cleanup**
   - Preserve line breaks where useful.
   - Collapse excessive blank lines.
   - Trim trailing whitespace.

## Non-Goals
- Do not attempt semantic rewriting of the content.
- Do not invent new headings or reorder sections.
- Do not parse arbitrary rich-text formats.
- Do not require external libraries beyond the Python standard library unless necessary for the demo.

## CLI Behavior
- Accept one input `.txt` path and one optional output `.md` path.
- If no output path is provided, write alongside the input using the same basename.
- Print a short success message with the output location.

## Suggested Acceptance Criteria
- Running the script on a sample text file produces a valid `.md` file.
- Lists, headings, quotes, and code blocks are converted consistently.
- The output remains readable even when the input contains no markup cues.

## Example
### Source
```text
PROJECT NOTES:
- gather requirements
- build converter
IMPORTANT: keep output readable
```

### Markdown Output
```md
## PROJECT NOTES
- gather requirements
- build converter
**IMPORTANT:** keep output readable
```

## Demo Definition
This should be a compact, understandable proof-of-concept that demonstrates text normalization and basic Markdown styling rather than a production-grade document parser.
