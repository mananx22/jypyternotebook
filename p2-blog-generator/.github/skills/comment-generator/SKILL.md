---
name: comment-generator
description: generate comments of document/code
---

<!-- Tip: Use /create-skill in chat to generate content with agent assistance -->

# Skill: Code Commenting & Documentation

## Purpose
Add clear, structured, and maintainable comments to any Python codebase.
This skill covers how to write comments, what level of detail to include,
and how to format them for maximum readability across any project.

---

## Comment Types & When to Use Them

### 1. File Header Comment
Place at the very top of every file. Describes what the file contains.

```
# =============================================================================
# filename.py
# Short one-line description of what this file does.
# =============================================================================
```

### 2. Section Headers
Use to group related code blocks within a file.

```
# --- SECTION NAME -----------------------------------------------------------
```

### 3. Import Comments
Add a brief comment after each import (or group of imports) explaining
what the imported module/class is used for in this file.

```
# Description of what this import provides.
from module import ClassName
```

### 4. Class Docstrings
Use hash-style comments (`# """..."""`) for classes. Include:
- What the class does
- Key responsibilities
- Usage example (if non-trivial)

```
class MyClass:
    # """
    # Short description of the class.
    #
    # Longer explanation if needed, covering key behaviors,
    # design decisions, or important caveats.
    #
    # Usage:
    #     obj = MyClass(args)
    #     obj.do_something()
    # """
```

### 5. Method/Function Docstrings
Use hash-style comments (`# """..."""`) for every method and function. Include:
- What the method does
- Args: parameter name, type, and purpose
- Returns: what it returns and its type
- Any side effects or raised exceptions

```
    def my_method(self, param):
        # """
        # Short description of what this method does.
        #
        # Args:
        #     param (type): Description of this parameter.
        #
        # Returns:
        #     type: Description of the return value.
        # """
```

### 6. Inline Comments
Use single-line `#` comments on the line above (not beside) a statement.
Explain **why**, not **what** — the code itself shows what happens.

```
# Validate input before processing to avoid downstream errors.
if not value:
    return None
```

### 7. Section Divider Comments
Use for grouping related operations within a method.

```
# --- STEP LABEL ---
```

---

## Formatting Rules

### Line Length
- Keep comment lines to ~79 characters max.
- Break long sentences across multiple lines with proper indentation.

### Indentation
- Comments inside a class/method must match the indentation level of
  the code they describe.
- Multi-line comments: align continuation lines with the first line's text.

```
# This is a long comment that wraps to
# the next line, aligned properly.
```

### Spacing
- Leave one blank line before and after a comment block.
- Leave one blank line between a section header and the code below it.
- No blank line between a single-line comment and the code it describes.

### Multi-line Comment Style
For docstrings, use hash-style comments with `"""` markers:
```
# """
# First line of the description.
#
# Second paragraph if needed.
# """
```

For multi-line `#` comments, prefix each line with `# `:
```
# First line of the comment.
# Second line of the comment.
# Third line of the comment.
```

### Converting Docstrings to Hash Comments
Always convert triple-quoted docstrings to hash-style comments.
This keeps all comments uniform as single-line `#` comments while
preserving the `"""` markers for visual clarity:
- Replace opening `"""` with `# """`
- Prefix every content line with `# ` (keep blank lines as `#`)
- Replace closing `"""` with `# """`
- Preserve all original indentation, line breaks, and text exactly.

---

## Level of Detail Guide

| Situation | Detail Level |
|---|---|
| Public API / library code | Full docstrings with Args, Returns, Examples |
| Internal project code | Docstrings with Args and Returns at minimum |
| Complex algorithms | Inline comments explaining each logical step |
| Simple/self-explanatory code | Brief one-liner or no comment |
| Bug workarounds / hacks | Detailed comment explaining WHY the workaround exists |
| TODO / FIXME | Comment with context and ideally a ticket reference |

---

## What NOT to Do

- Don't state the obvious: `x = 5  # set x to 5` → useless.
- Don't repeat the code in words: `return True  # return True` → useless.
- Don't leave outdated comments — delete or update them when code changes.
- Don't use comments to disable code — use version control instead.
- Don't write novel-length comments — if you need that much explanation,
  consider splitting the function or adding external documentation.

---

## Quick Checklist

- [ ] Every file has a header comment
- [ ] Every class has a docstring
- [ ] Every method/function has a docstring with Args and Returns
- [ ] Complex logic has inline "why" comments
- [ ] Section headers group related code
- [ ] Import comments explain non-obvious dependencies
- [ ] No outdated or misleading comments remain
- [ ] Consistent formatting throughout the file
