#!/usr/bin/env python3
"""
RegexQ — A Declarative Regex Query Builder

Write regex like you think about patterns, not like you're debugging line noise.

Author: Aria Seyedahmadi (astroteam.ir)
License: MIT
"""

import sys
import re
from typing import Optional

__version__ = "2.0.0"
__author__ = "Aria Seyedahmadi"

# ─── Helpers ────────────────────────────────────────────────────────────────────

SPECIAL = set(r"\.^$*+?{}[]|()")


def esc(text: str) -> str:
    """Escape regex special characters in a literal string."""
    return "".join(f"\\{c}" if c in SPECIAL else c for c in text)


def esc_class(text: str) -> str:
    """Escape characters for use inside a character class [...]."""
    special_in_class = set(r"]\^-")
    return "".join(f"\\{c}" if c in special_in_class else c for c in text)


# ─── Builder ────────────────────────────────────────────────────────────────────


class RegexBuilder:
    """Accumulates regex fragments from parsed operations."""

    def __init__(self):
        self._parts: list[str] = []

    def _add(self, fragment: str) -> "RegexBuilder":
        self._parts.append(fragment)
        return self

    # ── Anchors ──────────────────────────────────────────────────────────────

    def start(self):
        return self._add("^")

    def end(self):
        return self._add("$")

    def boundary(self):
        return self._add(r"\b")

    # ── Literals & Character Classes ─────────────────────────────────────────

    def literal(self, text: str):
        return self._add(esc(text))

    def any_char(self):
        return self._add(".")

    def one_of(self, chars: str):
        return self._add(f"[{esc_class(chars)}]")

    def none_of(self, chars: str):
        return self._add(f"[^{esc_class(chars)}]")

    def range(self, start: str, end: str):
        return self._add(f"[{esc_class(start)}-{esc_class(end)}]")

    # ── Shorthand Classes ────────────────────────────────────────────────────

    def digit(self):
        return self._add(r"\d")

    def digits(self, min_: int = 1, max_: Optional[int] = None):
        if max_ is not None:
            return self._add(rf"\d{{{min_},{max_}}}")
        return self._add(rf"\d{{{min_},}}")

    def word(self):
        return self._add(r"\w+")

    def word_char(self):
        return self._add(r"\w")

    def letter(self):
        return self._add("[a-zA-Z]")

    def letters(self):
        return self._add("[a-zA-Z]+")

    def lowercase(self):
        return self._add("[a-z]+")

    def uppercase(self):
        return self._add("[A-Z]+")

    def space(self):
        return self._add(r"\s")

    def spaces(self):
        return self._add(r"\s+")

    def whitespace(self):
        return self._add(r"\s+")

    def tab(self):
        return self._add(r"\t")

    def newline(self):
        return self._add(r"\n")

    # ── Wildcards & Patterns ─────────────────────────────────────────────────

    def anything(self):
        return self._add(".*")

    def something(self):
        return self._add(".+")

    def anything_but(self, chars: str):
        return self._add(f"[^{esc_class(chars)}]*")

    def something_but(self, chars: str):
        return self._add(f"[^{esc_class(chars)}]+")

    def until(self, text: str):
        """Match everything up to and including `text`."""
        e = esc(text)
        return self._add(f"(?:(?!{e}).)*{e}")

    def before(self, text: str):
        """Match everything up to (but not including) `text`."""
        e = esc(text)
        return self._add(f"(?:(?!{e}).)*")

    def between(self, open_: str, close_: str):
        """Match content between two delimiters (non-greedy)."""
        return self._add(f"{esc(open_)}(.*?){esc(close_)}")

    # ── Quantifiers ──────────────────────────────────────────────────────────

    def maybe(self, text: str):
        """Make a literal optional."""
        e = esc(text)
        if len(text) == 1:
            return self._add(f"{e}?")
        return self._add(f"(?:{e})?")

    def repeat(self, n: int):
        """Repeat the previous token exactly n times."""
        return self._add(f"{{{n}}}")

    def at_least(self, n: int):
        """Previous token at least n times."""
        return self._add(f"{{{n},}}")

    def between_times(self, a: int, b: int):
        """Previous token between a and b times."""
        return self._add(f"{{{a},{b}}}")

    def one_or_more(self):
        return self._add("+")

    def zero_or_more(self):
        return self._add("*")

    def optional(self):
        return self._add("?")

    def lazy(self):
        return self._add("?")

    # ── Groups ───────────────────────────────────────────────────────────────

    def group_start(self):
        return self._add("(")

    def group_end(self):
        return self._add(")")

    def named_start(self, name: str):
        return self._add(f"(?P<{name}>")

    def named_end(self):
        return self._add(")")

    def either(self, *options: str):
        escaped = [esc(o) for o in options]
        return self._add(f"(?:{'|'.join(escaped)})")

    def either_raw(self, *options: str):
        return self._add(f"(?:{'|'.join(options)})")

    # ── Lookaround ───────────────────────────────────────────────────────────

    def if_followed_by(self, text: str):
        return self._add(f"(?={esc(text)})")

    def if_not_followed_by(self, text: str):
        return self._add(f"(?!{esc(text)})")

    def if_preceded_by(self, text: str):
        return self._add(f"(?<={esc(text)})")

    def if_not_preceded_by(self, text: str):
        return self._add(f"(?<!{esc(text)})")

    # ── Common Patterns (Presets) ────────────────────────────────────────────

    def email(self):
        return self._add(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

    def url(self):
        return self._add(r"https?://[^\s/$.?#].[^\s]*")

    def ipv4(self):
        octet = r"(?:25[0-5]|2[0-4]\d|[01]?\d\d?)"
        return self._add(rf"{octet}\.{octet}\.{octet}\.{octet}")

    def date_iso(self):
        return self._add(r"\d{4}-\d{2}-\d{2}")

    def time_24h(self):
        return self._add(r"(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?")

    def phone(self):
        return self._add(r"[\+]?[\d\s\-\(\)]{7,15}")

    def hex_color(self):
        return self._add(r"#(?:[0-9a-fA-F]{3}){1,2}")

    def integer(self):
        return self._add(r"-?\d+")

    def decimal(self):
        return self._add(r"-?\d+\.?\d*")

    def quoted(self, quote: str = '"'):
        q = esc(quote)
        return self._add(f'{q}[^{esc_class(quote)}]*{q}')

    def line(self):
        return self._add(r"^.*$")

    # ── Flags ────────────────────────────────────────────────────────────────

    def flag_ignorecase(self):
        self._parts.insert(0, "(?i)")
        return self

    def flag_multiline(self):
        self._parts.insert(0, "(?m)")
        return self

    def flag_dotall(self):
        self._parts.insert(0, "(?s)")
        return self

    # ── Output ───────────────────────────────────────────────────────────────

    def build(self) -> str:
        return "".join(self._parts)


# ─── CLI Parser ─────────────────────────────────────────────────────────────────

# Map of operation → (number_of_extra_args,)
# None means the handler will figure out the args itself.
OPERATIONS = {
    # Anchors
    "start":          0,
    "end":            0,
    "boundary":       0,
    # Literals
    "literal":        1,
    "lit":            1,   # alias
    "any_char":       0,
    "char":           0,   # alias
    "one_of":         1,
    "none_of":        1,
    "range":          1,   # expects "a-z" style
    # Shorthand classes
    "digit":          0,
    "digits":         0,   # can also be digits:2 or digits:2,5
    "word":           0,
    "word_char":      0,
    "letter":         0,
    "letters":        0,
    "lowercase":      0,
    "uppercase":      0,
    "space":          0,
    "spaces":         0,
    "whitespace":     0,
    "tab":            0,
    "newline":        0,
    # Wildcards
    "anything":       0,
    "something":      0,
    "anything_but":   1,
    "something_but":  1,
    "until":          1,
    "before":         1,
    "between":        1,   # expects "open,close"
    # Quantifiers
    "maybe":          1,
    "repeat":         1,
    "at_least":       1,
    "times":          1,   # "2,5" or "3"
    "one_or_more":    0,
    "zero_or_more":   0,
    "optional":       0,
    "lazy":           0,
    # Groups
    "group":          0,   # alias for group_start
    "end_group":      0,   # alias for group_end
    "group_start":    0,
    "group_end":      0,
    "named":          1,   # named:name or named <name>
    "end_named":      0,
    "either":         1,   # comma-separated
    # Lookaround
    "if_followed_by":       1,
    "if_not_followed_by":   1,
    "if_preceded_by":       1,
    "if_not_preceded_by":   1,
    # Presets
    "email":          0,
    "url":            0,
    "ipv4":           0,
    "ip":             0,   # alias
    "date":           0,
    "time":           0,
    "phone":          0,
    "hex_color":      0,
    "color":          0,   # alias
    "integer":        0,
    "decimal":        0,
    "quoted":         0,   # can also be quoted:' for single-quote
    "line":           0,
    # Flags
    "ignorecase":     0,
    "multiline":      0,
    "dotall":         0,
    # Raw injection (advanced)
    "raw":            1,
}


def parse_args(args: list[str]) -> str:
    builder = RegexBuilder()
    i = 0

    while i < len(args):
        raw_token = args[i]

        # Handle colon-style parameters: digits:2,5 or named:id or quoted:'
        token = raw_token
        colon_arg = None
        if ":" in raw_token:
            token, colon_arg = raw_token.split(":", 1)

        # Resolve aliases
        aliases = {
            "lit": "literal",
            "char": "any_char",
            "ip": "ipv4",
            "color": "hex_color",
            "group": "group_start",
            "end_group": "group_end",
            "end_named": "named_end",
        }
        token = aliases.get(token, token)

        if token not in OPERATIONS and raw_token not in OPERATIONS:
            sys.exit(f"Error: Unknown operation '{raw_token}'\n"
                     f"Run 'regexq --help' to see available operations.")

        # ── Dispatch ─────────────────────────────────────────────────────────

        # Anchors
        if token == "start":
            builder.start()
        elif token == "end":
            builder.end()
        elif token == "boundary":
            builder.boundary()

        # Literals
        elif token == "literal":
            if colon_arg:
                builder.literal(colon_arg)
            else:
                i += 1
                builder.literal(args[i])
        elif token == "any_char":
            builder.any_char()
        elif token == "one_of":
            i += 1
            builder.one_of(args[i])
        elif token == "none_of":
            i += 1
            builder.none_of(args[i])
        elif token == "range":
            if colon_arg:
                a, b = colon_arg.split("-", 1)
            else:
                i += 1
                a, b = args[i].split("-", 1)
            builder.range(a, b)

        # Shorthand classes
        elif token == "digit":
            builder.digit()
        elif token == "digits":
            if colon_arg:
                parts = colon_arg.split(",")
                if len(parts) == 2:
                    builder.digits(int(parts[0]), int(parts[1]))
                else:
                    builder.digits(int(parts[0]))
            else:
                builder.digits()
        elif token == "word":
            builder.word()
        elif token == "word_char":
            builder.word_char()
        elif token == "letter":
            builder.letter()
        elif token == "letters":
            builder.letters()
        elif token == "lowercase":
            builder.lowercase()
        elif token == "uppercase":
            builder.uppercase()
        elif token == "space":
            builder.space()
        elif token == "spaces":
            builder.spaces()
        elif token == "whitespace":
            builder.whitespace()
        elif token == "tab":
            builder.tab()
        elif token == "newline":
            builder.newline()

        # Wildcards
        elif token == "anything":
            builder.anything()
        elif token == "something":
            builder.something()
        elif token == "anything_but":
            i += 1
            builder.anything_but(args[i])
        elif token == "something_but":
            i += 1
            builder.something_but(args[i])
        elif token == "until":
            i += 1
            builder.until(args[i])
        elif token == "before":
            i += 1
            builder.before(args[i])
        elif token == "between":
            if colon_arg:
                o, c = colon_arg.split(",", 1)
            else:
                i += 1
                o, c = args[i].split(",", 1)
            builder.between(o, c)

        # Quantifiers
        elif token == "maybe":
            if colon_arg:
                builder.maybe(colon_arg)
            else:
                i += 1
                builder.maybe(args[i])
        elif token == "repeat":
            n = int(colon_arg) if colon_arg else int(args[(i := i + 1)])
            builder.repeat(n)
        elif token == "at_least":
            n = int(colon_arg) if colon_arg else int(args[(i := i + 1)])
            builder.at_least(n)
        elif token == "times":
            val = colon_arg if colon_arg else args[(i := i + 1)]
            parts = val.split(",")
            if len(parts) == 2:
                builder.between_times(int(parts[0]), int(parts[1]))
            else:
                builder.repeat(int(parts[0]))
        elif token == "one_or_more":
            builder.one_or_more()
        elif token == "zero_or_more":
            builder.zero_or_more()
        elif token == "optional":
            builder.optional()
        elif token == "lazy":
            builder.lazy()

        # Groups
        elif token == "group_start":
            builder.group_start()
        elif token == "group_end":
            builder.group_end()
        elif token == "named":
            name = colon_arg if colon_arg else args[(i := i + 1)]
            builder.named_start(name)
        elif token == "named_end":
            builder.named_end()
        elif token == "either":
            if colon_arg:
                options = colon_arg.split(",")
            else:
                i += 1
                options = args[i].split(",")
            builder.either(*options)

        # Lookaround
        elif token == "if_followed_by":
            i += 1
            builder.if_followed_by(args[i])
        elif token == "if_not_followed_by":
            i += 1
            builder.if_not_followed_by(args[i])
        elif token == "if_preceded_by":
            i += 1
            builder.if_preceded_by(args[i])
        elif token == "if_not_preceded_by":
            i += 1
            builder.if_not_preceded_by(args[i])

        # Presets
        elif token == "email":
            builder.email()
        elif token == "url":
            builder.url()
        elif token == "ipv4":
            builder.ipv4()
        elif token == "date":
            builder.date_iso()
        elif token == "time":
            builder.time_24h()
        elif token == "phone":
            builder.phone()
        elif token == "hex_color":
            builder.hex_color()
        elif token == "integer":
            builder.integer()
        elif token == "decimal":
            builder.decimal()
        elif token == "quoted":
            q = colon_arg if colon_arg else '"'
            builder.quoted(q)
        elif token == "line":
            builder.line()

        # Flags
        elif token == "ignorecase":
            builder.flag_ignorecase()
        elif token == "multiline":
            builder.flag_multiline()
        elif token == "dotall":
            builder.flag_dotall()

        # Raw
        elif token == "raw":
            i += 1
            builder._add(args[i])

        i += 1

    return builder.build()


# ─── Test Mode ──────────────────────────────────────────────────────────────────


def test_regex(pattern: str, test_strings: list[str]):
    """Test a generated regex against input strings."""
    compiled = re.compile(pattern)
    print(f"Pattern: {pattern}\n")
    for s in test_strings:
        match = compiled.search(s)
        if match:
            print(f"  ✓ '{s}' → matched '{match.group()}'")
            if match.groups():
                for idx, g in enumerate(match.groups(), 1):
                    print(f"      group {idx}: '{g}'")
            if match.groupdict():
                for name, val in match.groupdict().items():
                    print(f"      {name}: '{val}'")
        else:
            print(f"  ✗ '{s}' → no match")


# ─── Help Text ──────────────────────────────────────────────────────────────────

HELP = f"""\
RegexQ v{__version__} — Declarative Regex Query Builder
Author: {__author__} · astroteam.ir · MIT License

USAGE
  regexq <op> [arg] <op> [arg] ...
  regexq --test '<regex_ops...>' -- 'test string 1' 'test string 2'
  regexq --explain '<regex_ops...>'

EXAMPLES
  regexq start literal 'Hello' space word end
    → ^Hello\\s\\w+$

  regexq literal 'Price:' space literal '$' digits:1,6 maybe '.' digits:2,2
    → Price:\\s\\$\\d{{1,6}}\\.?\\d{{2,2}}

  regexq named:user word literal '@' named:domain word literal '.' letters
    → (?P<user>\\w+)@(?P<domain>\\w+)\\.[a-zA-Z]+

  regexq start either 'cat,dog,bird' end
    → ^(?:cat|dog|bird)$

  regexq --test 'email' -- 'hi@example.com' 'not-an-email' 'test@test.io'
    → Tests the email preset against each string

OPERATIONS

  Anchors
    start                    ^           Start of string
    end                      $           End of string
    boundary                 \\b          Word boundary

  Literals & Characters
    literal <text>           escaped     Literal text (auto-escaped)
    lit <text>               escaped     Alias for literal
    any_char / char          .           Any single character
    one_of <chars>           [chars]     One of the given characters
    none_of <chars>          [^chars]    None of the given characters
    range:<a>-<b>            [a-b]       Character range (e.g. range:a-z)

  Classes
    digit                    \\d          Single digit
    digits                   \\d{{1,}}     One or more digits
    digits:<n>               \\d{{n,}}     At least n digits
    digits:<a>,<b>           \\d{{a,b}}    Between a and b digits
    word                     \\w+         Word (letters, digits, _)
    word_char                \\w          Single word character
    letter                   [a-zA-Z]    Single letter
    letters                  [a-zA-Z]+   One or more letters
    lowercase                [a-z]+      Lowercase letters
    uppercase                [A-Z]+      Uppercase letters
    space                    \\s          Single whitespace
    spaces / whitespace      \\s+         One or more whitespace
    tab                      \\t          Tab character
    newline                  \\n          Newline character

  Wildcards & Patterns
    anything                 .*          Zero or more of anything
    something                .+          One or more of anything
    anything_but <chars>     [^c]*       Anything except these chars
    something_but <chars>    [^c]+       Something except these chars
    until <text>             (?:(?!t).)* Everything up to and including text
    before <text>            (?:(?!t).)* Everything before text (not including)
    between:<open>,<close>               Content between delimiters

  Quantifiers
    maybe <text>             (text)?     Optional literal
    repeat:<n>               {{n}}        Repeat previous n times
    at_least:<n>             {{n,}}       At least n times
    times:<a>,<b>            {{a,b}}      Between a and b times
    one_or_more              +           One or more of previous
    zero_or_more             *           Zero or more of previous
    optional                 ?           Previous is optional
    lazy                     ?           Make previous non-greedy

  Groups
    group / group_start      (           Start capturing group
    end_group / group_end    )           End capturing group
    named:<name>             (?P<name>   Start named group
    end_named                )           End named group
    either <a,b,c>           (?:a|b|c)   Match one of alternatives

  Lookaround
    if_followed_by <text>    (?=text)    Positive lookahead
    if_not_followed_by <t>   (?!text)    Negative lookahead
    if_preceded_by <text>    (?<=text)   Positive lookbehind
    if_not_preceded_by <t>   (?<!text)   Negative lookbehind

  Presets (common patterns)
    email                    Email address
    url                      HTTP/HTTPS URL
    ipv4 / ip                IPv4 address
    date                     ISO date (YYYY-MM-DD)
    time                     24h time (HH:MM or HH:MM:SS)
    phone                    Phone number
    hex_color / color        Hex color (#RGB or #RRGGBB)
    integer                  Integer (with optional minus)
    decimal                  Decimal number
    quoted                   Double-quoted string
    quoted:'                 Single-quoted string
    line                     Entire line

  Flags
    ignorecase               (?i)        Case-insensitive
    multiline                (?m)        Multiline mode
    dotall                   (?s)        Dot matches newline

  Advanced
    raw <regex>              Inject raw regex (no escaping)

TIPS
  • Use colon syntax for compact params: digits:2,5  named:id  range:a-z
  • Pipe to clipboard: regexq start word end | pbcopy
  • Use --test to validate against sample strings
  • Use --explain to see a breakdown of the generated regex
"""


# ─── Explain Mode ───────────────────────────────────────────────────────────────


def explain_regex(pattern: str):
    """Print a human-readable explanation of a regex."""
    print(f"Pattern: {pattern}\n")

    descriptions = [
        (r"^\(\?[imsx]+\)", "flags"),
        (r"^\^", "start of string"),
        (r"^\$", "end of string"),
        (r"^\\b", "word boundary"),
        (r"^\\d\{(\d+),(\d+)\}", lambda m: f"digit ({m.group(1)} to {m.group(2)} times)"),
        (r"^\\d\{(\d+),\}", lambda m: f"digit (at least {m.group(1)} times)"),
        (r"^\\d\{(\d+)\}", lambda m: f"digit (exactly {m.group(1)} times)"),
        (r"^\\d", "digit"),
        (r"^\\w\+", "word (letters, digits, underscore)"),
        (r"^\\w", "word character"),
        (r"^\\s\+", "one or more whitespace"),
        (r"^\\s", "whitespace"),
        (r"^\\t", "tab"),
        (r"^\\n", "newline"),
        (r"^\.\+", "one or more of any character"),
        (r"^\.\*", "zero or more of any character"),
        (r"^\.", "any character"),
        (r"^\[a-zA-Z\]\+", "one or more letters"),
        (r"^\[a-zA-Z\]", "a letter"),
        (r"^\[a-z\]\+", "lowercase letters"),
        (r"^\[A-Z\]\+", "uppercase letters"),
        (r"^\[\^([^\]]+)\]\*", lambda m: f"anything except '{m.group(1)}'"),
        (r"^\[\^([^\]]+)\]\+", lambda m: f"one or more of anything except '{m.group(1)}'"),
        (r"^\[([^\]]+)\]", lambda m: f"one of: '{m.group(1)}'"),
        (r"^\(\\?P<([^>]+)>", lambda m: f"start named group '{m.group(1)}'"),
        (r"^\(\\?:", "start non-capturing group"),
        (r"^\(\\?=", "positive lookahead"),
        (r"^\(\\?!", "negative lookahead"),
        (r"^\(\\?<=", "positive lookbehind"),
        (r"^\(\\?<!", "negative lookbehind"),
        (r"^\(", "start group"),
        (r"^\)", "end group"),
        (r"^\|", "or"),
        (r"^\{(\d+),(\d+)\}", lambda m: f"between {m.group(1)} and {m.group(2)} times"),
        (r"^\{(\d+),\}", lambda m: f"at least {m.group(1)} times"),
        (r"^\{(\d+)\}", lambda m: f"exactly {m.group(1)} times"),
        (r"^\+\?", "one or more (lazy)"),
        (r"^\*\?", "zero or more (lazy)"),
        (r"^\+", "one or more"),
        (r"^\*", "zero or more"),
        (r"^\?", "optional"),
    ]

    remaining = pattern
    step = 1
    while remaining:
        matched = False
        for regex, desc in descriptions:
            m = re.match(regex, remaining)
            if m:
                text = desc(m) if callable(desc) else desc
                print(f"  {step}. {m.group():<20s} {text}")
                remaining = remaining[m.end():]
                step += 1
                matched = True
                break
        if not matched:
            # Try to grab a literal character (possibly escaped)
            m = re.match(r"^\\(.)", remaining)
            if m:
                print(f"  {step}. {m.group():<20s} literal '{m.group(1)}'")
                remaining = remaining[m.end():]
            else:
                print(f"  {step}. {remaining[0]:<20s} literal '{remaining[0]}'")
                remaining = remaining[1:]
            step += 1


# ─── Main ───────────────────────────────────────────────────────────────────────


def main():
    argv = sys.argv[1:]

    if not argv or argv[0] in ("-h", "--help", "help"):
        print(HELP)
        sys.exit(0)

    if argv[0] in ("-v", "--version"):
        print(f"regexq {__version__}")
        sys.exit(0)

    # --test mode: regexq --test 'ops...' -- 'str1' 'str2'
    if argv[0] == "--test":
        argv = argv[1:]
        if "--" in argv:
            sep = argv.index("--")
            ops = argv[:sep]
            test_strings = argv[sep + 1:]
        else:
            sys.exit("Error: --test requires '--' separator before test strings.\n"
                     "Usage: regexq --test <ops...> -- 'string1' 'string2'")
        pattern = parse_args(ops)
        test_regex(pattern, test_strings)
        sys.exit(0)

    # --explain mode
    if argv[0] == "--explain":
        pattern = parse_args(argv[1:])
        explain_regex(pattern)
        sys.exit(0)

    # Normal mode
    print(parse_args(argv))


if __name__ == "__main__":
    main()
