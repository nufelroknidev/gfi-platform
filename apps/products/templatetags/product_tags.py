from django import template

register = template.Library()


@register.filter
def parse_specs(text):
    """
    Parse pipe-separated specifications into a list of row lists.
    Returns [[cell, cell, ...], ...] — first row is treated as a header in the template.
    Falls back to colon-splitting for legacy data that predates the pipe format.
    """
    if not text:
        return []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return []
    # Detect format: use pipe if at least one line contains '|'
    use_pipe = any('|' in line for line in lines)
    rows = []
    for line in lines:
        if use_pipe:
            cells = [c.strip() for c in line.split('|')]
        elif ':' in line:
            label, _, value = line.partition(':')
            cells = [label.strip(), value.strip()]
        else:
            cells = [line]
        if any(c for c in cells):
            rows.append(cells)
    return rows
