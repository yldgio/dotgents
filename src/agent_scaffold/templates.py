"""Template rendering utilities."""

from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape


def get_template_env() -> Environment:
    """Get Jinja2 environment with package templates.
    
    Returns:
        Configured Jinja2 environment
    """
    return Environment(
        loader=PackageLoader("agent_scaffold", "templates"),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_template(template_path: str, **context: object) -> str:
    """Render a template with the given context.
    
    Args:
        template_path: Path to template file (relative to templates directory)
        **context: Template context variables
    
    Returns:
        Rendered template content
    """
    env = get_template_env()
    template = env.get_template(template_path)
    return template.render(**context)
