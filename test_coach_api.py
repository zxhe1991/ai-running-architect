"""
测试教练建议 API
创建一个独立的 FastAPI 端点来测试教练建议功能
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Initialize OpenAI client
SUPER_MIND_API_KEY = os.getenv("SUPER_MIND_API_KEY")
SUPER_MIND_BASE_URL = os.getenv("SUPER_MIND_BASE_URL", "https://space.ai-builders.com/backend/v1")

if not SUPER_MIND_API_KEY:
    raise ValueError("SUPER_MIND_API_KEY not set in .env file")

openai_client = OpenAI(
    api_key=SUPER_MIND_API_KEY,
    base_url=SUPER_MIND_BASE_URL
)

app = FastAPI(title="Coach Advice Test API")

# Request models
class CoachRequest(BaseModel):
    user_profile: Dict[str, Any]
    goal: Dict[str, Any]
    today_analysis: Dict[str, Any]
    historical_runs: list = []
    subjective_feeling: Optional[str] = None
    language: str = "Chinese"

# Helper function to parse pace
def parse_pace_to_seconds(pace_str):
    """Convert pace string (e.g., "8:15") to seconds."""
    if not pace_str or pace_str == 'N/A':
        return None
    try:
        parts = str(pace_str).split(':')
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except:
        return None
    return None

def calculate_days_until_target(target_date_str: str) -> Optional[int]:
    """Calculate days until target date."""
    try:
        if "month" in target_date_str.lower():
            months = int(''.join(filter(str.isdigit, target_date_str)))
            target_date = datetime.now() + timedelta(days=months * 30)
        elif "week" in target_date_str.lower():
            weeks = int(''.join(filter(str.isdigit, target_date_str)))
            target_date = datetime.now() + timedelta(weeks=weeks)
        else:
            target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
        
        days_until = (target_date - datetime.now()).days
        return days_until if days_until > 0 else None
    except:
        return None

@app.post("/coach/advice")
async def get_coach_advice(request: CoachRequest):
    """
    获取教练建议的测试端点
    """
    try:
        # Extract data
        user_profile = request.user_profile
        goal = request.goal
        today_analysis = request.today_analysis
        historical_runs = request.historical_runs
        subjective_feeling = request.subjective_feeling or ""
        language = request.language
        
        # Build context
        age = user_profile.get('age', 'Unknown')
        gender = user_profile.get('gender', 'Unknown')
        target_pace = goal.get('target_pace', 'Unknown')
        target_date = goal.get('target_date', 'Unknown')
        weekly_hours = goal.get('weekly_hours', 5.0)
        pace_unit = goal.get('pace_unit', 'km')
        
        # Calculate days until target
        days_until = calculate_days_until_target(target_date)
        days_str = f"{days_until} 天后" if days_until else "未知"
        weeks_until = days_until / 7.0 if days_until else None
        weeks_str = f"{weeks_until:.1f} 周" if weeks_until else "未知"
        
        # Today's metrics
        basic_stats = today_analysis.get('basic_stats', {})
        drift_pct = today_analysis.get('cardiac_drift', {}).get('drift_percentage')
        avg_hr = basic_stats.get('avg_heart_rate')
        avg_pace = basic_stats.get('avg_pace') or basic_stats.get('avg_pace_min_km')
        distance = basic_stats.get('total_distance_km', 0)
        run_type = today_analysis.get('pacing_variance', {}).get('run_type', 'Unknown')
        
        # Parse pace
        current_pace_seconds = parse_pace_to_seconds(avg_pace) if avg_pace else None
        target_pace_seconds = parse_pace_to_seconds(target_pace) if target_pace else None
        
        pace_gap = None
        if current_pace_seconds and target_pace_seconds:
            pace_gap = current_pace_seconds - target_pace_seconds
        
        # Historical context
        historical_summary = ""
        if historical_runs:
            if language == 'Chinese':
                historical_summary = "\n**历史相似跑步：**\n"
            else:
                historical_summary = "\n**Historical Similar Runs:**\n"
            
            for i, run in enumerate(historical_runs[:3], 1):
                run_data = run.get('data', {})
                hist_date = run_data.get('Date', 'Unknown')
                hist_distance = run_data.get('Distance', 'N/A')
                hist_pace = run_data.get('Avg Pace', 'N/A')
                hist_hr = run_data.get('Avg HR', 'N/A')
                
                if language == 'Chinese':
                    historical_summary += f"{i}. 日期: {hist_date}, 距离: {hist_distance}, 配速: {hist_pace}, 心率: {hist_hr}\n"
                else:
                    historical_summary += f"{i}. Date: {hist_date}, Distance: {hist_distance}, Pace: {hist_pace}, HR: {hist_hr}\n"
        
        # Build prompt
        pace_unit_label = "min/mi" if pace_unit == 'mile' else "min/km"
        distance_unit = "miles" if pace_unit == 'mile' else "km"
        
        if pace_unit == 'mile':
            distance_display = distance / 1.60934
        else:
            distance_display = distance
        
        drift_str = f"{drift_pct:.2f}%" if drift_pct is not None else "N/A"
        pace_gap_str = ""
        if pace_gap is not None:
            if pace_gap > 0:
                pace_gap_str = f"当前配速比目标慢 {pace_gap:.0f} 秒/公里" if language == 'Chinese' else f"Current pace is {pace_gap:.0f} seconds slower per km than target"
            else:
                pace_gap_str = f"当前配速比目标快 {abs(pace_gap):.0f} 秒/公里" if language == 'Chinese' else f"Current pace is {abs(pace_gap):.0f} seconds faster per km than target"
        
        # Build system prompt based on language
        if language == 'Chinese':
            system_prompt = f"""你是一位专业的跑步教练，正在分析跑者的表现并提供全面的训练指导。

**用户资料：**
- 年龄: {age}
- 性别: {gender}
- 每周可用训练时间: {weekly_hours} 小时

**训练目标：**
- 目标配速: {target_pace} {pace_unit_label}
- 目标日期: {target_date} ({days_str})
- 剩余时间: {weeks_str}
- 配速单位: {pace_unit_label}

**今日跑步分析：**
- 距离: {distance_display:.2f} {distance_unit}
- 平均配速: {avg_pace} {pace_unit_label} {pace_gap_str}
- 平均心率: {avg_hr} bpm
- 心脏漂移: {drift_str} (负值表示后半程效率下降，表明疲劳)
- 配速类型: {run_type}
- 主观感受: {subjective_feeling if subjective_feeling else '未提供'}

{historical_summary}

**你的任务 - 以 JSON 格式提供三个独立的回复（全部使用中文）：**

1. **immediate_advice**: 即时评估和下次训练建议
   - 评估用户是否按计划达成目标
   - 分析心脏漂移和主观感受
   - 推荐下一次训练（何时：具体日期，什么：类型、时长、配速/心率目标）
   - 是否需要休息？如果需要，休息几天？
   - 使用 {pace_unit_label} 作为配速单位

2. **training_plan**: 详细的周训练计划
   - 创建一个全面的计划，在目标日期前达到目标配速
   - 考虑：每周可用 {weekly_hours} 小时
   - 包括：轻松跑、节奏跑、间歇跑、长距离跑、休息日
   - 为每种训练类型指定配速区间和心率区间
   - 逐步增加训练量和强度
   - 包含恢复周
   - 格式为周计划分解
   - 所有配速使用 {pace_unit_label}，距离使用 {distance_unit}

3. **strategy**: 训练策略和原理
   - 解释计划背后的原理
   - 关键里程碑和检查点
   - 过度训练的警告信号
   - 如果落后于进度如何调整

返回 JSON 对象，包含以下键："immediate_advice", "training_plan", "strategy"
具体说明日期、配速（{pace_unit_label}）、距离（{distance_unit}）和时长。
全部使用中文回复。"""
        else:
            system_prompt = f"""You are an expert running coach analyzing a runner's performance and providing comprehensive training guidance.

**User Profile:**
- Age: {age}
- Gender: {gender}
- Available Training Time: {weekly_hours} hours per week

**Training Goal:**
- Target Pace: {target_pace} {pace_unit_label}
- Target Date: {target_date} ({days_str})
- Time Remaining: {weeks_str}
- Pace Unit: {pace_unit_label}

**Today's Run Analysis:**
- Distance: {distance_display:.2f} {distance_unit}
- Average Pace: {avg_pace} {pace_unit_label} {pace_gap_str}
- Average Heart Rate: {avg_hr} bpm
- Cardiac Drift: {drift_str} (negative means efficiency dropped in 2nd half, indicating fatigue)
- Pacing Type: {run_type}
- Subjective Feeling: {subjective_feeling if subjective_feeling else 'Not provided'}

{historical_summary}

**Your Task - Provide THREE separate responses as JSON in English:**

1. **immediate_advice**: Immediate assessment and next workout recommendation
   - Assess if the user is on track for their goal
   - Analyze cardiac drift and subjective feeling
   - Recommend the NEXT workout (when: specific day/date, what: type, duration, pace/HR targets)
   - Should they rest? If yes, how many days?
   - Use {pace_unit_label} for pace units

2. **training_plan**: Detailed week-by-week training plan
   - Create a comprehensive plan to achieve the target pace by the target date
   - Consider: {weekly_hours} hours per week available
   - Include: Easy runs, tempo runs, intervals, long runs, rest days
   - Specify pace zones and HR zones for each workout type
   - Progressively build volume and intensity
   - Account for recovery weeks
   - Format as week-by-week breakdown
   - Use {pace_unit_label} for all pace references and {distance_unit} for distances

3. **strategy**: Training strategy and rationale
   - Explain the rationale behind the plan
   - Key milestones and checkpoints
   - Warning signs of overtraining
   - How to adjust if falling behind schedule

Return your response as a JSON object with these exact keys: "immediate_advice", "training_plan", "strategy"
Be specific with dates, paces (in {pace_unit_label}), distances (in {distance_unit}), and durations.
Respond in English."""

        user_message = "请分析我的跑步数据并提供全面的教练建议和训练计划。" if language == 'Chinese' else "Please analyze my run and provide comprehensive coaching advice with training plan."
        
        # Call OpenAI API
        print(f"\n{'='*60}")
        print("Calling OpenAI API...")
        print(f"Model: gpt-5")
        print(f"Language: {language}")
        print(f"Max tokens: 3000")
        print(f"Base URL: {SUPER_MIND_BASE_URL}")
        print(f"API Key: {SUPER_MIND_API_KEY[:20]}..." if SUPER_MIND_API_KEY else "NOT SET")
        print(f"{'='*60}\n")
        
        try:
            completion = openai_client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=3000,
                response_format={"type": "json_object"}
            )
            
            print(f"API call successful!")
            print(f"Completion object: {type(completion)}")
            print(f"Choices count: {len(completion.choices)}")
            
            if len(completion.choices) > 0:
                response_text = completion.choices[0].message.content
                print(f"Raw response length: {len(response_text)} characters")
                print(f"First 500 chars: {response_text[:500]}")
            else:
                print("ERROR: No choices in completion response!")
                print(f"Full completion object: {completion}")
                raise ValueError("No choices in completion response")
                
        except Exception as api_error:
            print(f"API call failed: {api_error}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise
        
        # Parse JSON response
        try:
            response_dict = json.loads(response_text)
            immediate_advice = response_dict.get('immediate_advice', '')
            training_plan = response_dict.get('training_plan', '')
            strategy = response_dict.get('strategy', '')
            
            print(f"\n{'='*60}")
            print("Parsed Response:")
            print(f"immediate_advice length: {len(immediate_advice)} chars")
            print(f"training_plan length: {len(training_plan)} chars")
            print(f"strategy length: {len(strategy)} chars")
            print(f"{'='*60}\n")
            
            return {
                "success": True,
                "immediate_advice": immediate_advice,
                "training_plan": training_plan,
                "strategy": strategy,
                "raw_response": response_text[:500]  # First 500 chars for debugging
            }
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text[:1000]}")
            return {
                "success": False,
                "error": f"JSON parsing failed: {str(e)}",
                "raw_response": response_text[:1000]
            }
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error: {e}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Error getting coaching advice: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "Coach Advice Test API",
        "endpoints": {
            "/coach/advice": "POST - Get coaching advice",
            "/docs": "Swagger UI documentation"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
