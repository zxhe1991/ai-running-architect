"""
AI Running Architect - Streamlit Application
Complete coaching app integrating historical data, current run data, and user profile.
"""
import streamlit as st
import pandas as pd
import numpy as np
import faiss
import pickle
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

# Import analyzers
from tcx_analyzer import analyze_tcx
from csv_analyzer import analyze_csv
from build_index import build_index
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
# Try SUPER_MIND_API_KEY first, then AI_BUILDER_TOKEN (for deployment platform)
SUPER_MIND_API_KEY = os.getenv("SUPER_MIND_API_KEY") or os.getenv("AI_BUILDER_TOKEN")
SUPER_MIND_BASE_URL = os.getenv("SUPER_MIND_BASE_URL", "https://space.ai-builders.com/backend/v1")

if not SUPER_MIND_API_KEY:
    st.error("SUPER_MIND_API_KEY or AI_BUILDER_TOKEN not found! Please configure it in .env file or deployment config.")
    st.stop()

openai_client = OpenAI(
    api_key=SUPER_MIND_API_KEY,
    base_url=SUPER_MIND_BASE_URL
)

# Page configuration
# Read PORT from environment variable (required for deployment)
PORT = int(os.getenv("PORT", "8501"))

st.set_page_config(
    page_title="AI Running Architect",
    page_icon="🏃",
    layout="wide"
)

# Initialize session state and load persisted data
USER_CONFIG_FILE = "user_config.json"

def load_user_config():
    """Load user configuration from file"""
    if os.path.exists(USER_CONFIG_FILE):
        try:
            with open(USER_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_user_config(config):
    """Save user configuration to file"""
    try:
        with open(USER_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.warning(f"Failed to save user config: {e}")

# Load persisted configuration
persisted_config = load_user_config()

# Initialize session state with persisted values or defaults
# Don't auto-load pre-existing index files - only use user-defined data
if 'knowledge_base_built' not in st.session_state:
    # Only set to True if user explicitly builds index (not from pre-existing files)
    st.session_state.knowledge_base_built = False
    
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = persisted_config.get('user_profile', {})
    
if 'goal' not in st.session_state:
    st.session_state.goal = persisted_config.get('goal', {})
    
if 'pace_unit' not in st.session_state:
    st.session_state.pace_unit = persisted_config.get('pace_unit', 'km')
    
if 'language' not in st.session_state:
    st.session_state.language = persisted_config.get('language', 'Chinese')

# Language translations
TRANSLATIONS = {
    'Chinese': {
        'app_title': '🏃 AI 跑步教练',
        'app_subtitle': '您的个人AI跑步教练',
        'setup_context': '⚙️ 设置与上下文',
        'user_profile': '👤 用户资料',
        'age': '年龄',
        'gender': '性别',
        'male': '男性',
        'female': '女性',
        'other': '其他',
        'the_goal': '🎯 目标',
        'target_pace': '目标配速',
        'target_date': '目标日期',
        'pace_unit': '配速单位',
        'pace_unit_km': '每公里 (min/km)',
        'pace_unit_mile': '每英里 (min/mi)',
        'training_availability': '⏰ 训练时间',
        'weekly_hours': '每周可用训练时间（小时）',
        'historical_data': '📚 历史跑步数据',
        'upload_csv': '上传 Garmin_Runing.csv',
        'file_uploaded': '文件已上传！',
        'build_index': '🔨 构建历史数据索引',
        'index_built': '历史数据索引构建成功！已索引 {count} 次跑步。',
        'index_error': '构建历史数据索引时出错：{error}',
        'index_ready': '✅ 历史数据已就绪',
        'index_not_built': '⚠️ 历史数据尚未构建',
        'todays_run': '📊 今日跑步数据',
        'upload_today_csv': '上传 Running_Today.csv',
        'upload_today_csv_help': '上传今日跑步数据的 CSV 文件（格式类似 Garmin CSV）',
        'csv_uploaded': 'CSV 文件已上传！',
        'subjective_feeling': '💭 主观感受',
        'feeling_placeholder': '例如：腿部感觉沉重，感觉很强壮，最后2公里很吃力...',
        'analyze_button': '🔍 分析并获取建议',
        'upload_csv_first': '请先上传 CSV 文件！',
        'no_historical_warning': '历史数据未构建。分析将在没有历史上下文的情况下进行。',
        'analyzing': '正在分析今日跑步...',
        'key_metrics': '📈 关键指标',
        'distance': '距离',
        'cardiac_drift': '心脏漂移',
        'avg_hr': '平均心率',
        'avg_pace': '平均配速',
        'searching_historical': '正在搜索历史跑步记录...',
        'historical_context': '📚 历史对比',
        'similar_runs': '您历史中的相似跑步：',
        'similar_run': '相似跑步 #{num}',
        'date': '日期',
        'avg_pace_label': '平均配速',
        'avg_hr_label': '平均心率',
        'aerobic_te': '有氧训练效果',
        'getting_advice': '正在获取AI教练建议和训练计划...',
        'immediate_assessment': '🎓 即时评估与下次训练',
        'detailed_plan': '📅 详细训练计划',
        'plan_not_available': '训练计划不可用',
        'training_strategy': '💡 训练策略与原理',
        'strategy_not_available': '策略信息不可用',
        'detailed_analysis': '📊 详细分析',
        'cardiac_drift_details': '心脏漂移详情',
        'first_half_efficiency': '前半程效率',
        'first_half_avg_hr': '前半程平均心率',
        'second_half_efficiency': '后半程效率',
        'second_half_avg_hr': '后半程平均心率',
        'pacing_analysis': '配速分析',
        'run_type': '跑步类型',
        'speed_variation': '速度变化',
        'cadence_metrics': '步频指标',
        'avg_cadence': '平均步频',
        'consistency': '一致性',
        'vertical_oscillation': '垂直振幅',
        'average': '平均值',
        'assessment': '评估',
        'cardiac_drift_details': '心脏漂移详情',
        'first_half_efficiency': '前半程效率',
        'first_half_avg_hr': '前半程平均心率',
        'second_half_efficiency': '后半程效率',
        'second_half_avg_hr': '后半程平均心率',
        'pacing_analysis': '配速分析',
        'run_type': '跑步类型',
        'speed_variation': '速度变化',
        'cadence_metrics': '步频指标',
        'avg_cadence': '平均步频',
        'consistency': '一致性',
        'vertical_oscillation': '垂直振幅',
        'average': '平均值',
        'assessment': '评估',
        'language_choice': '🌐 语言选择',
        'select_language': '选择语言'
    },
    'English': {
        'app_title': '🏃 AI Running Architect',
        'app_subtitle': 'Your Personal Running Coach Powered by AI',
        'setup_context': '⚙️ Setup & Context',
        'user_profile': '👤 User Profile',
        'age': 'Age',
        'gender': 'Gender',
        'male': 'Male',
        'female': 'Female',
        'other': 'Other',
        'the_goal': '🎯 The Goal',
        'target_pace': 'Target Pace (mm:ss)',
        'target_date': 'Target Date',
        'pace_unit': 'Pace Unit',
        'pace_unit_km': 'Per Kilometer (min/km)',
        'pace_unit_mile': 'Per Mile (min/mi)',
        'training_availability': '⏰ Training Availability',
        'weekly_hours': 'Available Training Hours per Week',
        'historical_data': '📚 Historical Running Data',
        'upload_csv': 'Upload Garmin_Runing.csv',
        'file_uploaded': 'File uploaded!',
        'build_index': '🔨 Build Historical Data Index',
        'index_built': 'Historical data index built successfully! Indexed {count} runs.',
        'index_error': 'Error building historical data index: {error}',
        'index_ready': '✅ Historical data ready',
        'index_not_built': '⚠️ Historical data not built yet',
        'todays_run': '📊 Today\'s Run Data',
        'upload_today_csv': 'Upload Running_Today.csv',
        'upload_today_csv_help': 'Upload today\'s running data CSV file (similar to Garmin CSV format)',
        'csv_uploaded': 'CSV file uploaded!',
        'subjective_feeling': '💭 Subjective Feeling',
        'feeling_placeholder': 'e.g., Legs felt heavy, felt strong, struggled in the last 2km...',
        'analyze_button': '🔍 Analyze & Coach Me',
        'upload_csv_first': 'Please upload a CSV file first!',
        'no_historical_warning': 'Historical data not built. Analysis will proceed without historical context.',
        'analyzing': 'Analyzing today\'s run...',
        'key_metrics': '📈 Key Metrics',
        'distance': 'Distance',
        'cardiac_drift': 'Cardiac Drift',
        'avg_hr': 'Avg HR',
        'avg_pace': 'Avg Pace',
        'searching_historical': 'Searching historical runs...',
        'historical_context': '📚 Historical Context',
        'similar_runs': 'Similar runs from your history:',
        'similar_run': 'Similar Run #{num}',
        'date': 'Date',
        'avg_pace_label': 'Avg Pace',
        'avg_hr_label': 'Avg HR',
        'aerobic_te': 'Aerobic TE',
        'getting_advice': 'Getting coaching advice and training plan from AI...',
        'immediate_assessment': '🎓 Immediate Assessment & Next Workout',
        'detailed_plan': '📅 Detailed Training Plan',
        'plan_not_available': 'Training plan not available',
        'training_strategy': '💡 Training Strategy & Rationale',
        'strategy_not_available': 'Strategy information not available',
        'detailed_analysis': '📊 Detailed Analysis',
        'cardiac_drift_details': 'Cardiac Drift Details',
        'first_half_efficiency': 'First Half Efficiency',
        'first_half_avg_hr': 'First Half Avg HR',
        'second_half_efficiency': 'Second Half Efficiency',
        'second_half_avg_hr': 'Second Half Avg HR',
        'pacing_analysis': 'Pacing Analysis',
        'run_type': 'Run Type',
        'speed_variation': 'Speed Variation',
        'cadence_metrics': 'Cadence Metrics',
        'avg_cadence': 'Average Cadence',
        'consistency': 'Consistency',
        'vertical_oscillation': 'Vertical Oscillation',
        'average': 'Average',
        'assessment': 'Assessment',
        'cardiac_drift_details': 'Cardiac Drift Details',
        'first_half_efficiency': 'First Half Efficiency',
        'first_half_avg_hr': 'First Half Avg HR',
        'second_half_efficiency': 'Second Half Efficiency',
        'second_half_avg_hr': 'Second Half Avg HR',
        'pacing_analysis': 'Pacing Analysis',
        'run_type': 'Run Type',
        'speed_variation': 'Speed Variation',
        'cadence_metrics': 'Cadence Metrics',
        'avg_cadence': 'Average Cadence',
        'consistency': 'Consistency',
        'vertical_oscillation': 'Vertical Oscillation',
        'average': 'Average',
        'assessment': 'Assessment',
        'language_choice': '🌐 Language Choice',
        'select_language': 'Select Language'
    }
}

def t(key: str) -> str:
    """Get translated text."""
    lang = st.session_state.language
    return TRANSLATIONS.get(lang, TRANSLATIONS['English']).get(key, key)


def parse_pace_to_seconds(pace_str: str) -> Optional[float]:
    """Convert pace string (e.g., '5:30') to seconds per km."""
    if not pace_str or pace_str == '':
        return None
    try:
        parts = str(pace_str).strip().split(':')
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except:
        return None
    return None


def create_run_summary(row: pd.Series) -> str:
    """Create a text summary for a run."""
    date = row.get('Date', 'Unknown')
    distance = row.get('Distance', 'N/A')
    avg_hr = row.get('Avg HR', 'N/A')
    avg_pace = row.get('Avg Pace', 'N/A')
    aerobic_te = row.get('Aerobic TE', 'N/A')
    return f"Date: {date}, Dist: {distance}, HR: {avg_hr}, Pace: {avg_pace}, Effort: {aerobic_te}"


def build_knowledge_base(csv_file_path: str):
    """Build FAISS index from CSV file."""
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Loading CSV file...")
        # Load and clean data
        df = pd.read_csv(csv_file_path)
        progress_bar.progress(0.1)
        
        # Clean data
        status_text.text("Cleaning data...")
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Convert Avg Pace to seconds
        if 'Avg Pace' in df.columns:
            df['Avg Pace (seconds)'] = df['Avg Pace'].apply(parse_pace_to_seconds)
        
        # Clean numeric columns
        numeric_columns = ['Calories', 'Steps']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').replace('', np.nan)
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        progress_bar.progress(0.2)
        
        # Create summaries
        status_text.text("Creating run summaries...")
        summaries = []
        for idx, row in df.iterrows():
            summary = create_run_summary(row)
            summaries.append(summary)
        
        progress_bar.progress(0.3)
        
        # Vectorize summaries
        status_text.text("Creating embeddings...")
        embeddings = []
        total = len(summaries)
        for i, summary in enumerate(summaries):
            progress = 0.3 + (i / total) * 0.6
            progress_bar.progress(progress)
            status_text.text(f"Embedding {i + 1}/{total}...")
            
            try:
                response = openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=summary
                )
                embedding = np.array(response.data[0].embedding, dtype=np.float32)
                embeddings.append(embedding)
            except Exception as e:
                st.warning(f"Error embedding summary {i + 1}: {e}")
                embeddings.append(np.zeros(1536, dtype=np.float32))
        
        # Build FAISS index
        status_text.text("Building FAISS index...")
        embeddings_array = np.array(embeddings).astype('float32')
        dimension = embeddings_array.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings_array)
        
        progress_bar.progress(0.9)
        
        # Save index and data
        status_text.text("Saving index...")
        faiss.write_index(index, "garmin.index")
        with open("garmin_data.pkl", 'wb') as f:
            pickle.dump(df, f)
        
        progress_bar.progress(1.0)
        status_text.text("Complete!")
        
        st.session_state.knowledge_base_built = True
        return True, len(df)
            
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        st.error(f"Error: {str(e)}\n\n{error_trace}")
        return False, str(e)


def search_similar_runs(query_text: str, k: int = 3) -> List[Dict[str, Any]]:
    """Search for similar runs in the knowledge base."""
    try:
        # Load index and data
        if not os.path.exists("garmin.index") or not os.path.exists("garmin_data.pkl"):
            return []
        
        index = faiss.read_index("garmin.index")
        
        # Try to load pickle file with StringDtype handling
        df = None
        pickle_error = None
        
        try:
            with open("garmin_data.pkl", 'rb') as f:
                df = pickle.load(f)
        except Exception as e:
            pickle_error = str(e)
            # Check if it's a StringDtype error
            if 'StringDtype' in str(e) or 'string' in str(e).lower():
                # Try to reload from CSV and rebuild
                if os.path.exists("Garmin_Runing.csv"):
                    try:
                        df = pd.read_csv("Garmin_Runing.csv")
                        # Clean and prepare data
                        if 'Date' in df.columns:
                            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                        # Convert all string columns to object dtype before saving
                        for col in df.columns:
                            if df[col].dtype.name == 'string' or 'StringDtype' in str(df[col].dtype):
                                df[col] = df[col].astype('object')
                        
                        # Save with compatible format
                        with open("garmin_data.pkl", 'wb') as f:
                            pickle.dump(df, f)
                        st.success("已修复历史数据文件格式")
                    except Exception as csv_error:
                        st.error(f"无法从 CSV 重新加载: {csv_error}")
                        return []
                else:
                    st.error("无法加载历史数据。请重新构建索引。")
                    return []
            else:
                st.error(f"加载 pickle 文件时出错: {e}")
                return []
        
        # Fix StringDtype columns if still present
        if df is not None:
            for col in df.columns:
                try:
                    dtype_str = str(df[col].dtype)
                    if 'string' in dtype_str.lower() or 'StringDtype' in dtype_str:
                        df[col] = df[col].astype('object')
                except Exception:
                    # If conversion fails, try to recreate the column
                    try:
                        df[col] = df[col].astype(str).astype('object')
                    except Exception:
                        pass  # Skip if still fails
        
        # Embed query
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query_text
        )
        query_embedding = np.array([response.data[0].embedding], dtype=np.float32)
        
        # Search
        distances, indices = index.search(query_embedding, k)
        
        # Get similar runs
        similar_runs = []
        for i, idx in enumerate(indices[0]):
            if idx < len(df):
                run_data = df.iloc[idx].to_dict()
                similar_runs.append({
                    'index': int(idx),
                    'distance': float(distances[0][i]),
                    'data': run_data
                })
        
        return similar_runs
        
    except Exception as e:
        st.error(f"Error searching knowledge base: {e}")
        return []


def calculate_days_until_target(target_date_str: str) -> Optional[int]:
    """Calculate days until target date."""
    try:
        if "month" in target_date_str.lower():
            # Parse "In 3 months"
            months = int(''.join(filter(str.isdigit, target_date_str)))
            target_date = datetime.now() + timedelta(days=months * 30)
        elif "week" in target_date_str.lower():
            weeks = int(''.join(filter(str.isdigit, target_date_str)))
            target_date = datetime.now() + timedelta(weeks=weeks)
        else:
            # Try to parse as date
            target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
        
        days_until = (target_date - datetime.now()).days
        return days_until
    except:
        return None


def get_coach_advice(user_profile: Dict, goal: Dict, today_metrics: Dict, 
                     historical_runs: List[Dict], subjective_feeling: str) -> Dict[str, str]:
    """Get coaching advice and training plan from LLM."""
    
    # Build context
    age = user_profile.get('age', 'Unknown')
    gender = user_profile.get('gender', 'Unknown')
    target_pace = goal.get('target_pace', 'Unknown')
    target_date = goal.get('target_date', 'Unknown')
    weekly_hours = goal.get('weekly_hours', 5.0)
    
    # Calculate days until target
    days_until = calculate_days_until_target(target_date)
    days_str = f"{days_until} days from now" if days_until else "Unknown"
    weeks_until = days_until / 7.0 if days_until else None
    
    # Today's metrics
    drift_pct = today_metrics.get('cardiac_drift', {}).get('drift_percentage')
    avg_hr = today_metrics.get('basic_stats', {}).get('avg_heart_rate')
    avg_pace = today_metrics.get('basic_stats', {}).get('avg_pace')
    distance = today_metrics.get('basic_stats', {}).get('total_distance_km')
    run_type = today_metrics.get('pacing_variance', {}).get('run_type', 'Unknown')
    
    # Parse current pace to compare with target
    current_pace_seconds = parse_pace_to_seconds(avg_pace) if avg_pace else None
    target_pace_seconds = parse_pace_to_seconds(target_pace) if target_pace else None
    
    pace_gap = None
    if current_pace_seconds and target_pace_seconds:
        pace_gap = current_pace_seconds - target_pace_seconds  # Positive means slower than target
    
    # Historical context
    historical_summary = ""
    if historical_runs:
        lang = st.session_state.language
        if lang == 'Chinese':
            historical_summary = "\n**历史相似跑步：**\n"
        else:
            historical_summary = "\n**Historical Similar Runs:**\n"
        
        for i, run in enumerate(historical_runs[:3], 1):
            run_data = run['data']
            # Convert pandas Series to dict if needed
            if isinstance(run_data, pd.Series):
                run_data = run_data.to_dict()
            
            hist_date = run_data.get('Date', 'Unknown')
            if isinstance(hist_date, pd.Timestamp):
                hist_date = hist_date.strftime('%Y-%m-%d')
            elif hasattr(hist_date, 'strftime'):
                hist_date = hist_date.strftime('%Y-%m-%d')
            
            hist_distance = run_data.get('Distance', 'N/A')
            hist_pace = run_data.get('Avg Pace', 'N/A')
            hist_hr = run_data.get('Avg HR', 'N/A')
            
            if lang == 'Chinese':
                historical_summary += f"{i}. 日期: {hist_date}, 距离: {hist_distance}, 配速: {hist_pace}, 心率: {hist_hr}\n"
            else:
                historical_summary += f"{i}. Date: {hist_date}, Distance: {hist_distance}, Pace: {hist_pace}, HR: {hist_hr}\n"
    
    # Build system prompt
    drift_str = f"{drift_pct:.2f}%" if drift_pct is not None else "N/A"
    pace_gap_str = ""
    if pace_gap is not None:
        if pace_gap > 0:
            pace_gap_str = f"Current pace is {pace_gap:.0f} seconds slower per km than target"
        else:
            pace_gap_str = f"Current pace is {abs(pace_gap):.0f} seconds faster per km than target"
    
    weeks_str = f"{weeks_until:.1f} weeks" if weeks_until else "Unknown"
    
    # Get pace unit for display
    pace_unit = goal.get('pace_unit', 'km')
    pace_unit_label = "min/mi" if pace_unit == 'mile' else "min/km"
    distance_unit = "miles" if pace_unit == 'mile' else "km"
    
    # Convert distance for display
    if pace_unit == 'mile':
        distance_display = distance / 1.60934
    else:
        distance_display = distance
    
    # Convert pace for display
    def convert_pace_for_display(pace_str, target_unit):
        """Convert pace from min/km to min/mile or vice versa."""
        if not pace_str:
            return "N/A"
        pace_seconds = parse_pace_to_seconds(pace_str)
        if not pace_seconds:
            return pace_str
        
        if target_unit == 'mile':
            pace_seconds_mile = pace_seconds * 1.60934
        else:
            pace_seconds_mile = pace_seconds / 1.60934
        
        minutes = int(pace_seconds_mile // 60)
        seconds = int(pace_seconds_mile % 60)
        return f"{minutes}:{seconds:02d}"
    
    avg_pace_display = convert_pace_for_display(avg_pace, pace_unit)
    target_pace_display = convert_pace_for_display(target_pace, pace_unit)
    
    # Language for prompt
    lang = st.session_state.language
    response_lang = "Chinese" if lang == 'Chinese' else "English"
    
    # Build prompt based on language
    if response_lang == 'Chinese':
        system_prompt = f"""你是一位专业的跑步教练，正在分析跑者的表现并提供全面的训练指导。

**用户资料：**
- 年龄: {age}
- 性别: {gender}
- 每周可用训练时间: {weekly_hours} 小时

**训练目标：**
- 目标配速: {target_pace_display} {pace_unit_label}
- 目标日期: {target_date} ({days_str})
- 剩余时间: {weeks_str}
- 配速单位: {pace_unit_label}

**今日跑步分析：**
- 距离: {distance_display:.2f} {distance_unit}
- 平均配速: {avg_pace_display} {pace_unit_label} {pace_gap_str}
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

    # Check if we should use mock response (when API has issues)
    USE_MOCK_RESPONSE = os.getenv("USE_MOCK_RESPONSE", "false").lower() == "true"
    
    if USE_MOCK_RESPONSE:
        # Use mock response as temporary solution
        from mock_coach_response import get_mock_coach_advice
        return get_mock_coach_advice(
            user_profile,
            goal,
            today_metrics,
            historical_runs,
            subjective_feeling,
            response_lang
        )
    
    try:
        user_message = "请分析我的跑步数据并提供全面的教练建议和训练计划。" if response_lang == 'Chinese' else "Please analyze my run and provide comprehensive coaching advice with training plan."
        
        # Try without json_object first, then parse JSON manually
        try:
            completion = openai_client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=2000,
                # Don't use json_object format - it seems to cause empty responses
            )
            
            response_text = completion.choices[0].message.content
            
            # Check if response is empty
            if not response_text or len(response_text.strip()) == 0:
                # If empty, try to extract from usage or return error
                usage = completion.usage
                error_msg = f"API 返回了空响应（使用了 {usage.completion_tokens} tokens）。这可能是 API 端点的问题。"
                if response_lang == 'English':
                    error_msg = f"API returned empty response (used {usage.completion_tokens} tokens). This may be an API endpoint issue."
                
                return {
                    'immediate_advice': error_msg,
                    'training_plan': error_msg,
                    'strategy': error_msg
                }
            
            # Try to extract JSON from response
            try:
                # Look for JSON object in response
                if '{' in response_text and '}' in response_text:
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    json_str = response_text[start:end]
                    response_dict = json.loads(json_str)
                    
                    return {
                        'immediate_advice': response_dict.get('immediate_advice', ''),
                        'training_plan': response_dict.get('training_plan', ''),
                        'strategy': response_dict.get('strategy', '')
                    }
                else:
                    # If no JSON found, return the text as immediate_advice
                    return {
                        'immediate_advice': response_text[:1000],
                        'training_plan': '请查看即时评估部分' if response_lang == 'Chinese' else 'Please see immediate assessment',
                        'strategy': '请查看即时评估部分' if response_lang == 'Chinese' else 'Please see immediate assessment'
                    }
            except json.JSONDecodeError:
                # If JSON parsing fails, return the text
                return {
                    'immediate_advice': response_text[:1000],
                    'training_plan': response_text[1000:2000] if len(response_text) > 1000 else '请查看即时评估部分' if response_lang == 'Chinese' else 'Please see immediate assessment',
                    'strategy': response_text[2000:3000] if len(response_text) > 2000 else '请查看即时评估部分' if response_lang == 'Chinese' else 'Please see immediate assessment'
                }
                
        except Exception as api_error:
            error_msg = f"API 调用失败: {str(api_error)}"
            if response_lang == 'English':
                error_msg = f"API call failed: {str(api_error)}"
            
            return {
                'immediate_advice': error_msg,
                'training_plan': error_msg,
                'strategy': error_msg
            }
        
    except Exception as e:
        return {
            'immediate_advice': f"Error getting coaching advice: {str(e)}",
            'training_plan': '',
            'strategy': ''
        }




# Sidebar
with st.sidebar:
    st.header(t('setup_context'))
    
    # Language Choice
    st.subheader(t('language_choice'))
    language = st.selectbox(
        t('select_language'),
        ["Chinese", "English"],
        index=0 if st.session_state.language == 'Chinese' else 1
    )
    if st.session_state.language != language:
        st.session_state.language = language
        # Save immediately when language changes
        save_user_config({
            'user_profile': st.session_state.user_profile,
            'goal': st.session_state.goal,
            'pace_unit': st.session_state.pace_unit,
            'language': st.session_state.language
        })
    
    # User Profile
    st.subheader(t('user_profile'))
    age = st.number_input(
        t('age'), 
        min_value=10, 
        max_value=100, 
        value=st.session_state.user_profile.get('age', 30), 
        step=1
    )
    gender_options = [t('male'), t('female'), t('other')] if language == 'Chinese' else ["Male", "Female", "Other"]
    current_gender = st.session_state.user_profile.get('gender', gender_options[0])
    gender_index = gender_options.index(current_gender) if current_gender in gender_options else 0
    gender = st.selectbox(t('gender'), gender_options, index=gender_index)
    
    # Update user profile and save
    st.session_state.user_profile = {
        'age': age,
        'gender': gender
    }
    
    # Goal
    st.subheader(t('the_goal'))
    
    # Pace Unit Selection
    pace_unit = st.radio(
        t('pace_unit'),
        ['km', 'mile'],
        index=0 if st.session_state.pace_unit == 'km' else 1,
        horizontal=True
    )
    st.session_state.pace_unit = pace_unit
    
    pace_help = t('pace_unit_km') if pace_unit == 'km' else t('pace_unit_mile')
    target_pace = st.text_input(
        t('target_pace'), 
        value=st.session_state.goal.get('target_pace', "5:00"), 
        help=pace_help
    )
    target_date = st.text_input(
        t('target_date'), 
        value=st.session_state.goal.get('target_date', "In 3 months"), 
        help="e.g., 'In 3 months' or '2024-12-31'"
    )
    
    # Training Availability
    st.subheader(t('training_availability'))
    weekly_hours = st.number_input(
        t('weekly_hours'), 
        min_value=1.0, 
        max_value=20.0, 
        value=st.session_state.goal.get('weekly_hours', 5.0), 
        step=0.5, 
        help="How many hours can you train per week?"
    )
    
    st.session_state.goal = {
        'target_pace': target_pace,
        'target_date': target_date,
        'weekly_hours': weekly_hours,
        'pace_unit': pace_unit
    }
    
    # Save configuration whenever it changes
    save_user_config({
        'user_profile': st.session_state.user_profile,
        'goal': st.session_state.goal,
        'pace_unit': st.session_state.pace_unit,
        'language': st.session_state.language
    })
    
    # Historical Running Data
    st.subheader(t('historical_data'))
    
    # Instructions for getting historical data
    with st.expander("📖 " + ("如何获取历史数据" if language == 'Chinese' else "How to Get Historical Data")):
        if language == 'Chinese':
            st.markdown("""
            **获取历史跑步数据：**
            
            • **登录网站：** 在电脑上访问 Garmin Connect 网页版 并登录。
            
            • **进入报告：** 点击左侧菜单栏的 "Reports" (报告)。
            
            • **选择跑步趋势：** 选择 "Running" (跑步) -> "Activity Trends" (活动趋势)。
            
            • **导出：** 点击图表右上角的 "Export" 按钮，选择 "Export to CSV"
            """)
        else:
            st.markdown("""
            **Get Historical Running Data:**
            
            • **Login:** Access Garmin Connect web on your computer and log in.
            
            • **Go to Reports:** Click "Reports" in the left menu bar.
            
            • **Select Running Trends:** Choose "Running" -> "Activity Trends".
            
            • **Export:** Click the "Export" button in the top right corner of the chart, select "Export to CSV"
            """)
    
    csv_file = st.file_uploader(
        "Upload Historical Garmin running csv data" if language == 'English' else "上传历史 Garmin 跑步 CSV 数据",
        type=['csv'],
        help="Upload your historical running data CSV file exported from Garmin Connect"
    )
    
    if csv_file is not None:
        # Save uploaded file
        with open("Garmin_Runing.csv", "wb") as f:
            f.write(csv_file.getbuffer())
        st.success(t('file_uploaded'))
        st.info("💡 " + ("历史数据已上传。将在点击'分析并获取建议'时自动构建索引。" if language == 'Chinese' else "Historical data uploaded. Index will be built automatically when you click 'Analyze & Coach Me'."))
    
    # Only show historical data status if user has explicitly built index
    # Don't show default/pre-existing index files - only show if user built it
    if st.session_state.knowledge_base_built:
        # User has built index from their uploaded CSV
        if os.path.exists("garmin.index") and os.path.exists("garmin_data.pkl"):
            st.success(t('index_ready'))
            # Show how many runs are indexed
            try:
                with open("garmin_data.pkl", 'rb') as f:
                    df = pickle.load(f)
                    st.info(f"已索引 {len(df)} 次跑步记录" if language == 'Chinese' else f"Indexed {len(df)} runs")
            except:
                pass
    elif csv_file is not None:
        # User just uploaded CSV but index not built yet
        st.info("💡 " + ("历史数据已上传。将在点击'分析并获取建议'时自动构建索引。" if language == 'Chinese' else "Historical data uploaded. Index will be built automatically when you click 'Analyze & Coach Me'."))
    elif os.path.exists("Garmin_Runing.csv"):
        # CSV file exists but index not built yet
        st.info("💡 " + ("已检测到历史数据文件。点击'分析并获取建议'按钮将自动构建索引" if language == 'Chinese' else "Historical data file detected. Click 'Analyze & Coach Me' button to build index automatically"))
    else:
        # No CSV file uploaded
        st.info("💡 " + ("上传 Garmin_Runing.csv 文件以构建历史数据索引" if language == 'Chinese' else "Upload Garmin_Runing.csv file to build historical data index"))


# Main UI
st.title(t('app_title'))
st.markdown(f"### {t('app_subtitle')}")

# File uploader for CSV (Today's Run)
st.subheader(t('todays_run'))

# Instructions for getting today's data
with st.expander("📖 " + ("如何获取今日数据" if language == 'Chinese' else "How to Get Today's Data")):
    if language == 'Chinese':
        st.markdown("""
        **获取今日跑步数据：**
        
        • **打开活动：** 在 Garmin Connect 网页版中点击你刚刚完成的那次跑步活动。
        
        • **点击齿轮：** 在页面右上角找到 齿轮图标 (Settings)。
        
        • **选择导出：** 选择 "Export Splits to CSV"。
        """)
    else:
        st.markdown("""
        **Get Today's Running Data:**
        
        • **Open Activity:** Click on the running activity you just completed in Garmin Connect web.
        
        • **Click Gear:** Find the gear icon (Settings) in the top right corner of the page.
        
        • **Select Export:** Select "Export Splits to CSV".
        """)

csv_today_file = st.file_uploader(
    "Upload Today's Garmin running csv data" if language == 'English' else "上传今日 Garmin 跑步 CSV 数据",
    type=['csv'],
    help="Upload today's running data CSV file exported from Garmin Connect"
)

if csv_today_file is not None:
    # Save uploaded file
    with open("Running_Today.csv", "wb") as f:
        f.write(csv_today_file.getbuffer())
    st.success(t('csv_uploaded'))

# Subjective feeling
st.subheader(t('subjective_feeling'))
subjective_feeling = st.text_area(
    t('feeling_placeholder'),
    placeholder=t('feeling_placeholder'),
    height=100
)

# Analyze button
if st.button(t('analyze_button'), type="primary", use_container_width=True):
    if not os.path.exists("Running_Today.csv"):
        st.error(t('upload_csv_first'))
        st.stop()
    
    # Build historical index if CSV file exists but index is not built
    if os.path.exists("Garmin_Runing.csv") and not st.session_state.knowledge_base_built:
        with st.spinner("正在构建历史数据索引..." if language == 'Chinese' else "Building historical data index..."):
            success, result = build_knowledge_base("Garmin_Runing.csv")
            if success:
                st.success(t('index_built').format(count=result))
                st.session_state.knowledge_base_built = True
            else:
                st.warning(t('index_error').format(error=result))
                st.info("将继续分析，但不会使用历史数据上下文。" if language == 'Chinese' else "Will continue analysis without historical data context.")
    
    if not st.session_state.knowledge_base_built:
        st.warning(t('no_historical_warning'))
    
    # Analyze CSV file (Today's run)
    with st.spinner(t('analyzing')):
        try:
            today_analysis = analyze_csv("Running_Today.csv")
        except Exception as e:
            st.error(f"Error analyzing CSV file: {e}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")
            st.stop()
    
    # Convert pace based on unit selection
    pace_unit = st.session_state.pace_unit
    basic_stats = today_analysis.get('basic_stats', {})
    distance_km = basic_stats.get('total_distance_km', 0)
    avg_pace_km = basic_stats.get('avg_pace')
    
    # Convert distance
    if pace_unit == 'mile':
        distance_display = distance_km / 1.60934
        distance_unit = " mi"
    else:
        distance_display = distance_km
        distance_unit = " km"
    
    # Convert pace
    def convert_pace_to_unit(pace_str, target_unit):
        """Convert pace from min/km to min/mile or vice versa."""
        if not pace_str:
            return "N/A"
        pace_seconds = parse_pace_to_seconds(pace_str)
        if not pace_seconds:
            return pace_str
        
        if target_unit == 'mile':
            # Convert min/km to min/mile (multiply by 1.60934)
            pace_seconds_mile = pace_seconds * 1.60934
        else:
            # Convert min/mile to min/km (divide by 1.60934)
            pace_seconds_mile = pace_seconds / 1.60934
        
        minutes = int(pace_seconds_mile // 60)
        seconds = int(pace_seconds_mile % 60)
        return f"{minutes}:{seconds:02d}"
    
    avg_pace_display = convert_pace_to_unit(avg_pace_km, pace_unit)
    pace_unit_label = "min/mi" if pace_unit == 'mile' else "min/km"
    
    # Display key metrics
    st.header(t('key_metrics'))
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            t('distance'),
            f"{distance_display:.2f}{distance_unit}" if distance_display else "N/A"
        )
    
    with col2:
        drift = today_analysis.get('cardiac_drift', {}).get('drift_percentage')
        if drift is not None:
            drift_delta = None
            if drift > -5:
                drift_delta = "Good" if language == 'English' else "良好"
            elif drift < -10:
                drift_delta = "Concerning" if language == 'English' else "需关注"
            st.metric(
                t('cardiac_drift'),
                f"{drift:.2f}%",
                delta=drift_delta
            )
        else:
            st.metric(t('cardiac_drift'), "N/A")
    
    with col3:
        avg_hr = basic_stats.get('avg_heart_rate')
        st.metric(
            t('avg_hr'),
            f"{avg_hr:.1f} bpm" if avg_hr else "N/A"
        )
    
    with col4:
        st.metric(
            t('avg_pace'),
            f"{avg_pace_display} {pace_unit_label}" if avg_pace_display != "N/A" else "N/A"
        )
    
    # Search similar runs (used internally for AI analysis, not displayed)
    historical_runs = []
    if st.session_state.knowledge_base_built:
        # Double-check that files actually exist before searching
        if not (os.path.exists("garmin.index") and os.path.exists("garmin_data.pkl")):
            st.warning("⚠️ 历史数据索引文件不存在，请重新构建索引。" if language == 'Chinese' else "⚠️ Historical data index files not found. Please rebuild index.")
            st.session_state.knowledge_base_built = False
        else:
            # Silently search for historical context (used in AI analysis)
            try:
                # Create query from today's run
                distance = today_analysis['basic_stats'].get('total_distance_km', 0)
                if distance == 0:
                    distance = today_analysis['basic_stats'].get('total_distance', 0)
                pace = today_analysis['basic_stats'].get('avg_pace') or today_analysis['basic_stats'].get('avg_pace_min_km', 'N/A')
                
                # Use language-appropriate query
                if language == 'Chinese':
                    query = f"距离: {distance} 公里, 配速: {pace} 每公里"
                else:
                    query = f"Distance: {distance} km, Pace: {pace} per km"
                
                historical_runs = search_similar_runs(query, k=3)
            except Exception as search_error:
                # Silently fail - historical context is optional
                historical_runs = []
    
    # Historical context is used internally for AI analysis but not displayed to user
    
    # Get coaching advice
    with st.spinner(t('getting_advice')):
        coach_response = get_coach_advice(
            st.session_state.user_profile,
            st.session_state.goal,
            today_analysis,
            historical_runs,
            subjective_feeling
        )
    
    # Display immediate advice
    st.header(t('immediate_assessment'))
    immediate_advice = coach_response.get('immediate_advice', '')
    if immediate_advice and immediate_advice not in ['No advice available', '即时评估暂不可用', 'Immediate assessment not available']:
        st.info(immediate_advice)
    else:
        st.warning("即时评估暂不可用，请检查 API 连接或稍后重试" if language == 'Chinese' else "Immediate assessment not available, please check API connection or try again later")
    
    # Display training plan
    st.header(t('detailed_plan'))
    training_plan = coach_response.get('training_plan', '')
    if training_plan and training_plan not in ['训练计划暂不可用', 'Training plan not available', '训练计划解析失败', 'Failed to parse training plan']:
        st.markdown(training_plan)
    else:
        st.warning("训练计划暂不可用，请检查 API 连接或稍后重试" if language == 'Chinese' else "Training plan not available, please check API connection or try again later")
    
    # Display strategy
    st.header(t('training_strategy'))
    strategy = coach_response.get('strategy', '')
    if strategy and strategy not in ['训练策略暂不可用', 'Training strategy not available', '训练策略解析失败', 'Failed to parse strategy']:
        st.markdown(strategy)
    else:
        st.info("训练策略暂不可用，请检查 API 连接或稍后重试" if language == 'Chinese' else "Training strategy not available, please check API connection or try again later")
    
    # Export button - Excel format
    st.divider()
    st.subheader("📥 " + ("导出结果" if language == 'Chinese' else "Export Results"))
    
    # Generate Excel report
    try:
        from io import BytesIO
        
        # Create Excel file in memory
        buffer = BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Sheet 1: Key Metrics
            basic_stats = today_analysis.get('basic_stats', {})
            metrics_data = {
                ('Metric' if language == 'English' else '指标'): [
                    'Distance' if language == 'English' else '距离',
                    'Duration' if language == 'English' else '时长',
                    'Avg HR' if language == 'English' else '平均心率',
                    'Avg Pace' if language == 'English' else '平均配速'
                ],
                ('Value' if language == 'English' else '值'): [
                    f"{basic_stats.get('total_distance_km', 0):.2f} km",
                    f"{basic_stats.get('total_duration_minutes', 0):.2f} {'minutes' if language == 'English' else '分钟'}",
                    f"{basic_stats.get('avg_heart_rate', 'N/A')} bpm",
                    basic_stats.get('avg_pace', 'N/A')
                ]
            }
            metrics_df = pd.DataFrame(metrics_data)
            metrics_df.to_excel(writer, sheet_name='Key Metrics' if language == 'English' else '关键指标', index=False)
            
            # Sheet 2: Detailed Analysis
            detailed_data = []
            
            # Cardiac Drift
            drift_data = today_analysis.get('cardiac_drift', {})
            if drift_data.get('drift_percentage') is not None:
                detailed_data.append({
                    ('Category' if language == 'English' else '类别'): 'Cardiac Drift' if language == 'English' else '心率漂移',
                    ('Metric' if language == 'English' else '指标'): 'First Half Efficiency' if language == 'English' else '前半段效率',
                    ('Value' if language == 'English' else '值'): f"{drift_data.get('first_half_efficiency', 0):.4f}"
                })
                detailed_data.append({
                    ('Category' if language == 'English' else '类别'): 'Cardiac Drift' if language == 'English' else '心率漂移',
                    ('Metric' if language == 'English' else '指标'): 'Second Half Efficiency' if language == 'English' else '后半段效率',
                    ('Value' if language == 'English' else '值'): f"{drift_data.get('second_half_efficiency', 0):.4f}"
                })
                detailed_data.append({
                    ('Category' if language == 'English' else '类别'): 'Cardiac Drift' if language == 'English' else '心率漂移',
                    ('Metric' if language == 'English' else '指标'): 'Drift Percentage' if language == 'English' else '漂移百分比',
                    ('Value' if language == 'English' else '值'): f"{drift_data.get('drift_percentage', 0):.2f}%"
                })
            
            # Pacing Variance
            pacing_data = today_analysis.get('pacing_variance', {})
            detailed_data.append({
                ('Category' if language == 'English' else '类别'): 'Pacing' if language == 'English' else '配速',
                ('Metric' if language == 'English' else '指标'): 'Run Type' if language == 'English' else '跑步类型',
                ('Value' if language == 'English' else '值'): pacing_data.get('run_type', 'Unknown')
            })
            detailed_data.append({
                ('Category' if language == 'English' else '类别'): 'Pacing' if language == 'English' else '配速',
                ('Metric' if language == 'English' else '指标'): 'Speed Variation' if language == 'English' else '速度变化',
                ('Value' if language == 'English' else '值'): f"{pacing_data.get('coefficient_of_variation', 0):.3f}"
            })
            
            # Cadence
            cadence_data = today_analysis.get('cadence_metrics', {})
            if cadence_data.get('avg_cadence_spm') or cadence_data.get('avg_cadence'):
                avg_cadence = cadence_data.get('avg_cadence_spm') or cadence_data.get('avg_cadence')
                detailed_data.append({
                    ('Category' if language == 'English' else '类别'): 'Cadence' if language == 'English' else '步频',
                    ('Metric' if language == 'English' else '指标'): 'Average Cadence' if language == 'English' else '平均步频',
                    ('Value' if language == 'English' else '值'): f"{avg_cadence} spm"
                })
                detailed_data.append({
                    ('Category' if language == 'English' else '类别'): 'Cadence' if language == 'English' else '步频',
                    ('Metric' if language == 'English' else '指标'): 'Consistency' if language == 'English' else '一致性',
                    ('Value' if language == 'English' else '值'): cadence_data.get('cadence_consistency', 'Unknown')
                })
            
            # Vertical Oscillation
            vo_data = today_analysis.get('vertical_oscillation_metrics', {})
            if vo_data.get('avg_vertical_oscillation_cm') is not None:
                detailed_data.append({
                    ('Category' if language == 'English' else '类别'): 'Vertical Oscillation' if language == 'English' else '垂直振幅',
                    ('Metric' if language == 'English' else '指标'): 'Average' if language == 'English' else '平均值',
                    ('Value' if language == 'English' else '值'): f"{vo_data.get('avg_vertical_oscillation_cm')} cm"
                })
                if vo_data.get('max_vertical_oscillation_cm') is not None:
                    detailed_data.append({
                        ('Category' if language == 'English' else '类别'): 'Vertical Oscillation' if language == 'English' else '垂直振幅',
                        ('Metric' if language == 'English' else '指标'): 'Maximum' if language == 'English' else '最大值',
                        ('Value' if language == 'English' else '值'): f"{vo_data.get('max_vertical_oscillation_cm')} cm"
                    })
                if vo_data.get('assessment'):
                    detailed_data.append({
                        ('Category' if language == 'English' else '类别'): 'Vertical Oscillation' if language == 'English' else '垂直振幅',
                        ('Metric' if language == 'English' else '指标'): 'Assessment' if language == 'English' else '评估',
                        ('Value' if language == 'English' else '值'): vo_data.get('assessment', 'Unknown')
                    })
            
            if detailed_data:
                detailed_df = pd.DataFrame(detailed_data)
                detailed_df.to_excel(writer, sheet_name='Detailed Analysis' if language == 'English' else '详细分析', index=False)
            else:
                # Create empty sheet if no detailed data
                empty_df = pd.DataFrame({('Category' if language == 'English' else '类别'): [], ('Metric' if language == 'English' else '指标'): [], ('Value' if language == 'English' else '值'): []})
                empty_df.to_excel(writer, sheet_name='Detailed Analysis' if language == 'English' else '详细分析', index=False)
            
            # Sheet 3: Immediate Assessment & Next Workout
            immediate_advice = coach_response.get('immediate_advice', '')
            if immediate_advice:
                # Split content by newlines and create rows
                lines = immediate_advice.split('\n')
                immediate_df = pd.DataFrame({
                    ('Content' if language == 'English' else '内容'): [line.strip() for line in lines if line.strip()]
                })
            else:
                immediate_df = pd.DataFrame({
                    ('Content' if language == 'English' else '内容'): ['No data available' if language == 'English' else '暂无数据']
                })
            immediate_df.to_excel(writer, sheet_name='Immediate Assessment' if language == 'English' else '即时评估与下次训练', index=False)
            
            # Sheet 4: Detailed Training Plan
            training_plan = coach_response.get('training_plan', '')
            if training_plan:
                # Split content by newlines and create rows
                lines = training_plan.split('\n')
                training_plan_df = pd.DataFrame({
                    ('Content' if language == 'English' else '内容'): [line.strip() for line in lines if line.strip()]
                })
            else:
                training_plan_df = pd.DataFrame({
                    ('Content' if language == 'English' else '内容'): ['No data available' if language == 'English' else '暂无数据']
                })
            training_plan_df.to_excel(writer, sheet_name='Training Plan' if language == 'English' else '详细训练计划', index=False)
            
            # Sheet 5: Training Strategy & Rationale
            strategy = coach_response.get('strategy', '')
            if strategy:
                # Split content by newlines and create rows
                lines = strategy.split('\n')
                strategy_df = pd.DataFrame({
                    ('Content' if language == 'English' else '内容'): [line.strip() for line in lines if line.strip()]
                })
            else:
                strategy_df = pd.DataFrame({
                    ('Content' if language == 'English' else '内容'): ['No data available' if language == 'English' else '暂无数据']
                })
            strategy_df.to_excel(writer, sheet_name='Training Strategy' if language == 'English' else '训练策略与原理', index=False)
        
        excel_bytes = buffer.getvalue()
        buffer.close()
        
        st.download_button(
            label="📥 " + ("下载所有分析结果 (Excel)" if language == 'Chinese' else "Download All Results (Excel)"),
            data=excel_bytes,
            file_name=f"running_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    except ImportError:
        st.error("Excel export requires openpyxl library." if language == 'English' else "Excel导出需要openpyxl库。")
        st.info("Please run: `pip install openpyxl` in your terminal, then restart the app." if language == 'English' else "请在终端运行: `pip install openpyxl`，然后重启应用。")
    except Exception as e:
        st.error(f"Error generating Excel: {e}" if language == 'English' else f"生成Excel时出错: {e}")
        import traceback
        st.error(traceback.format_exc())
    
    # Additional metrics - use translated labels
    with st.expander(t('detailed_analysis')):
        st.subheader(t('cardiac_drift_details'))
        drift_data = today_analysis.get('cardiac_drift', {})
        if drift_data.get('drift_percentage') is not None:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**{t('first_half_efficiency')}:** {drift_data.get('first_half_efficiency', 0):.4f}")
                st.write(f"**{t('first_half_avg_hr')}:** {drift_data.get('first_half_avg_hr', 0):.1f} bpm")
            with col2:
                st.write(f"**{t('second_half_efficiency')}:** {drift_data.get('second_half_efficiency', 0):.4f}")
                st.write(f"**{t('second_half_avg_hr')}:** {drift_data.get('second_half_avg_hr', 0):.1f} bpm")
        
        st.subheader(t('pacing_analysis'))
        pacing_data = today_analysis.get('pacing_variance', {})
        st.write(f"**{t('run_type')}:** {pacing_data.get('run_type', 'Unknown')}")
        st.write(f"**{t('speed_variation')}:** {pacing_data.get('coefficient_of_variation', 0):.3f}")
        
        st.subheader(t('cadence_metrics'))
        cadence_data = today_analysis.get('cadence_metrics', {})
        if cadence_data.get('avg_cadence_spm') or cadence_data.get('avg_cadence'):
            avg_cadence = cadence_data.get('avg_cadence_spm') or cadence_data.get('avg_cadence')
            st.write(f"**{t('avg_cadence')}:** {avg_cadence} spm")
            st.write(f"**{t('consistency')}:** {cadence_data.get('cadence_consistency', 'Unknown')}")
        
        st.subheader(t('vertical_oscillation'))
        vo_data = today_analysis.get('vertical_oscillation_metrics', {})
        if vo_data.get('avg_vertical_oscillation_cm') is not None:
            st.write(f"**{t('average')}:** {vo_data.get('avg_vertical_oscillation_cm')} cm")
            if vo_data.get('max_vertical_oscillation_cm') is not None:
                st.write(f"**最大垂直振幅:** {vo_data.get('max_vertical_oscillation_cm')} cm" if language == 'Chinese' else f"**Max:** {vo_data.get('max_vertical_oscillation_cm')} cm")
            if vo_data.get('assessment'):
                st.write(f"**{t('assessment')}:** {vo_data.get('assessment', 'Unknown')}")
        else:
            st.info("无垂直振幅数据" if language == 'Chinese' else "No vertical oscillation data available")
