# RegexQ

**A declarative regex query builder for your terminal.** Write regex like you think about patterns — not like you're debugging line noise.

```bash
# Instead of writing: ^(?P<user>\w+)@(?P<domain>\w+)\.[a-zA-Z]{2,}$
# Write this:
regexq start named:user word end_named literal '@' named:domain word end_named literal '.' letters end
```

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/downloads/)

---

## Why RegexQ?

Regex is powerful but unreadable. RegexQ gives you a **composable, left-to-right vocabulary** for building patterns. Every operation maps to a clear regex concept — no guessing, no magic, no NLP.

```bash
# Match a price like $19.99 or $5
regexq literal '$' digits:1,6 maybe '.' digits:2,2
# → \$\d{1,6}\.?\d{2,2}

# Match CSV fields containing a comma inside double quotes
regexq literal '"' anything_but '"' literal ',' anything_but '"' literal '"'
# → "[^"]*,[^"]*"

# Validate an ISO date
regexq start date end
# → ^\d{4}-\d{2}-\d{2}$
```

## Installation

RegexQ is a single Python file with **zero dependencies** (just Python 3.10+ standard library).

### Quick Install (Recommended)

Use the one-line installer:

```bash
# Clone and install
git clone https://github.com/astroteam-ir/regexq.git
cd regexq
./install.sh
```

The installer will:
- Check your Python version (requires 3.10+)
- Install regexq to `/usr/local/bin` or `~/.local/bin`
- Make it executable and ready to use
- Guide you if PATH configuration is needed

### Manual Installation

If you prefer manual installation:

```bash
# Clone the repo
git clone https://github.com/astroteam-ir/regexq.git
cd regexq

# Make it executable
chmod +x regexq.py

# Option 1: Symlink into PATH
ln -s "$(pwd)/regexq.py" /usr/local/bin/regexq

# Option 2: Copy to a directory in PATH
cp regexq.py ~/.local/bin/regexq

# Option 3: Just alias it
echo 'alias regexq="python3 /path/to/regexq.py"' >> ~/.bashrc
```

## Quick Start

```bash
# Basic: match lines starting with "ERROR"
regexq start literal 'ERROR' anything
# → ^ERROR.*

# Named capture groups
regexq named:year digits:4,4 end_named literal '-' named:month digits:2,2 end_named literal '-' named:day digits:2,2 end_named
# → (?P<year>\d{4,4})-(?P<month>\d{2,2})-(?P<day>\d{2,2})

# Alternatives
regexq start either 'GET,POST,PUT,DELETE' space
# → ^(?:GET|POST|PUT|DELETE)\s

# Test against real strings
regexq --test start literal 'Hello' space word end -- 'Hello World' 'Hello' 'Hello 123' 'Goodbye World'
# Pattern: ^Hello\s\w+$
#
#   ✓ 'Hello World' → matched 'Hello World'
#   ✗ 'Hello' → no match
#   ✓ 'Hello 123' → matched 'Hello 123'
#   ✗ 'Goodbye World' → no match

# Explain what a pattern does
regexq --explain start word literal '@' word literal '.' letters end
```

## Full Operations Reference

### Anchors

| Operation | Output | Description |
|-----------|--------|-------------|
| `start` | `^` | Start of string |
| `end` | `$` | End of string |
| `boundary` | `\b` | Word boundary |

### Literals & Characters

| Operation | Output | Description |
|-----------|--------|-------------|
| `literal <text>` | escaped text | Literal match (auto-escaped) |
| `lit <text>` | escaped text | Alias for `literal` |
| `any_char` / `char` | `.` | Any single character |
| `one_of <chars>` | `[chars]` | Match one of the characters |
| `none_of <chars>` | `[^chars]` | Match none of the characters |
| `range:a-z` | `[a-z]` | Character range |

### Character Classes

| Operation | Output | Description |
|-----------|--------|-------------|
| `digit` | `\d` | Single digit |
| `digits` | `\d{1,}` | One or more digits |
| `digits:3` | `\d{3,}` | At least 3 digits |
| `digits:2,5` | `\d{2,5}` | Between 2 and 5 digits |
| `word` | `\w+` | Word characters |
| `word_char` | `\w` | Single word character |
| `letter` | `[a-zA-Z]` | Single letter |
| `letters` | `[a-zA-Z]+` | One or more letters |
| `lowercase` | `[a-z]+` | Lowercase letters |
| `uppercase` | `[A-Z]+` | Uppercase letters |
| `space` | `\s` | Single whitespace |
| `spaces` / `whitespace` | `\s+` | One or more whitespace |
| `tab` | `\t` | Tab character |
| `newline` | `\n` | Newline |

### Wildcards & Patterns

| Operation | Output | Description |
|-----------|--------|-------------|
| `anything` | `.*` | Zero or more of anything |
| `something` | `.+` | One or more of anything |
| `anything_but <c>` | `[^c]*` | Anything except these chars |
| `something_but <c>` | `[^c]+` | One+ except these chars |
| `until <text>` | `(?:(?!t).)*t` | Match through text |
| `before <text>` | `(?:(?!t).)*` | Match up to text (exclusive) |
| `between:<a>,<b>` | `a(.*?)b` | Content between delimiters |

### Quantifiers

| Operation | Output | Description |
|-----------|--------|-------------|
| `maybe <text>` | `(text)?` | Optional literal |
| `repeat:3` | `{3}` | Exactly 3 times |
| `at_least:2` | `{2,}` | At least 2 times |
| `times:2,5` | `{2,5}` | Between 2 and 5 times |
| `one_or_more` | `+` | One or more |
| `zero_or_more` | `*` | Zero or more |
| `optional` | `?` | Make previous optional |
| `lazy` | `?` | Make previous non-greedy |

### Groups

| Operation | Output | Description |
|-----------|--------|-------------|
| `group` / `group_start` | `(` | Start capturing group |
| `end_group` / `group_end` | `)` | End capturing group |
| `named:<name>` | `(?P<name>` | Start named group |
| `end_named` | `)` | End named group |
| `either <a,b,c>` | `(?:a\|b\|c)` | Match one of alternatives |

### Lookaround

| Operation | Output | Description |
|-----------|--------|-------------|
| `if_followed_by <t>` | `(?=t)` | Positive lookahead |
| `if_not_followed_by <t>` | `(?!t)` | Negative lookahead |
| `if_preceded_by <t>` | `(?<=t)` | Positive lookbehind |
| `if_not_preceded_by <t>` | `(?<!t)` | Negative lookbehind |

### Presets (Common Patterns)

| Operation | Matches |
|-----------|---------|
| `email` | Email addresses |
| `url` | HTTP/HTTPS URLs |
| `ipv4` / `ip` | IPv4 addresses |
| `date` | ISO dates (YYYY-MM-DD) |
| `time` | 24h time (HH:MM[:SS]) |
| `phone` | Phone numbers |
| `hex_color` / `color` | Hex colors (#RGB / #RRGGBB) |
| `integer` | Integers (with optional `-`) |
| `decimal` | Decimal numbers |
| `quoted` | Double-quoted strings |
| `quoted:'` | Single-quoted strings |
| `line` | Entire line (`^.*$`) |

### Flags

| Operation | Output | Description |
|-----------|--------|-------------|
| `ignorecase` | `(?i)` | Case-insensitive matching |
| `multiline` | `(?m)` | `^`/`$` match line boundaries |
| `dotall` | `(?s)` | `.` matches newline |

### Advanced

| Operation | Description |
|-----------|-------------|
| `raw <regex>` | Inject raw regex (no escaping) |

## Real-World Examples

```bash
# Log parsing: extract timestamp, level, message
regexq literal '[' named:ts until ']' end_named space named:level either 'INFO,WARN,ERROR' end_named space named:msg something end_named
# → \[(?P<ts>(?:(?!\]).)*\])\s(?P<level>(?:INFO|WARN|ERROR))(?P<msg>.+)

# Extract HTML tag attributes
regexq literal '<' word spaces before '>' literal '>'
# → <\w+\s+(?:(?!>).)*>

# Password validation: 8+ chars, must contain digit
regexq start if_followed_by '.*\d' raw '.{8,}' end
# Combine raw for complex assertions

# Match a hex color
regexq start hex_color end
# → ^#(?:[0-9a-fA-F]{3}){1,2}$

# Pipe to grep
regexq start literal 'ERROR' anything | xargs -I{} grep -E '{}' server.log

# Pipe to clipboard (macOS)
regexq start email end | pbcopy
```

## Modes

### Default Mode
Outputs the regex string to stdout — perfect for piping.

### Test Mode (`--test`)
Validates a pattern against sample strings:
```bash
regexq --test start digits end -- '123' 'abc' '45.6'
```

### Explain Mode (`--explain`)
Shows a step-by-step breakdown of the generated pattern:
```bash
regexq --explain start word literal '@' word literal '.' letters end
```

## Design Principles

1. **Deterministic** — Same input always produces the same regex. No AI, no guessing.
2. **Composable** — Operations chain left to right, just like regex reads.
3. **Safe** — All user input is auto-escaped. Use `raw` only when you mean it.
4. **Zero dependencies** — Single Python file, stdlib only.
5. **Unix-friendly** — Outputs to stdout, plays well with pipes.

## Developer

**Aria Seyedahmadi** — [astroteam.ir](https://astroteam.ir)

## License

MIT License — see [LICENSE](LICENSE) for details.
