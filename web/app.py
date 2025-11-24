#!/usr/bin/env python3
"""
READ Web Interface
A beautiful web UI for managing the READ pipeline
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'paper2agent-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base directories
BASE_DIR = Path(__file__).parent.parent
AGENTS_DIR = BASE_DIR / "agents"
SCRIPTS_DIR = BASE_DIR / "scripts"
UPLOADS_DIR = BASE_DIR / "web" / "uploads"

# Create uploads directory if it doesn't exist
UPLOADS_DIR.mkdir(exist_ok=True)

# Global state
current_execution = {
    "running": False,
    "step": None,
    "project_name": None,
    "logs": []
}


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/project/<project_name>')
def project_detail(project_name):
    """Project detail page"""
    project_dir = BASE_DIR / f"{project_name}_Agent"
    if not project_dir.exists():
        return "Project not found", 404
    return render_template('project.html', project_name=project_name)


@app.route('/api/projects')
def list_projects():
    """List all agent projects"""
    projects = []
    for item in BASE_DIR.iterdir():
        if item.is_dir() and item.name.endswith('_Agent'):
            project_info = get_project_info(item)
            projects.append(project_info)
    return jsonify(projects)


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload a file and return the file path"""
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400
        
        # Save file with timestamp to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        filepath = UPLOADS_DIR / filename
        file.save(str(filepath))
        
        logger.info(f"File uploaded: {filepath}")
        return jsonify({
            "success": True,
            "filepath": str(filepath),
            "filename": filename
        })
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/project/<project_name>')
def get_project(project_name):
    """Get detailed information about a project"""
    project_dir = BASE_DIR / f"{project_name}_Agent"
    if not project_dir.exists():
        return jsonify({"error": "Project not found"}), 404
    
    info = get_project_info(project_dir)
    return jsonify(info)


@app.route('/api/project/<project_name>/steps')
def get_project_steps(project_name):
    """Get pipeline steps status for a project"""
    project_dir = BASE_DIR / f"{project_name}_Agent"
    pipeline_dir = project_dir / ".pipeline"
    
    steps = []
    step_files = [
        ("01_setup_done", "Step 1: Setup Project"),
        ("02_clone_done", "Step 2: Clone Repository"),
        ("03_folders_done", "Step 3: Prepare Folders"),
        ("04_context7_done", "Step 4: Add Context7 MCP"),
        ("05_step1_done", "Step 5.1: Setup Environment"),
        ("05_step2_done", "Step 5.2: Execute Tutorials"),
        ("05_step3_done", "Step 5.3: Extract Tools"),
        ("05_step4_done", "Step 5.4: Wrap MCP Server"),
        ("05_step5_done", "Step 5.5: Generate Coverage"),
        ("06_mcp_done", "Step 6: Launch MCP Server")
    ]
    
    for file_name, title in step_files:
        completed = (pipeline_dir / file_name).exists() if pipeline_dir.exists() else False
        steps.append({
            "name": file_name,
            "title": title,
            "completed": completed
        })
    
    return jsonify(steps)


@app.route('/api/project/create', methods=['POST'])
def create_project():
    """Create a new project"""
    data = request.json
    project_name = data.get('project_name')
    repo_url = data.get('repo_url')
    api_key = data.get('api_key')
    
    if not project_name or not repo_url or not api_key:
        return jsonify({"error": "Missing required fields"}), 400
    
    # Validate API key format (basic check)
    if not api_key.startswith('sk-ant-'):
        return jsonify({"error": "Invalid API key format. Should start with 'sk-ant-'"}), 400
    
    try:
        # Set API key in environment
        env = os.environ.copy()
        env['ANTHROPIC_API_KEY'] = api_key
        
        # Run setup script
        cmd = f"cd {BASE_DIR} && bash Paper2Agent.sh {project_name} {repo_url}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
        
        return jsonify({
            "success": True,
            "message": f"Project {project_name} created successfully",
            "output": result.stdout
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/project/<project_name>/execute/<step>', methods=['POST'])
def execute_step(project_name, step):
    """Execute a specific pipeline step"""
    global current_execution
    
    if current_execution["running"]:
        return jsonify({"error": "Another execution is in progress"}), 409
    
    project_dir = BASE_DIR / f"{project_name}_Agent"
    if not project_dir.exists():
        return jsonify({"error": "Project not found"}), 404
    
    current_execution = {
        "running": True,
        "step": step,
        "project_name": project_name,
        "logs": []
    }
    
    try:
        # Map step to script
        script_map = {
            "01": "01_setup_project.sh",
            "02": "02_clone_repo.sh",
            "03": "03_prepare_folders.sh",
            "04": "04_add_context7_mcp.sh",
            "05_1": "05_run_step1_setup_env.sh",
            "05_2": "05_run_step2_execute_tutorials.sh",
            "05_3": "05_run_step3_extract_tools.sh",
            "05_4": "05_run_step4_wrap_mcp.sh",
            "05_5": "05_run_step5_generate_coverage.sh",
            "06": "06_launch_mcp.sh"
        }
        
        script_name = script_map.get(step)
        if not script_name:
            return jsonify({"error": "Invalid step"}), 400
        
        script_path = SCRIPTS_DIR / script_name
        cmd = f"cd {project_dir} && bash {script_path} {project_name}"
        
        logger.info(f"Executing: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3600)
        
        current_execution["running"] = False
        current_execution["logs"].append(result.stdout)
        
        return jsonify({
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None
        })
        
    except subprocess.TimeoutExpired:
        current_execution["running"] = False
        return jsonify({"error": "Execution timeout"}), 408
    except Exception as e:
        current_execution["running"] = False
        return jsonify({"error": str(e)}), 500


@app.route('/api/project/<project_name>/outputs')
def get_outputs(project_name):
    """Get output files from a project"""
    project_dir = BASE_DIR / f"{project_name}_Agent"
    outputs_dir = project_dir / "claude_outputs"
    
    if not outputs_dir.exists():
        return jsonify([])
    
    outputs = []
    for file in outputs_dir.glob("*.json"):
        outputs.append({
            "name": file.name,
            "size": file.stat().st_size,
            "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
        })
    
    return jsonify(outputs)


@app.route('/api/project/<project_name>/output/<filename>')
def get_output_file(project_name, filename):
    """Download a specific output file"""
    project_dir = BASE_DIR / f"{project_name}_Agent"
    file_path = project_dir / "claude_outputs" / filename
    
    if not file_path.exists():
        return jsonify({"error": "File not found"}), 404
    
    return send_file(file_path, as_attachment=True)


@app.route('/api/project/<project_name>/tools')
def get_tools(project_name):
    """Get generated tools for a project"""
    project_dir = BASE_DIR / f"{project_name}_Agent"
    tools_dir = project_dir / "src" / "tools"
    
    if not tools_dir.exists():
        return jsonify([])
    
    tools = []
    for file in tools_dir.glob("*.py"):
        if file.name != "__init__.py":
            tools.append({
                "name": file.stem,
                "filename": file.name,
                "size": file.stat().st_size,
                "lines": len(file.read_text().splitlines())
            })
    
    return jsonify(tools)


@app.route('/api/project/<project_name>/reports')
def get_reports(project_name):
    """Get reports for a project"""
    project_dir = BASE_DIR / f"{project_name}_Agent"
    reports_dir = project_dir / "reports"
    
    if not reports_dir.exists():
        return jsonify([])
    
    reports = []
    for file in reports_dir.rglob("*.md"):
        reports.append({
            "name": file.name,
            "path": str(file.relative_to(reports_dir)),
            "size": file.stat().st_size
        })
    
    return jsonify(reports)


@app.route('/api/project/<project_name>/report/<path:report_path>')
def get_report_content(project_name, report_path):
    """Get report content"""
    project_dir = BASE_DIR / f"{project_name}_Agent"
    file_path = project_dir / "reports" / report_path
    
    if not file_path.exists():
        return jsonify({"error": "Report not found"}), 404
    
    return jsonify({
        "content": file_path.read_text(),
        "name": file_path.name
    })


@app.route('/api/project/<project_name>/visualizations')
def get_visualizations(project_name):
    """Get visualization files"""
    project_dir = BASE_DIR / f"{project_name}_Agent"
    outputs_dir = project_dir / "tmp" / "outputs"
    
    if not outputs_dir.exists():
        return jsonify([])
    
    visualizations = []
    for file in outputs_dir.glob("*.png"):
        visualizations.append({
            "name": file.name,
            "path": f"/api/project/{project_name}/visualization/{file.name}",
            "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
        })
    
    return jsonify(visualizations)


@app.route('/api/project/<project_name>/visualization/<filename>')
def get_visualization_file(project_name, filename):
    """Serve a visualization image"""
    project_dir = BASE_DIR / f"{project_name}_Agent"
    file_path = project_dir / "tmp" / "outputs" / filename
    
    if not file_path.exists() or not file_path.suffix == '.png':
        return jsonify({"error": "File not found"}), 404
    
    return send_file(file_path, mimetype='image/png')


@app.route('/api/status')
def get_status():
    """Get current execution status"""
    return jsonify(current_execution)


@app.route('/api/project/<project_name>/mcp/tools')
def get_project_mcp_tools(project_name):
    """Get all MCP tools available for a specific project"""
    try:
        tools = load_mcp_tools(project_name)
        return jsonify({
            "success": True,
            "project": project_name,
            "tools": tools,
            "count": len(tools)
        })
    except Exception as e:
        logger.error(f"Error getting MCP tools for {project_name}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/project/<project_name>/chat', methods=['POST'])
def chat_with_claude(project_name):
    """Chat with Claude using API with MCP tools support"""
    try:
        from anthropic import Anthropic
    except ImportError:
        return jsonify({"success": False, "error": "anthropic package not installed. Run: pip install anthropic"}), 500
    
    data = request.json
    message = data.get('message')
    api_key = data.get('api_key')
    history = data.get('history', [])
    uploaded_files = data.get('uploaded_files', [])
    
    if not message or not api_key:
        return jsonify({"success": False, "error": "Missing message or API key"}), 400
    
    # If files were uploaded, add file information to the message
    if uploaded_files:
        file_info = "\n\n已上传的文件：\n"
        for file_data in uploaded_files:
            file_info += f"- {file_data['filename']} (路径: {file_data['filepath']})\n"
        message = message + file_info
    
    try:
        client = Anthropic(api_key=api_key)
        
        # Load MCP tools for this project
        mcp_tools = load_mcp_tools(project_name)
        
        # Build messages from history
        messages = history + [{"role": "user", "content": message}]
        
        # Call Claude API with tools
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            tools=mcp_tools if mcp_tools else [],
            messages=messages,
            system=f"You are a helpful assistant for the {project_name} project. You have access to MCP tools that you can use to help the user."
        )
        
        # Handle tool use
        if response.stop_reason == "tool_use":
            # Execute tools and continue conversation
            tool_results = []
            for content in response.content:
                if content.type == "tool_use":
                    tool_result = execute_mcp_tool(project_name, content.name, content.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": content.id,
                        "content": str(tool_result)
                    })
            
            # Continue conversation with tool results
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
            
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                tools=mcp_tools if mcp_tools else [],
                messages=messages
            )
        
        # Extract text response
        response_text = ""
        for content in response.content:
            if hasattr(content, 'text'):
                response_text += content.text
        
        return jsonify({
            "success": True,
            "message": response_text
        })
        
    except Exception as e:
        logger.error(f"Claude API error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/project/<project_name>/execute-mcp-tool', methods=['POST'])
def api_execute_mcp_tool(project_name):
    """Execute an MCP tool"""
    try:
        data = request.json
        tool_name = data.get('tool_name')
        tool_input = data.get('parameters', {})
        
        logger.info(f"API received tool_name: {tool_name}")
        logger.info(f"API received parameters: {tool_input}")
        
        if not tool_name:
            return jsonify({"error": "tool_name is required"}), 400
        
        # Handle file uploads - replace uploaded file references
        if isinstance(tool_input, dict):
            for key, value in tool_input.items():
                if isinstance(value, str) and value.startswith('__UPLOAD__:'):
                    # Extract the actual file path
                    tool_input[key] = value.replace('__UPLOAD__:', '')
        
        logger.info(f"Final parameters after processing: {tool_input}")
        result = execute_mcp_tool(project_name, tool_name, tool_input)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error executing MCP tool: {str(e)}")
        return jsonify({"error": str(e)}), 500


def load_mcp_tools(project_name):
    """Load MCP tools from project and convert to Anthropic tools format"""
    import asyncio
    import importlib
    import sys
    
    async def _load_tools_async():
        try:
            project_dir = BASE_DIR / f"{project_name}_Agent"
            tools_dir = project_dir / "src" / "tools"
            
            if not tools_dir.exists():
                return []
            
            # Add project src to path
            if str(project_dir / "src") not in sys.path:
                sys.path.insert(0, str(project_dir / "src"))
            
            # Import all tool modules
            tools = []
            
            for tool_file in sorted(tools_dir.glob("*.py")):
                if tool_file.stem == "__init__":
                    continue
                
                try:
                    # Import the module
                    module = importlib.import_module(f"tools.{tool_file.stem}")
                    mcp_instance = getattr(module, f"{tool_file.stem}_mcp", None)
                    
                    if not mcp_instance:
                        continue
                    
                    # Get all tools using FastMCP async API
                    tools_dict = await mcp_instance.get_tools()
                    
                    for tool_name, tool_obj in tools_dict.items():
                        # Convert MCP tool to Anthropic tool format
                        tool_schema = {
                            "name": tool_obj.name,
                            "description": tool_obj.description or f"Tool: {tool_obj.name}",
                            "input_schema": tool_obj.parameters
                        }
                        tools.append(tool_schema)
                except Exception as e:
                    logger.error(f"Error loading module {tool_file.stem}: {str(e)}")
                    continue
            
            logger.info(f"Loaded {len(tools)} MCP tools for {project_name}")
            return tools
            
        except Exception as e:
            logger.error(f"Error loading MCP tools: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    # Run async function in sync context
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_load_tools_async())
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Error in async execution: {str(e)}")
        return []


def execute_mcp_tool(project_name, tool_name, tool_input):
    """Execute an MCP tool and return the result"""
    import asyncio
    import importlib
    import sys
    
    async def _execute_tool_async():
        try:
            project_dir = BASE_DIR / f"{project_name}_Agent"
            tools_dir = project_dir / "src" / "tools"
            
            logger.info(f"Executing tool: {tool_name} with input: {tool_input}")
            logger.info(f"Project dir: {project_dir}")
            logger.info(f"Tools dir: {tools_dir}")
            
            # Set custom output directory if out_prefix is provided as a path
            if 'out_prefix' in tool_input and tool_input['out_prefix']:
                out_prefix_value = str(tool_input['out_prefix']).strip()
                if out_prefix_value:
                    custom_output = Path(out_prefix_value)
                    
                    # Check if it's a path (contains / or is absolute)
                    if custom_output.is_absolute() or '/' in out_prefix_value:
                        # It's a directory path
                        output_dir = custom_output if not custom_output.suffix else custom_output.parent
                        
                        # Create directory if it doesn't exist
                        try:
                            output_dir.mkdir(parents=True, exist_ok=True)
                            logger.info(f"Created/verified output directory: {output_dir}")
                        except Exception as e:
                            logger.warning(f"Could not create output directory {output_dir}: {e}")
                        
                        # Set environment variables for all tool modules
                        os.environ['BASIC_USAGE_OUTPUT_DIR'] = str(output_dir)
                        os.environ['ADVANCED_VISUALIZATION_OUTPUT_DIR'] = str(output_dir)
                        os.environ['CLASSIFICATION_OUTPUT_DIR'] = str(output_dir)
                        os.environ['CLUSTERING_OUTPUT_DIR'] = str(output_dir)
                        logger.info(f"Set custom output directory: {output_dir}")
                    else:
                        # It's just a filename prefix, keep it in tool_input
                        logger.info(f"Using filename prefix: {out_prefix_value}")
            
            # Add project src to path
            if str(project_dir / "src") not in sys.path:
                sys.path.insert(0, str(project_dir / "src"))
            
            # Search for the tool in all modules
            all_tools = []
            for tool_file in sorted(tools_dir.glob("*.py")):
                if tool_file.stem == "__init__":
                    continue
                
                try:
                    logger.info(f"Checking module: {tool_file.stem}")
                    module = importlib.import_module(f"tools.{tool_file.stem}")
                    mcp_instance = getattr(module, f"{tool_file.stem}_mcp", None)
                    
                    if not mcp_instance:
                        logger.warning(f"No MCP instance found in {tool_file.stem}")
                        continue
                    
                    # Get all tools using FastMCP async API
                    tools_dict = await mcp_instance.get_tools()
                    all_tools.extend(tools_dict.keys())
                    logger.info(f"Module {tool_file.stem} has tools: {list(tools_dict.keys())}")
                    
                    if tool_name in tools_dict:
                        logger.info(f"Found tool {tool_name} in {tool_file.stem}")
                        tool_obj = tools_dict[tool_name]
                        
                        try:
                            # Execute the tool function
                            logger.info(f"Executing tool function with params: {tool_input}")
                            result = tool_obj.fn(**tool_input)
                            
                            # Handle async functions
                            if asyncio.iscoroutine(result):
                                result = await result
                            
                            logger.info(f"Tool execution successful")
                            return {"success": True, "result": result}
                        except Exception as exec_error:
                            logger.error(f"Error executing tool {tool_name}: {str(exec_error)}")
                            import traceback
                            logger.error(traceback.format_exc())
                            return {"success": False, "error": f"Tool execution failed: {str(exec_error)}"}
                except Exception as e:
                    logger.error(f"Error loading module {tool_file.stem}: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
                    continue
            
            logger.error(f"Tool {tool_name} not found. Available tools: {all_tools}")
            return {"error": f"Tool {tool_name} not found. Available tools: {', '.join(all_tools)}"}
            
        except Exception as e:
            logger.error(f"Error executing MCP tool {tool_name}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    # Run async function in sync context
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_execute_tool_async())
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Error in async execution: {str(e)}")
        return {"error": str(e)}


def get_project_info(project_dir: Path) -> dict:
    """Extract project information"""
    pipeline_dir = project_dir / ".pipeline"
    
    # Count completed steps
    completed_steps = 0
    if pipeline_dir.exists():
        completed_steps = len(list(pipeline_dir.glob("*_done")))
    
    # Check for tools
    tools_dir = project_dir / "src" / "tools"
    tools_count = 0
    if tools_dir.exists():
        tools_count = len([f for f in tools_dir.glob("*.py") if f.name != "__init__.py"])
    
    # Check for MCP server
    mcp_file = project_dir / "src" / f"{project_dir.stem.replace('_Agent', '').lower()}_mcp.py"
    has_mcp = mcp_file.exists()
    
    return {
        "name": project_dir.stem.replace('_Agent', ''),
        "path": str(project_dir),
        "completed_steps": completed_steps,
        "total_steps": 10,
        "tools_count": tools_count,
        "has_mcp": has_mcp,
        "progress": int((completed_steps / 10) * 100)
    }


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 READ Web Interface")
    print("="*60)
    print(f"\n📂 Base Directory: {BASE_DIR}")
    print(f"🌐 Access the interface at: http://localhost:5000")
    print("\n🔐 Security Notice:")
    print("   - API keys are NOT stored permanently")
    print("   - Each project creation requires API key input")
    print("   - Keys are only used during pipeline execution")
    print("\n" + "="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
