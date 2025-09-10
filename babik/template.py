import re
import os
from datetime import datetime

TEMPLATE_DIR = "templates"  # Folder containing HTML templates and includes

#def render_template(template: str, *contexts) -> str | list[str]:
def render_template(template: str, *contexts, _internal=False) -> str | list[str]:
    flat_contexts = []
    for ctx in contexts:
        if isinstance(ctx, (list, tuple)):
            flat_contexts.extend(ctx)
        else:
            flat_contexts.append(ctx)

    # Force single render on _internal, skipping batch logic
    if _internal or all(isinstance(c, dict) for c in flat_contexts):
        merged_context = {}
        for ctx in flat_contexts:
            merged_context.update(ctx)

        template = _render_extends(template, merged_context)
        template = _render_includes(template, merged_context)
        template = _render_ifs(template, merged_context)
        template = _render_loops(template, merged_context)
        template = _render_variables(template, merged_context)
        return template

    # Batch rendering path
    elif all(isinstance(c, dict) for c in flat_contexts if isinstance(c, dict)):
        return [render_template(template, ctx) for ctx in flat_contexts]

    else:
        raise ValueError("All context arguments must be dictionaries or lists of dictionaries")

def _render_includes(template: str, context: dict) -> str:
    pattern = re.compile(r'{% include "(.*?)" %}')

    def replacer(match):
        filename = match.group(1).strip()
        path = os.path.join(TEMPLATE_DIR, filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                included_content = f.read()
            return render_template(included_content, context)
        except FileNotFoundError:
            return f"<!-- include file not found: {filename} -->"

    return pattern.sub(replacer, template)


def _render_loops(template: str, context: dict) -> str:
    #pattern = re.compile(r'{% for (\w+) in (.*?) %}(.*?){% endfor %}', re.DOTALL)
    pattern = re.compile(
        r'{%\s*for\s+(\w+)\s+in\s+(.*?)\s*%}(.*?){%\s*endfor\s*%}',
        re.DOTALL
    )
    def replacer(match):
        var_name = match.group(1)
        iterable_expr = match.group(2).strip()
        block = match.group(3)
        print('----')
        print(var_name)
        print(iterable_expr)
        print(block)
        print('----')
        #try:
        iterable = eval(iterable_expr, {}, context)
        result = ''
        for item in iterable:
            loop_context = context.copy()
            loop_context[var_name] = item
            rendered = render_template(block, loop_context, _internal=True)
            result += rendered
        return result
        #except Exception as e:
        #    print(f"[Loop Error] in '{iterable_expr}': {e}")
        #    return ''

    prev = None
    while prev != template:
        prev = template
        template = pattern.sub(replacer, template)

    return template




def _render_ifs(template: str, context: dict) -> str:
    pattern = re.compile(r'{% if (.*?) %}(.*?){% endif %}', re.DOTALL)

    def replacer(match):
        condition = match.group(1).strip()
        content = match.group(2)
        try:
            if eval(condition, {}, context):
                return content
            else:
                return ''
        except:
            return ''

    return pattern.sub(replacer, template)


def _render_variables(template: str, context: dict) -> str:
    def resolve_variable(expr, context):
        parts = expr.split('.')
        val = context
        for part in parts:
            if isinstance(val, dict) and part in val:
                val = val[part]
            elif hasattr(val, part):
                val = getattr(val, part)
            else:
                return ''
        return val

    def replacer(match):
        expr = match.group(1).strip()
        # Handle | date:"..." filter
        if "| date:" in expr:
            var_expr, format_str = expr.split("| date:")
            var_expr = var_expr.strip()
            format_str = format_str.strip().strip('"').strip("'")
            value = resolve_variable(var_expr, context)

            # If it's a string, try to parse as a date
            if isinstance(value, str):
                try:
                    dt = datetime.strptime(value, "%Y%m%d")
                    #print(dt.strftime(format_str))
                    return dt.strftime(format_str)
                except ValueError:
                    pass  # Fall back to raw string

            # If it’s something else (e.g., int), convert to string
            #return str(value)

        # Plain variable
        value = resolve_variable(expr, context)
        return str(value)

    return re.sub(r'{{\s*(.*?)\s*}}', replacer, template)



def _render_extends(template: str, context: dict) -> str:
    extend_match = re.search(r'{% extends "(.*?)" %}', template)
    if not extend_match:
        return template

    base_file = extend_match.group(1)
    base_path = os.path.join(TEMPLATE_DIR, base_file)
    with open(base_path, 'r', encoding='utf-8') as f:
        base_template = f.read()

    # Get all blocks from the child
    blocks = dict(re.findall(r'{% block (\w+) %}(.*?){% endblock %}', template, re.DOTALL))

    # Replace blocks in the base template
    def block_replacer(match):
        block_name = match.group(1)
        return blocks.get(block_name, match.group(2))  # child block or fallback to base

    rendered = re.sub(r'{% block (\w+) %}(.*?){% endblock %}', block_replacer, base_template, flags=re.DOTALL)
    return rendered

def load_template(filename: str) -> str:
    path = os.path.join(TEMPLATE_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
