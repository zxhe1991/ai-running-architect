"""
Streamlit 音频录音组件
使用浏览器 Web Audio API 实现实时录音
"""
import streamlit.components.v1 as components
import base64
import os

def audio_recorder(key=None, pause_threshold=2.0, sample_rate=16000):
    """
    创建一个音频录音组件
    
    Args:
        key: 组件的唯一键
        pause_threshold: 暂停阈值（秒）
        sample_rate: 采样率
    
    Returns:
        录音的音频数据（base64编码的WAV格式）
    """
    
    # HTML/JavaScript 代码用于录音
    recorder_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            .recorder-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 15px;
                padding: 20px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                background: #f9f9f9;
            }
            .record-button {
                padding: 15px 30px;
                font-size: 18px;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                transition: all 0.3s;
                font-weight: bold;
            }
            .record-button.recording {
                background: #ff4444;
                color: white;
                animation: pulse 1.5s infinite;
            }
            .record-button.idle {
                background: #4CAF50;
                color: white;
            }
            .record-button.idle:hover {
                background: #45a049;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
            .status {
                font-size: 16px;
                color: #666;
                min-height: 24px;
            }
            .timer {
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }
        </style>
    </head>
    <body>
        <div class="recorder-container">
            <button id="recordBtn" class="record-button idle">🎤 开始录音</button>
            <div class="status" id="status">点击按钮开始录音</div>
            <div class="timer" id="timer" style="display:none;">00:00</div>
            <audio id="audioPlayback" controls style="display:none; width: 100%;"></audio>
        </div>
        
        <script>
            let mediaRecorder;
            let audioChunks = [];
            let isRecording = false;
            let startTime;
            let timerInterval;
            
            const recordBtn = document.getElementById('recordBtn');
            const status = document.getElementById('status');
            const timer = document.getElementById('timer');
            const audioPlayback = document.getElementById('audioPlayback');
            
            // 格式化时间
            function formatTime(seconds) {
                const mins = Math.floor(seconds / 60);
                const secs = Math.floor(seconds % 60);
                return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            }
            
            // 更新计时器
            function updateTimer() {
                if (isRecording && startTime) {
                    const elapsed = Math.floor((Date.now() - startTime) / 1000);
                    timer.textContent = formatTime(elapsed);
                }
            }
            
            async function startRecording() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    
                    mediaRecorder = new MediaRecorder(stream, {
                        mimeType: 'audio/webm;codecs=opus'
                    });
                    
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = (event) => {
                        if (event.data.size > 0) {
                            audioChunks.push(event.data);
                        }
                    };
                    
                    mediaRecorder.onstop = () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                        const reader = new FileReader();
                        
                        reader.onloadend = () => {
                            const base64Audio = reader.result.split(',')[1];
                            
                            // 发送到 Streamlit
                            window.parent.postMessage({
                                type: 'streamlit:setComponentValue',
                                value: base64Audio
                            }, '*');
                            
                            // 显示音频播放器
                            const audioUrl = URL.createObjectURL(audioBlob);
                            audioPlayback.src = audioUrl;
                            audioPlayback.style.display = 'block';
                            
                            status.textContent = '录音完成！可以播放预览或重新录音';
                        };
                        
                        reader.readAsDataURL(audioBlob);
                        stream.getTracks().forEach(track => track.stop());
                    };
                    
                    mediaRecorder.start();
                    isRecording = true;
                    startTime = Date.now();
                    
                    recordBtn.textContent = '⏹️ 停止录音';
                    recordBtn.className = 'record-button recording';
                    status.textContent = '正在录音...';
                    timer.style.display = 'block';
                    
                    timerInterval = setInterval(updateTimer, 1000);
                    
                } catch (error) {
                    console.error('Error accessing microphone:', error);
                    status.textContent = '错误: 无法访问麦克风。请检查浏览器权限。';
                    alert('无法访问麦克风。请确保已授予麦克风权限。');
                }
            }
            
            function stopRecording() {
                if (mediaRecorder && isRecording) {
                    mediaRecorder.stop();
                    isRecording = false;
                    clearInterval(timerInterval);
                    
                    recordBtn.textContent = '🎤 重新录音';
                    recordBtn.className = 'record-button idle';
                    timer.style.display = 'none';
                }
            }
            
            recordBtn.addEventListener('click', () => {
                if (!isRecording) {
                    startRecording();
                } else {
                    stopRecording();
                }
            });
        </script>
    </body>
    </html>
    """
    
    # 创建组件
    audio_data = components.html(
        recorder_html,
        height=300,
        key=key
    )
    
    return audio_data
