from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import os
import httpx
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import html2text
import pandas as pd
import pickle
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Super Mind API Configuration
SUPER_MIND_API_KEY = os.getenv("SUPER_MIND_API_KEY")
SUPER_MIND_BASE_URL = os.getenv("SUPER_MIND_BASE_URL", "https://space.ai-builders.com/backend/v1")

# Initialize OpenAI client
if not SUPER_MIND_API_KEY:
    raise ValueError("SUPER_MIND_API_KEY environment variable not set! Please configure it in .env file.")

openai_client = OpenAI(
    api_key=SUPER_MIND_API_KEY,
    base_url=SUPER_MIND_BASE_URL
)

app = FastAPI(
    title="Chat API Service",
    description="FastAPI application with OpenAI-compatible chat completion API",
    version="1.0.0"
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    error_trace = traceback.format_exc()
    logger.error(f"Global exception handler caught: {type(exc).__name__}: {str(exc)}")
    logger.error(f"Traceback:\n{error_trace}")
    try:
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": f"Internal server error: {str(exc)}",
                    "type": "internal_error",
                    "error_type": type(exc).__name__,
                    "traceback": error_trace
                }
            }
        )
    except Exception as json_err:
        logger.error(f"Failed to create JSONResponse: {json_err}")
        # Fallback to plain text
        from fastapi.responses import Response
        return Response(
            content=f"Internal Server Error: {str(exc)}\n\nTraceback:\n{error_trace}",
            status_code=500,
            media_type="text/plain"
        )


class ChatRequest(BaseModel):
    user_message: str


class ChatResponse(BaseModel):
    response: str


class WebSearchRequest(BaseModel):
    query: str


class WebSearchResponse(BaseModel):
    results: Any  # API returns a complex nested structure, use Any for flexibility
    success: bool
    error: Optional[str] = None


@app.post(
    "/chat",
    summary="Chat Completion API with Agentic Loop",
    description="""
    Chat completion API using OpenAI SDK to call Super Mind API with tool calling support.
    
    This endpoint implements a full agentic loop that can:
    - Call web_search tool when needed
    - Process tool results and continue the conversation
    - Loop up to 3 times to handle complex queries
    
    Accepts a user message and returns an AI-generated response using the GPT-5 model.
    """,
    response_model=ChatResponse,
    responses={
        200: {
            "description": "Successfully returned AI response",
            "content": {
                "application/json": {
                    "example": {
                        "response": "Hello! I'm doing well, thank you for asking."
                    }
                }
            }
        },
        500: {
            "description": "Super Mind API call failed"
        }
    }
)
async def chat(request: ChatRequest):
    """
    Chat API - Call Super Mind API using OpenAI SDK with Agentic Loop
    
    Implements a full agentic loop that:
    1. Sends user message to LLM with available tools
    2. If LLM requests a tool call, executes it
    3. Feeds tool results back to LLM
    4. Repeats up to 3 times until final answer
    
    - **user_message**: The user's message (required)
    
    Returns the assistant's final response as a JSON object.
    """
    import json
    import logging
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger(__name__)
    
    try:
        max_turns = 3
        messages = [
            {"role": "user", "content": request.user_message}
        ]
        
        logger.info(f"[Agent] Starting conversation with message: {request.user_message}")
        logger.info(f"[Agent] Max turns: {max_turns}")
        
        for turn in range(1, max_turns + 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"[Agent] Turn {turn}/{max_turns}")
            logger.info(f"{'='*60}")
            
            # Call OpenAI API with tools
            completion = openai_client.chat.completions.create(
                model="gpt-5",
                messages=messages,
                tools=[WEB_SEARCH_TOOL_SCHEMA, READ_PAGE_TOOL_SCHEMA],
                tool_choice="auto"
            )
            
            assistant_message = completion.choices[0].message
            
            # Check if LLM wants to call a tool
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    logger.info(f"[Agent] Decided to call tool: '{function_name}'")
                
                # Add assistant's message with tool calls to conversation
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })
                
                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"[Agent] Executing tool: '{function_name}' with arguments: {function_args}")
                    
                    if function_name == "web_search":
                        query = function_args.get("query", "")
                        logger.info(f"[Agent] Calling web_search with query: '{query}'")
                        
                        # Execute web search
                        search_result = web_search(query)
                        
                        if search_result["success"]:
                            # Format the search results for the LLM
                            # Extract key information from the nested structure
                            results_data = search_result["results"]
                            
                            # Create a readable summary of search results
                            search_summary = format_search_results(results_data)
                            
                            # Log tool output summary (truncate if too long)
                            summary_preview = search_summary[:200] + "..." if len(search_summary) > 200 else search_summary
                            logger.info(f"[System] Tool Output: '{summary_preview}'")
                            
                            # Add tool result to messages
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": search_summary
                            })
                            
                            logger.info(f"[System] Tool result added to conversation history")
                        else:
                            error_msg = f"Search failed: {search_result.get('error', 'Unknown error')}"
                            logger.warning(f"[System] Tool Output: '{error_msg}'")
                            
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": f"Error: {error_msg}"
                            })
                    
                    elif function_name == "read_page":
                        url = function_args.get("url", "")
                        logger.info(f"[Agent] Calling read_page with URL: '{url}'")
                        
                        # Execute page reading
                        page_result = read_page(url)
                        
                        if page_result["success"]:
                            content = page_result["content"]
                            
                            # Log tool output summary (truncate if too long)
                            content_preview = content[:200] + "..." if len(content) > 200 else content
                            logger.info(f"[System] Tool Output: '{content_preview}'")
                            
                            # Add tool result to messages
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": f"Page content from {url}:\n\n{content}"
                            })
                            
                            logger.info(f"[System] Tool result added to conversation history")
                        else:
                            error_msg = f"Failed to read page: {page_result.get('error', 'Unknown error')}"
                            logger.warning(f"[System] Tool Output: '{error_msg}'")
                            
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": f"Error: {error_msg}"
                            })
                    
                    else:
                        logger.warning(f"[System] Unknown tool: {function_name}")
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": f"Error: Unknown tool '{function_name}'"
                        })
                
                # Continue loop to get LLM's response to tool results
                logger.info(f"[Agent] Tool execution complete, continuing conversation...")
                continue
            else:
                # No tool calls, LLM has final answer
                final_response = assistant_message.content
                logger.info(f"\n{'='*60}")
                logger.info(f"[Agent] Final Answer (Turn {turn}):")
                logger.info(f"{'='*60}")
                logger.info(f"{final_response}")
                logger.info(f"{'='*60}\n")
                
                return ChatResponse(response=final_response)
        
        # If we've exhausted all turns, return the last response
        logger.warning(f"[Agent] Reached max turns ({max_turns}), returning last response")
        final_response = messages[-1].get("content", "I apologize, but I need more information to answer your question.")
        
        return ChatResponse(response=final_response)
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"[Error] Exception occurred: {str(e)}")
        logger.error(f"[Error] Traceback:\n{error_trace}")
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "message": f"Error calling Super Mind API: {str(e)}",
                    "type": "api_error",
                    "error_type": type(e).__name__
                }
            }
        )


def format_search_results(results_data: Dict[str, Any]) -> str:
    """
    Format search results into a readable string for the LLM.
    
    Args:
        results_data: The raw search results from the API
        
    Returns:
        Formatted string with search results
    """
    try:
        formatted_parts = []
        
        if "queries" in results_data and results_data["queries"]:
            for query_item in results_data["queries"]:
                keyword = query_item.get("keyword", "")
                response_data = query_item.get("response", {})
                
                formatted_parts.append(f"Search Query: {keyword}\n")
                
                # Add answer if available
                if response_data.get("answer"):
                    formatted_parts.append(f"Answer: {response_data['answer']}\n")
                
                # Add search results
                if "results" in response_data and response_data["results"]:
                    formatted_parts.append(f"\nSearch Results ({len(response_data['results'])} found):\n")
                    for idx, result in enumerate(response_data["results"][:5], 1):  # Limit to top 5
                        title = result.get("title", "No title")
                        url = result.get("url", "")
                        content = result.get("content", "")[:500]  # Limit content length
                        score = result.get("score", 0)
                        
                        formatted_parts.append(f"\n{idx}. {title}")
                        formatted_parts.append(f"   URL: {url}")
                        formatted_parts.append(f"   Relevance Score: {score:.2f}")
                        if content:
                            formatted_parts.append(f"   Content: {content}...")
                        formatted_parts.append("")
        
        # Add combined answer if available
        if results_data.get("combined_answer"):
            formatted_parts.append(f"\nCombined Answer:\n{results_data['combined_answer']}\n")
        
        # Add errors if any
        if results_data.get("errors"):
            formatted_parts.append(f"\nErrors: {results_data['errors']}\n")
        
        result_text = "\n".join(formatted_parts)
        
        if not result_text.strip():
            return "No search results found."
        
        return result_text
        
    except Exception as e:
        return f"Error formatting search results: {str(e)}"


def web_search(query: str) -> Dict[str, Any]:
    """
    Search the web using AI Builder Space search API.
    
    Args:
        query: The search query string
        
    Returns:
        Dictionary containing search results or error information
    """
    try:
        # Prepare the request
        search_url = "https://space.ai-builders.com/backend/v1/search/"
        headers = {
            "Authorization": f"Bearer {SUPER_MIND_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "keywords": [query],
            "max_results": 3
        }
        
        # Make the POST request
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                search_url,
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                return {
                    "results": response.json(),
                    "success": True,
                    "error": None
                }
            else:
                return {
                    "results": [],
                    "success": False,
                    "error": f"API returned status {response.status_code}: {response.text}"
                }
                
    except Exception as e:
        return {
            "results": [],
            "success": False,
            "error": str(e)
        }


def read_page(url: str) -> Dict[str, Any]:
    """
    Fetch a web page and extract its main text content.
    
    Args:
        url: The URL of the web page to read
        
    Returns:
        Dictionary containing page content or error information
    """
    try:
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            return {
                "content": None,
                "success": False,
                "error": f"Invalid URL format: {url}. URL must start with http:// or https://"
            }
        
        # Fetch the page
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = client.get(url, headers=headers)
            
            if response.status_code != 200:
                return {
                    "content": None,
                    "success": False,
                    "error": f"HTTP {response.status_code}: Failed to fetch page"
                }
            
            # Parse HTML and extract text
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            # Extract main content (try to find main/article/content tags first)
            main_content = None
            for tag_name in ['main', 'article', '[role="main"]', 'content']:
                main_content = soup.find(tag_name)
                if main_content:
                    break
            
            if not main_content:
                main_content = soup.find('body')
            
            if not main_content:
                main_content = soup
            
            # Convert to text using html2text for better formatting
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = True
            h.body_width = 0  # Don't wrap lines
            text_content = h.handle(str(main_content))
            
            # Clean up the text
            text_content = '\n'.join(line.strip() for line in text_content.split('\n') if line.strip())
            
            # Limit content length (keep first 8000 characters)
            if len(text_content) > 8000:
                text_content = text_content[:8000] + "\n\n[Content truncated...]"
            
            return {
                "content": text_content,
                "success": True,
                "url": url,
                "error": None
            }
            
    except httpx.TimeoutException:
        return {
            "content": None,
            "success": False,
            "error": "Request timeout: Page took too long to load"
        }
    except Exception as e:
        return {
            "content": None,
            "success": False,
            "error": str(e)
        }


# Tool schemas for LLM function calling
WEB_SEARCH_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for current information. Use this tool when you need to find recent or real-time information about events, facts, news, or any topic that requires up-to-date data.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string. Should be clear and specific, containing the main keywords for the search."
                }
            },
            "required": ["query"]
        }
    }
}

READ_PAGE_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "read_page",
        "description": "Read and extract the main text content from a web page. Use this tool when you need to read the content of a specific webpage, such as documentation, articles, or changelogs. Always use web_search first to find the URL, then use read_page to read the actual content.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL of the web page to read. Must start with http:// or https://"
                }
            },
            "required": ["url"]
        }
    }
}


@app.post(
    "/web_search",
    summary="Web Search API",
    description="""
    Search the web using AI Builder Space search API.
    
    This endpoint accepts a search query and returns web search results.
    """,
    response_model=WebSearchResponse,
    responses={
        200: {
            "description": "Search results returned successfully",
        },
        500: {
            "description": "Search API call failed"
        }
    }
)
async def web_search_endpoint(request: WebSearchRequest):
    """
    Web Search API endpoint
    
    Accepts a search query and returns web search results from AI Builder Space.
    """
    try:
        result = web_search(request.query)
        
        if result["success"]:
            return WebSearchResponse(
                results=result["results"],
                success=True
            )
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": {
                        "message": f"Error calling search API: {result['error']}",
                        "type": "search_api_error"
                    }
                }
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "message": f"Unexpected error: {str(e)}",
                    "type": "internal_error",
                    "error_type": type(e).__name__
                }
            }
        )


@app.get("/tools")
async def get_tools():
    """
    Get available tools schema for LLM function calling.
    
    Returns the JSON schema that defines available tools for the LLM.
    """
    return {
        "tools": [WEB_SEARCH_TOOL_SCHEMA, READ_PAGE_TOOL_SCHEMA],
        "tool_choice": "auto"
    }


@app.post(
    "/test_tool_call",
    summary="Test Tool Call Format",
    description="""
    Test endpoint to verify LLM can output valid tool calls.
    
    This endpoint simulates what an LLM would return when asked a question
    that requires web search, showing the expected tool call format.
    """
)
async def test_tool_call():
    """
    Test endpoint to demonstrate valid tool call format.
    
    Returns an example of what the LLM should output when it needs to call
    the web_search tool for a question like "Who won the Super Bowl?"
    """
    # Example: When asked "Who won the Super Bowl?", LLM should output:
    example_tool_call = {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": "call_abc123",
                "type": "function",
                "function": {
                    "name": "web_search",
                    "arguments": '{"query": "Super Bowl winner 2024"}'
                }
            }
        ]
    }
    
    return {
        "message": "Example tool call format for question: 'Who won the Super Bowl?'",
        "expected_tool_call": example_tool_call,
        "tool_schema": WEB_SEARCH_TOOL_SCHEMA,
        "note": "The LLM should output tool_calls in this format when it needs to search the web."
    }


@app.post(
    "/upload_garmin",
    summary="Upload Garmin Running CSV",
    description="""
    Upload a Garmin running history CSV file.
    The file will be saved as 'Garmin_Runing.csv' and can be used to build a semantic search index.
    """,
    responses={
        200: {
            "description": "File uploaded successfully",
        },
        400: {
            "description": "Invalid file format"
        }
    }
)
async def upload_garmin_csv(file: UploadFile = File(...)):
    """
    Upload Garmin running CSV file.
    
    - **file**: The CSV file containing running history
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail={"error": "File must be a CSV file"}
            )
        
        # Save the uploaded file
        file_path = "Garmin_Runing.csv"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "saved_as": file_path,
            "size_bytes": len(content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "message": f"Error uploading file: {str(e)}",
                    "type": "upload_error"
                }
            }
        )


@app.post(
    "/upload_tcx",
    summary="Upload and Analyze TCX Running File",
    description="""
    Upload a Garmin TCX (Training Center XML) file for today's run.
    The file will be analyzed and comprehensive metrics will be returned.
    """,
    responses={
        200: {
            "description": "File analyzed successfully",
        },
        400: {
            "description": "Invalid file format"
        }
    }
)
async def upload_and_analyze_tcx(file: UploadFile = File(...)):
    """
    Upload TCX file and analyze running metrics.
    
    - **file**: The TCX file containing today's run data
    
    Returns comprehensive analysis including:
    - Basic stats (distance, duration, HR, pace)
    - Cardiac drift analysis
    - Pacing variance
    - Cadence metrics
    - Vertical oscillation analysis
    - Stride metrics
    - Ground contact metrics
    """
    try:
        # Validate file type
        if not file.filename.endswith('.tcx'):
            raise HTTPException(
                status_code=400,
                detail={"error": "File must be a TCX file (.tcx)"}
            )
        
        # Save the uploaded file temporarily
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tcx') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Import and use the analyzer
            try:
                from tcx_analyzer import analyze_tcx
            except ImportError as import_err:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": {
                            "message": f"Failed to import tcx_analyzer: {str(import_err)}",
                            "type": "import_error"
                        }
                    }
                )
            
            # Analyze the TCX file
            try:
                analysis_result = analyze_tcx(tmp_file_path)
            except Exception as analysis_err:
                import traceback
                error_trace = traceback.format_exc()
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": {
                            "message": f"Error analyzing TCX file: {str(analysis_err)}",
                            "type": "analysis_error",
                            "traceback": error_trace
                        }
                    }
                )
            
            # Also save as Runing_Today.tcx for reference
            try:
                with open("Runing_Today.tcx", "wb") as f:
                    f.write(content)
            except Exception as save_err:
                # Log but don't fail if save fails
                print(f"Warning: Could not save file: {save_err}")
            
            return {
                "message": "File analyzed successfully",
                "filename": file.filename,
                "saved_as": "Runing_Today.tcx",
                "size_bytes": len(content),
                "analysis": analysis_result
            }
            
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
            except Exception as cleanup_err:
                print(f"Warning: Could not clean up temp file: {cleanup_err}")
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Unexpected error in upload_tcx: {error_trace}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": f"Unexpected error: {str(e)}",
                    "type": "unexpected_error",
                    "error_type": type(e).__name__,
                    "traceback": error_trace
                }
            }
        )


@app.post(
    "/upload_running_csv",
    summary="Upload and Analyze Running CSV File",
    description="""
    Upload a running CSV file (similar to Running_Today.csv format).
    The file will be analyzed and comprehensive metrics will be returned.
    """,
    responses={
        200: {
            "description": "File analyzed successfully",
        },
        400: {
            "description": "Invalid file format"
        }
    }
)
async def upload_and_analyze_running_csv(file: UploadFile = File(...)):
    """
    Upload CSV file and analyze running metrics.
    
    - **file**: The CSV file containing today's run data
    
    Returns comprehensive analysis including:
    - Basic stats (distance, duration, HR, pace)
    - Cardiac drift analysis
    - Pacing variance
    - Cadence metrics
    - Vertical oscillation analysis
    - Stride metrics
    - Ground contact metrics
    """
    logger.info(f"Received upload request for file: {file.filename}")
    
    try:
        # Validate file type
        if not file.filename or not file.filename.endswith('.csv'):
            logger.warning(f"Invalid file type: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail={"error": "File must be a CSV file (.csv)"}
            )
        
        # Read file content first
        logger.info("Reading file content...")
        try:
            content = await file.read()
            logger.info(f"Read {len(content)} bytes from file")
        except Exception as read_err:
            logger.error(f"Failed to read file: {read_err}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "message": f"Failed to read uploaded file: {str(read_err)}",
                        "type": "file_read_error"
                    }
                }
            )
        
        if len(content) == 0:
            raise HTTPException(
                status_code=400,
                detail={"error": "Uploaded file is empty"}
            )
        
        # Save the uploaded file temporarily
        import tempfile
        import os
        
        logger.info("Creating temporary file...")
        try:
            fd, tmp_file_path = tempfile.mkstemp(suffix='.csv')
            with os.fdopen(fd, 'wb') as tmp_file:
                tmp_file.write(content)
            logger.info(f"Created temporary file: {tmp_file_path}")
        except Exception as write_err:
            logger.error(f"Failed to create temp file: {write_err}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": {
                        "message": f"Failed to create temporary file: {str(write_err)}",
                        "type": "temp_file_error"
                    }
                }
            )
        
        try:
            # Import and use the analyzer
            logger.info("Importing csv_analyzer...")
            try:
                from csv_analyzer import analyze_csv
                logger.info("csv_analyzer imported successfully")
            except ImportError as import_err:
                logger.error(f"Import error: {import_err}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": {
                            "message": f"Failed to import csv_analyzer: {str(import_err)}",
                            "type": "import_error"
                        }
                    }
                )
            
            # Analyze the CSV file
            logger.info("Analyzing CSV file...")
            try:
                analysis_result = analyze_csv(tmp_file_path)
                logger.info("CSV analysis completed successfully")
            except ValueError as val_err:
                logger.error(f"CSV validation error: {val_err}")
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": {
                            "message": f"CSV file error: {str(val_err)}",
                            "type": "csv_validation_error"
                        }
                    }
                )
            except Exception as analysis_err:
                import traceback
                error_trace = traceback.format_exc()
                logger.error(f"Analysis error: {analysis_err}\n{error_trace}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": {
                            "message": f"Error analyzing CSV file: {str(analysis_err)}",
                            "type": "analysis_error",
                            "error_type": type(analysis_err).__name__
                        }
                    }
                )
            
            # Also save as Running_Today.csv for reference
            try:
                with open("Running_Today.csv", "wb") as f:
                    f.write(content)
            except Exception as save_err:
                # Log but don't fail if save fails
                print(f"Warning: Could not save file: {save_err}")
            
            return {
                "message": "File analyzed successfully",
                "filename": file.filename,
                "saved_as": "Running_Today.csv",
                "size_bytes": len(content),
                "analysis": analysis_result
            }
            
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
            except Exception as cleanup_err:
                print(f"Warning: Could not clean up temp file: {cleanup_err}")
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Unexpected error in upload_running_csv: {error_trace}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": f"Unexpected error: {str(e)}",
                    "type": "unexpected_error",
                    "error_type": type(e).__name__,
                    "traceback": error_trace
                }
            }
        )


@app.get("/")
async def root():
    return {"message": "Chat API Service is running"}
