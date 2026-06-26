@echo off
echo ========================================
echo   波动光学仿真平台启动脚本
echo ========================================
echo.

echo 正在检查依赖项...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo 发现缺少依赖，正在安装...
    pip install -r requirements.txt
)

echo.
echo 启动波动光学仿真平台...
echo 请在浏览器中打开 http://localhost:8501
echo 按 Ctrl+C 可以停止服务器
echo.

streamlit run wave_optics_simulation.py --server.port 8501