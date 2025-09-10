import re
import os
from datetime import datetime

TEMPLATE_DIR = "templates"

def render_template(template: str, context) -> str:
    try:
        if isinstance(context, list):
            if not all(isinstance(c, dict) for c in context):
                raise ValueError("All items in context list must be dictionaries")
            return [render_template(template, ctx) for ctx in context]

        if not isinstance(context, dict):
            raise ValueError("Context must be a dict or list of dicts")

        template = _render_extends(template, context)
        template = _render_includes(template, context)
        template = _render_ifs(template, context)
        template = _render_loops(template, context)
        template = _render_variables(template, context)
        return template
    except Exception as e:
        return _render_debug_page(e, template, context)

"""def render_template(template: str, context) -> str | list[str]:
    if isinstance(context, list):
        if not all(isinstance(c, dict) for c in context):
            raise ValueError("All items in context list must be dictionaries")
        return [render_template(template, ctx) for ctx in context]

    if not isinstance(context, dict):
        raise ValueError("Context must be a dict or list of dicts")

    template = _render_extends(template, context)
    template = _render_includes(template, context)
    template = _render_ifs(template, context)
    template = _render_loops(template, context)
    template = _render_variables(template, context)
    return template
"""

def _render_includes(template: str, context: dict) -> str:
    pattern = re.compile(r'{% include "(.*?)" %}')
    def replacer(match):
        #print('checking includes')
        filename = match.group(1).strip()
        path = os.path.join(TEMPLATE_DIR, filename)
        #try:
        with open(path, 'r', encoding='utf-8') as f:
            included = f.read()
        return render_template(included, context)
        #except FileNotFoundError:
        #    return f"<!-- include file not found: {filename} -->"
    return pattern.sub(replacer, template)

"""
def _render_loops(template: str, context: dict) -> str:
    pattern = re.compile(r'{%\s*for\s+(\w+)\s+in\s+(.*?)\s*%}(.*?){%\s*endfor\s*%}', re.DOTALL)
    def replacer(match):
        print('checking loops')
        var, iterable_expr, block = match.groups()
        #try:
        iterable = eval(iterable_expr, {}, context)
        #except Exception as e:
        #    return f"<!-- loop error: {e} -->"
        result = ''
        for item in iterable:
            loop_ctx = context.copy()
            loop_ctx[var] = item
            result += render_template(block, loop_ctx)
        return result
    prev = None
    while prev != template:
        prev = template
        template = pattern.sub(replacer, template)
    return template
"""

def _render_loops(template: str, context: dict) -> str:
    pattern = re.compile(r'{%\s*for\s+(\w+)\s+in\s+(.*?)\s*%}(.*?){%\s*endfor\s*%}', re.DOTALL)

    def replacer(match):
        var_name, iterable_expr, block = match.groups()
        try:
            iterable = eval(iterable_expr, context)
            result = ''
            for item in iterable:
                loop_ctx = context.copy()
                loop_ctx[var_name] = item
                result += render_template(block, loop_ctx)
            return result
        except Exception as e:
            return f"<!-- loop error: {e} -->"

    # Support nested loops by reapplying until no change
    prev = None
    while prev != template:
        prev = template
        template = pattern.sub(replacer, template)
    return template


def _render_ifs(template: str, context: dict) -> str:
    IF_START = '{% if'
    ELSE_TAG = '{% else %}'
    ENDIF_TAG = '{% endif %}'
    def find_matching_block(s, start_index):
        stack = []
        i = start_index
        while i < len(s):
            if s[i:i+len(IF_START)] == IF_START:
                stack.append(i)
                i = s.find('%}', i) + 2
            elif s[i:i+len(ENDIF_TAG)] == ENDIF_TAG:
                stack.pop()
                if not stack:
                    return i + len(ENDIF_TAG)
                i += len(ENDIF_TAG)
            else:
                i += 1
        return -1

    pattern = re.compile(r'{% if (.*?) %}', re.DOTALL)

    while True:
        match = pattern.search(template)
        if not match:
            break

        condition = match.group(1).strip()
        start_if = match.start()
        end_condition = match.end()

        end_block = find_matching_block(template, start_if)
        if end_block == -1:
            break

        block_content = template[end_condition:end_block - len(ENDIF_TAG)]

        else_index = block_content.find(ELSE_TAG)
        if else_index != -1:
            true_block = block_content[:else_index]
            false_block = block_content[else_index + len(ELSE_TAG):]
        else:
            true_block = block_content
            false_block = ''

        true_block = _render_ifs(true_block, context)
        false_block = _render_ifs(false_block, context)

        #try:
        result = true_block if eval(condition, context) else false_block
        #except Exception:
        #    result = false_block

        template = template[:start_if] + result + template[end_block:]

    return template


def _render_variables(template: str, context: dict) -> str:
    def resolve(expr, ctx):
        #print('checking resolves')

        parts = expr.split('.')
        val = ctx
        for part in parts:
            if isinstance(val, dict):
                val = val.get(part, '')
            elif hasattr(val, part):
                val = getattr(val, part)
            else:
                return ''
            if callable(val):
                val = val()
        return val

    def replacer(match):
        expr = match.group(1).strip()
        #print('checking replacements')

        if "| date:" in expr:
            var_expr, fmt = expr.split("| date:")
            fmt = fmt.strip().strip('"').strip("'")
            value = resolve(var_expr.strip(), context)
            #try:
            return datetime.strptime(str(value), "%Y%m%d").strftime(fmt)
            #except:
            #    return str(value)
        return str(resolve(expr, context))

    return re.sub(r'{{\s*(.*?)\s*}}', replacer, template)

def _render_extends(template: str, context: dict) -> str:
    match = re.search(r'{% extends "(.*?)" %}', template)
    #print('loading extends')
    if not match:
        return template
    base_file = match.group(1)
    base_path = os.path.join(TEMPLATE_DIR, base_file)
    with open(base_path, 'r', encoding='utf-8') as f:
        base_template = f.read()
    blocks = dict(re.findall(r'{% block (\w+) %}(.*?){% endblock %}', template, re.DOTALL))
    def replace_block(match):
        name, default = match.groups()
        return blocks.get(name, default)
    return re.sub(r'{% block (\w+) %}(.*?){% endblock %}', replace_block, base_template, flags=re.DOTALL)

def load_template(filename: str) -> str:
    path = os.path.join(TEMPLATE_DIR, filename)
    #print('loading templates')
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

import traceback
import html

def _render_debug_page(error, template, context):
    tb = traceback.format_exc()
    error_message = html.escape(str(error))
    escaped_tb = html.escape(tb)
    escaped_template = html.escape(template)
    escaped_context = html.escape(repr(context))

    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: monospace; background: #fff; color: #000; padding: 2em; }}
            pre {{ background: #f6f8fa; padding: 1em; border: 1px solid #ccc; overflow-x: auto; }}
            .section {{ margin-bottom: 2em; }}
            h2 {{ color: #b00; }}
        </style>
        <title>Template Error</title>
    </head>
    <body>
        <h1>Template Error</h1>

        <div class="section">
            <h2>Error Message:</h2>
            <pre>{error_message}</pre>
        </div>

        <div class="section">
            <h2>Traceback:</h2>
            <pre>{escaped_tb}</pre>
        </div>

        <div class="section">
            <h2>Template:</h2>
            <pre>{escaped_template}</pre>
        </div>

        <div class="section">
            <h2>Context:</h2>
            <pre>{escaped_context}</pre>
        </div>
    </body>
    </html>
    """
