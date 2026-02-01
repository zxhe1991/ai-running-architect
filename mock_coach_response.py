"""
模拟教练响应 - 临时解决方案
当 API 修复后，可以切换回真实 API
"""
import json
from typing import Dict, Any

def get_mock_coach_advice(
    user_profile: Dict[str, Any],
    goal: Dict[str, Any],
    today_analysis: Dict[str, Any],
    historical_runs: list = [],
    subjective_feeling: str = "",
    language: str = "Chinese",
    historical_running_info: str = ""
) -> Dict[str, str]:
    """
    生成模拟的教练建议
    
    这是一个临时解决方案，用于在 API 修复之前测试应用功能。
    """
    
    age = user_profile.get('age', 30)
    gender = user_profile.get('gender', 'Unknown')
    target_pace = goal.get('target_pace', '5:00')
    target_date = goal.get('target_date', 'In 3 months')
    weekly_hours = goal.get('weekly_hours', 5.0)
    
    basic_stats = today_analysis.get('basic_stats', {})
    distance = basic_stats.get('total_distance_km', 0)
    avg_hr = basic_stats.get('avg_heart_rate', 0)
    avg_pace = basic_stats.get('avg_pace') or basic_stats.get('avg_pace_min_km', 'N/A')
    drift_pct = today_analysis.get('cardiac_drift', {}).get('drift_percentage', 0)
    
    if language == 'Chinese':
        immediate_advice = f"""**即时评估：**

根据您今天的跑步数据分析：
- 距离：{distance:.1f} 公里
- 平均心率：{avg_hr:.0f} bpm
- 平均配速：{avg_pace}

您的表现{'良好' if drift_pct > -5 else '需要改进'}。心脏漂移为 {drift_pct:.1f}%，{'表明您保持了良好的效率' if drift_pct > -5 else '表明后半程效率下降，可能需要注意恢复'}。

**下次训练建议：**
- **时间**：明天或后天（根据您的恢复情况）
- **类型**：轻松恢复跑
- **距离**：5-8 公里
- **配速**：比目标配速慢 30-60 秒/公里
- **心率区间**：最大心率的 60-70%
- **主观感受**：{subjective_feeling if subjective_feeling else '未提供'}

{'建议休息 1 天后再进行下一次训练。' if drift_pct < -10 else '可以继续进行训练，但要注意恢复。'}"""

        training_plan = f"""**详细训练计划（{target_date}）**

**目标：** 在 {target_date} 前达到 {target_pace} min/km 的配速
**每周可用时间：** {weekly_hours} 小时

**第1-2周：基础建立**
- 周一：轻松跑 6-8 km，配速 {target_pace} + 30-45秒
- 周三：节奏跑 5 km，配速 {target_pace} + 10-15秒
- 周五：轻松跑 5-6 km
- 周日：长距离跑 10-12 km，配速 {target_pace} + 30-45秒

**第3-4周：强度提升**
- 周一：轻松跑 8-10 km
- 周三：间歇跑 6x800m，配速 {target_pace} - 10秒，恢复 2分钟慢跑
- 周五：轻松跑 6 km
- 周日：长距离跑 12-15 km

**第5-6周：目标配速训练**
- 周一：轻松跑 8 km
- 周三：节奏跑 6-8 km，目标配速 {target_pace}
- 周五：轻松跑 5 km
- 周日：长距离跑 15 km，配速 {target_pace} + 15-20秒

**第7-8周：巩固和测试**
- 周一：轻松跑 6 km
- 周三：目标配速测试 5 km
- 周五：轻松跑 5 km
- 周日：长距离跑 12 km

**恢复周（每4周一次）：**
- 减少训练量 30-40%
- 专注于轻松跑和恢复"""

        strategy = f"""**训练策略和原理：**

**1. 渐进式训练原则**
- 每周增加训练量不超过 10%
- 强度训练和轻松跑的比例为 20:80
- 每4周安排一个恢复周

**2. 关键里程碑**
- **第2周末**：能够以目标配速 + 15秒完成 5 km
- **第4周末**：能够以目标配速完成 3 km
- **第6周末**：能够以目标配速完成 5 km
- **第8周末**：达到目标配速

**3. 过度训练警告信号**
- 静息心率持续升高（+5 bpm以上）
- 训练后恢复时间延长
- 主观感受持续不佳
- 配速无法达到预期

**4. 调整策略**
- 如果落后进度：增加1次轻松跑，但不要增加强度
- 如果提前完成：可以提前测试目标配速，但保持谨慎
- 如果出现过度训练信号：立即减少训练量 50%，增加恢复时间

**5. 个性化建议**
- 您的年龄：{age} 岁，建议最大心率约为 {220 - age} bpm
- 每周 {weekly_hours} 小时的训练时间{'充足' if weekly_hours >= 5 else '需要合理安排'}
- 建议在训练中加入力量训练（每周1-2次）以预防受伤"""
    else:
        immediate_advice = f"""**Immediate Assessment:**

Based on today's run analysis:
- Distance: {distance:.1f} km
- Average Heart Rate: {avg_hr:.0f} bpm
- Average Pace: {avg_pace}

Your performance is {'good' if drift_pct > -5 else 'needs improvement'}. Cardiac drift is {drift_pct:.1f}%, {'indicating good efficiency maintenance' if drift_pct > -5 else 'indicating efficiency drop in second half, may need recovery'}.

**Next Workout Recommendation:**
- **When**: Tomorrow or day after (based on recovery)
- **Type**: Easy recovery run
- **Distance**: 5-8 km
- **Pace**: 30-60 seconds slower than target pace per km
- **Heart Rate Zone**: 60-70% of max HR
- **Subjective Feeling**: {subjective_feeling if subjective_feeling else 'Not provided'}

{'Recommend resting 1 day before next workout.' if drift_pct < -10 else 'Can continue training but pay attention to recovery.'}"""

        training_plan = f"""**Detailed Training Plan ({target_date})**

**Goal:** Achieve {target_pace} min/km pace by {target_date}
**Weekly Available Time:** {weekly_hours} hours

**Weeks 1-2: Base Building**
- Monday: Easy run 6-8 km, pace {target_pace} + 30-45s
- Wednesday: Tempo run 5 km, pace {target_pace} + 10-15s
- Friday: Easy run 5-6 km
- Sunday: Long run 10-12 km, pace {target_pace} + 30-45s

**Weeks 3-4: Intensity Increase**
- Monday: Easy run 8-10 km
- Wednesday: Intervals 6x800m, pace {target_pace} - 10s, 2min recovery
- Friday: Easy run 6 km
- Sunday: Long run 12-15 km

**Weeks 5-6: Target Pace Training**
- Monday: Easy run 8 km
- Wednesday: Tempo run 6-8 km at target pace {target_pace}
- Friday: Easy run 5 km
- Sunday: Long run 15 km, pace {target_pace} + 15-20s

**Weeks 7-8: Consolidation and Testing**
- Monday: Easy run 6 km
- Wednesday: Target pace test 5 km
- Friday: Easy run 5 km
- Sunday: Long run 12 km

**Recovery Week (every 4 weeks):**
- Reduce training volume by 30-40%
- Focus on easy runs and recovery"""

        strategy = f"""**Training Strategy and Rationale:**

**1. Progressive Training Principle**
- Increase training volume by no more than 10% per week
- Intensity to easy run ratio: 20:80
- Recovery week every 4 weeks

**2. Key Milestones**
- **End of Week 2**: Able to complete 5 km at target pace + 15s
- **End of Week 4**: Able to complete 3 km at target pace
- **End of Week 6**: Able to complete 5 km at target pace
- **End of Week 8**: Achieve target pace

**3. Overtraining Warning Signs**
- Resting heart rate consistently elevated (+5 bpm)
- Prolonged recovery time after workouts
- Consistently poor subjective feeling
- Unable to achieve expected pace

**4. Adjustment Strategy**
- If behind schedule: Add 1 easy run, but don't increase intensity
- If ahead of schedule: Can test target pace earlier, but remain cautious
- If overtraining signs appear: Immediately reduce training volume by 50%, increase recovery time

**5. Personalized Recommendations**
- Your age: {age} years, estimated max HR: {220 - age} bpm
- {weekly_hours} hours per week is {'sufficient' if weekly_hours >= 5 else 'needs careful planning'}
- Recommend adding strength training (1-2 times per week) to prevent injuries"""
    
    return {
        'immediate_advice': immediate_advice,
        'training_plan': training_plan,
        'strategy': strategy
    }
