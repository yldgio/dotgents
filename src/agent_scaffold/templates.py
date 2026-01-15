"""Template rendering utilities."""

from jinja2 import Environment, PackageLoader

# Cache the Jinja2 environment for efficiency
_template_env: Environment | None = None


def get_template_env() -> Environment:
    """Get Jinja2 environment with package templates.
    
    Returns:
        Configured Jinja2 environment
    """
    global _template_env
    if _template_env is None:
        _template_env = Environment(
            loader=PackageLoader("agent_scaffold", "templates"),
            autoescape=False,  # Disable autoescape for Markdown files
            trim_blocks=True,
            lstrip_blocks=True,
        )
    return _template_env


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
