"""
Google Stitch Integration for Gemini Lens MCP.
Provides UI screen generation, frontend code scaffolding, design system management,
and project retrieval powered by Google Stitch and Antigravity.
"""

from typing import Optional
from .runner import execute_query

def register_stitch_tools(mcp):
    """Registers Google Stitch tools onto the MCP server."""

    @mcp.tool(
        name="stitch_list_projects",
        description="Lists all Google Stitch UI design projects owned by or shared with your Google account."
    )
    async def stitch_list_projects(filter: str = "view=owned") -> str:
        prompt = f"Please use Stitch list_projects with filter='{filter}' to list my available UI projects and return their titles and project IDs."
        return await execute_query("gemini-3.8-flash-high", prompt)

    @mcp.tool(
        name="stitch_create_project",
        description="Creates a new Google Stitch project container for app screens, design systems, and frontend code."
    )
    async def stitch_create_project(title: str = "New UI Project") -> str:
        prompt = f"Please use Stitch create_project with title='{title}' to create a new design project and report the project ID."
        return await execute_query("gemini-3.8-flash-high", prompt)

    @mcp.tool(
        name="stitch_list_screens",
        description="List all screens, UI mockups, and components inside a specific Google Stitch project."
    )
    async def stitch_list_screens(project_id: str) -> str:
        prompt = f"Please use Stitch list_screens for projectId='{project_id}' to list all screen IDs, device types, and titles."
        return await execute_query("gemini-3.8-flash-high", prompt)

    @mcp.tool(
        name="stitch_get_screen",
        description="Retrieve the full UI layout, components, and code for an existing screen inside a Google Stitch project."
    )
    async def stitch_get_screen(project_id: str, screen_id: str) -> str:
        prompt = f"Please use Stitch get_screen for projectId='{project_id}' and screenId='{screen_id}' to retrieve the screen details and frontend code."
        return await execute_query("gemini-3.8-flash-high", prompt)

    @mcp.tool(
        name="stitch_generate_screen",
        description="Generate a new mobile or desktop UI screen and frontend code in a Google Stitch project from a text prompt."
    )
    async def stitch_generate_screen(
        project_id: str,
        prompt: str,
        device_type: str = "MOBILE",
        design_system_id: Optional[str] = None
    ) -> str:
        instruction = (
            f"Please use Stitch generate_screen_from_text with:\n"
            f"- projectId: '{project_id}'\n"
            f"- prompt: '{prompt}'\n"
            f"- deviceType: '{device_type}'\n"
        )
        if design_system_id:
            instruction += f"- designSystem: '{design_system_id}'\n"
        return await execute_query("gemini-3.8-flash-high", instruction)

    @mcp.tool(
        name="stitch_apply_design_system",
        description="Apply an existing design system (color tokens, typography, layout specs) to a Google Stitch project."
    )
    async def stitch_apply_design_system(project_id: str, design_system_id: str) -> str:
        prompt = f"Please use Stitch apply_design_system to apply designSystemId='{design_system_id}' to projectId='{project_id}'."
        return await execute_query("gemini-3.8-flash-high", prompt)
