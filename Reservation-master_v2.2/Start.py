# Start.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import os
import importlib
import shutil

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.config import Config
import datetime

# 延迟导入依赖项，以便GUI可以启动
setup_config = None
Booking = None
start_scheduler = None
stop_scheduler = None
_last_dependency_error = ""

def load_dependencies():
    global _last_dependency_error
    global setup_config, Booking, start_scheduler, stop_scheduler
    try:
        from backend.config_setup import setup_config
        from backend.book import Booking
        from backend.scheduler import start_scheduler, stop_scheduler
        _last_dependency_error = ""
        return True
    except ImportError as e:
        _last_dependency_error = str(e)
        return False

class BookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🏸 南京医科大学场馆预约系统 v2")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)

        # UI 设计令牌
        self.ui = {
            'bg': '#f4f7fb',
            'surface': '#ffffff',
            'text': '#1f2d3d',
            'muted_text': '#5b6b7a',
            'primary': '#2f80ed',
            'primary_hover': '#2a74d8',
            'success': '#1f9d6a',
            'warning': '#d9822b',
            'error': '#c0392b',
            'border': '#dbe4ee',
            'title_font': ('Microsoft YaHei UI', 20, 'bold'),
            'subtitle_font': ('Microsoft YaHei UI', 14),
            'normal_font': ('Microsoft YaHei UI', 11),
            'action_font': ('Microsoft YaHei UI', 11, 'bold'),
        }

        self.root.configure(bg=self.ui['bg'])

        # 可视化时间段选项
        self.available_time_slots = [
            '08:01-09:00',
            '09:01-10:00',
            '10:01-11:00',
            '11:01-12:00',
            '12:01-13:00',
            '13:01-14:00',
            '14:01-15:00',
            '15:01-16:00',
            '16:01-17:00',
            '17:01-18:00',
            '18:01-19:00',
            '19:01-20:00',
            '20:01-21:00',
            '21:01-22:00',
        ]
        
        # 设置主题和样式
        self.style = ttk.Style()
        
        # 尝试使用现代主题
        try:
            self.style.theme_use('vista')
        except:
            try:
                self.style.theme_use('clam')
            except:
                pass
        
        # 自定义样式
        self.style.configure('App.TFrame', background=self.ui['bg'])
        self.style.configure('Card.TFrame', background=self.ui['surface'])
        self.style.configure('Card.TLabelframe', background=self.ui['surface'], bordercolor=self.ui['border'])
        self.style.configure('Card.TLabelframe.Label', background=self.ui['surface'], foreground=self.ui['primary'], font=('Microsoft YaHei UI', 11, 'bold'))

        self.style.configure('Title.TLabel', font=self.ui['title_font'], foreground=self.ui['text'], background=self.ui['bg'])
        self.style.configure('Subtitle.TLabel', font=self.ui['subtitle_font'], foreground=self.ui['muted_text'], background=self.ui['surface'])
        self.style.configure('Section.TLabel', font=('Microsoft YaHei UI', 12, 'bold'), foreground=self.ui['primary'], background=self.ui['surface'])
        self.style.configure('Normal.TLabel', font=self.ui['normal_font'], foreground=self.ui['text'], background=self.ui['surface'])
        self.style.configure('Muted.TLabel', font=self.ui['normal_font'], foreground=self.ui['muted_text'], background=self.ui['surface'])
        self.style.configure('Success.TLabel', font=self.ui['normal_font'], foreground=self.ui['success'], background=self.ui['surface'])
        self.style.configure('Warning.TLabel', font=self.ui['normal_font'], foreground=self.ui['warning'], background=self.ui['surface'])
        self.style.configure('Error.TLabel', font=self.ui['normal_font'], foreground=self.ui['error'], background=self.ui['surface'])
        # 移除旧的Action.TButton样式定义
        self.style.configure('Normal.TButton', font=('Microsoft YaHei UI', 10), padding=5)
        
        # 设置按钮样式 - 使用更直接的方式
        self.style.configure('TButton', font=('Microsoft YaHei UI', 10))
        
        # 创建新的按钮样式，确保背景和前景色对比明显
        # 使用更简单的样式定义，确保在所有主题下都能正确显示
        self.style.configure('CustomAction.TButton', font=self.ui['action_font'], padding=10)
        
        # 为不同状态设置样式
        self.style.map('CustomAction.TButton',
                  background=[('!disabled', self.ui['primary']), ('pressed', self.ui['primary_hover']), ('active', self.ui['primary_hover'])],
                  foreground=[('!disabled', 'white'), ('pressed', 'white'), ('active', 'white')])

        self.style.configure('TNotebook', background=self.ui['bg'], borderwidth=0)
        self.style.configure('TNotebook.Tab', padding=(18, 10), font=('Microsoft YaHei UI', 10, 'bold'))
        self.style.map('TNotebook.Tab',
                  background=[('selected', self.ui['surface']), ('!selected', '#eaf0f7')],
                  foreground=[('selected', self.ui['primary']), ('!selected', self.ui['muted_text'])])
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="16", style='App.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(self.main_frame, text="🏸 南京医科大学场馆预约系统", style='Title.TLabel')
        title_label.pack(pady=(0, 6))

        top_meta = ttk.Frame(self.main_frame, style='App.TFrame')
        top_meta.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(top_meta, text="智能预约助手 | v2", style='Muted.TLabel').pack(side=tk.LEFT)
        self.clock_var = tk.StringVar(value="")
        ttk.Label(top_meta, textvariable=self.clock_var, style='Muted.TLabel').pack(side=tk.RIGHT)
        self._tick_clock()
        
        # 创建标签页
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 欢迎页
        self.welcome_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.welcome_tab, text="🏠 首页")
        
        # 配置页
        self.config_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.config_tab, text="⚙️ 配置")
        
        # 操作页
        self.operation_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.operation_tab, text="🎯 操作")
        
        # 日志页
        self.log_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.log_tab, text="📋 日志")
        
        # 存储滚动区域
        self.canvases = {}
        
        # 初始化页面
        self.init_welcome_tab()
        self.init_config_tab()
        self.init_operation_tab()
        self.init_log_tab()

        # 绑定鼠标滚轮事件到主窗口
        self.root.bind("<MouseWheel>", self._on_mouse_wheel)
        
        # 调度器线程
        self.scheduler_thread = None
        self.scheduler_running = False
        
        # 当前状态
        self.current_status = "就绪"
        self.last_booking_time = None
        self.booking_count = 0
    
    def _on_mouse_wheel(self, event):
        """处理鼠标滚轮事件"""
        # 找到当前活动标签页的索引
        try:
            current_tab_index = self.notebook.index(self.notebook.select())
        except:
            return
        
        # 根据当前标签页索引获取对应的canvas
        if current_tab_index == 0:  # 首页
            canvas = self.canvases.get('welcome')
        elif current_tab_index == 1:  # 配置
            canvas = self.canvases.get('config')
        elif current_tab_index == 2:  # 操作
            canvas = self.canvases.get('operation')
        else:
            # 日志页使用的是scrolledtext，不需要处理
            return
        
        if canvas:
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _create_scrollable_tab(self, tab_widget, tab_key):
        """创建可滚动标签页，并返回内部可布局 frame。"""
        canvas = tk.Canvas(tab_widget, bg=self.ui['bg'], highlightthickness=0, borderwidth=0)
        scrollbar = ttk.Scrollbar(tab_widget, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='App.TFrame')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        self.canvases[tab_key] = canvas

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return scrollable_frame
    
    def init_welcome_tab(self):
        """初始化欢迎页"""
        scrollable_frame = self._create_scrollable_tab(self.welcome_tab, 'welcome')
        
        # 欢迎信息
        welcome_frame = ttk.LabelFrame(scrollable_frame, text="👋 欢迎使用", padding="20", style='Card.TLabelframe')
        welcome_frame.pack(fill=tk.X, padx=20, pady=15)
        
        ttk.Label(welcome_frame, text="欢迎使用南京医科大学场馆预约系统！", style='Subtitle.TLabel').pack(pady=8)
        ttk.Label(welcome_frame, text="本系统专为医学生设计，无需编程知识即可自动预约场馆。", style='Normal.TLabel').pack(pady=5)
        
        # 系统信息
        info_frame = ttk.LabelFrame(scrollable_frame, text="ℹ️ 系统信息", padding="20", style='Card.TLabelframe')
        info_frame.pack(fill=tk.X, padx=20, pady=15)
        
        info_text = """
当前版本：v2
适用场馆：羽毛球馆（serviceid=22）

自动预约时间：每天 08:00 自动尝试预约
放号窗口：08:00 - 08:30（30 分钟）
        """
        info_label = ttk.Label(info_frame, text=info_text, style='Normal.TLabel', justify=tk.LEFT)
        info_label.pack(pady=8)
        
        # 快速开始指南
        guide_frame = ttk.LabelFrame(scrollable_frame, text="📖 快速开始指南", padding="20", style='Card.TLabelframe')
        guide_frame.pack(fill=tk.X, padx=20, pady=15)
        
        steps = [
            "1️⃣ 首次使用，请先在【配置】页面设置账号密码和偏好",
            "2️⃣ 点击【保存配置】按钮保存设置",
            "3️⃣ 在【操作】页面点击【预拉取场地】测试配置",
            "4️⃣ 点击【启动自动预约】开始自动预约",
            "5️⃣ 在【日志】页面查看预约结果和系统状态"
        ]
        
        steps_frame = ttk.Frame(guide_frame)
        steps_frame.pack(fill=tk.X)
        
        for step in steps:
            ttk.Label(steps_frame, text=step, style='Normal.TLabel').pack(pady=4, anchor=tk.W)
        
        # 使用说明
        help_frame = ttk.LabelFrame(scrollable_frame, text="❓ 使用说明", padding="20", style='Card.TLabelframe')
        help_frame.pack(fill=tk.X, padx=20, pady=15)
        
        help_sections = [
            ("🔑 账号配置", "填写你的学号和密码，以及实际入场人的学号（可以多人，用/分隔）"),
            ("📅 日期优先级", "设置优先尝试的日期，如'tomorrow,today'表示优先明天，其次今天"),
            ("⏰ 时间段偏好", "设置偏好的时间段，系统会按顺序尝试。可以为每周的每一天设置不同的偏好"),
            ("🎯 预拉取场地", "测试配置是否正确，会尝试获取可用的场地信息"),
            ("⚡ 立即预约", "立即尝试预约一次，适合手动抢场"),
            ("🔄 自动预约", "启动后系统会在每天 08:00 自动尝试预约，无需人工干预")
        ]
        
        help_content = ttk.Frame(help_frame)
        help_content.pack(fill=tk.X)
        
        for title, content in help_sections:
            ttk.Label(help_content, text=title, style='Section.TLabel').pack(pady=(12, 6), anchor=tk.W)
            ttk.Label(help_content, text=content, style='Normal.TLabel').pack(pady=4, anchor=tk.W)
        
        # 常见问题
        faq_frame = ttk.LabelFrame(scrollable_frame, text="❗ 常见问题", padding="20", style='Card.TLabelframe')
        faq_frame.pack(fill=tk.X, padx=20, pady=15)
        
        faqs = [
            ("Q: 登录失败？", "A: 检查账号密码是否正确，确认学校系统可访问"),
            ("Q: 一直提示未到预订时间？", "A: 学校尚未放号，系统会在 08:00 自动尝试"),
            ("Q: 提示每日限预约一场？", "A: 账号当日已有预约，需更换账号或次日再试"),
            ("Q: 场地列表为空？", "A: 可能已被抢空或学校尚未放号，检查配置是否正确")
        ]
        
        faq_content = ttk.Frame(faq_frame)
        faq_content.pack(fill=tk.X)
        
        for question, answer in faqs:
            ttk.Label(faq_content, text=question, style='Section.TLabel').pack(pady=(12, 4), anchor=tk.W)
            ttk.Label(faq_content, text=answer, style='Normal.TLabel').pack(pady=4, anchor=tk.W)
        
        # 状态显示
        status_frame = ttk.LabelFrame(scrollable_frame, text="📊 当前状态", padding="20", style='Card.TLabelframe')
        status_frame.pack(fill=tk.X, padx=20, pady=15)
        
        self.welcome_status_var = tk.StringVar(value="系统就绪，可以开始使用")
        status_label = ttk.Label(status_frame, textvariable=self.welcome_status_var, style='Success.TLabel', font=('Microsoft YaHei UI', 12, 'bold'))
        status_label.pack(pady=8)
        
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ttk.Label(status_frame, text=f"当前时间：{current_time}", style='Normal.TLabel').pack(pady=4)
    
    def init_config_tab(self):
        """初始化配置页"""
        scrollable_frame = self._create_scrollable_tab(self.config_tab, 'config')
        self._build_account_config_section(scrollable_frame)
        self._build_time_preference_section(scrollable_frame)
        self._build_weekly_time_preference_section(scrollable_frame)
        self._build_config_save_section(scrollable_frame)

    def _build_account_config_section(self, parent):
        """构建账号与基础配置区域。"""
        config_frame = ttk.LabelFrame(parent, text="🔑 账号配置", padding="20", style='Card.TLabelframe')
        config_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # 创建表单框架
        form_frame = ttk.Frame(config_frame)
        form_frame.pack(fill=tk.X, padx=10)
        
        # 学号
        ttk.Label(form_frame, text="学号:", style='Normal.TLabel').grid(row=0, column=0, sticky=tk.W, padx=10, pady=8)
        self.username_var = tk.StringVar(value=Config.LOGIN_DATA['dlm'])
        ttk.Entry(form_frame, textvariable=self.username_var, width=35).grid(row=0, column=1, sticky=tk.W, padx=10, pady=8)
        ttk.Label(form_frame, text="（登录系统的账号，只需填一个）", style='Normal.TLabel').grid(row=0, column=2, sticky=tk.W, padx=10, pady=8)
        
        # 密码
        ttk.Label(form_frame, text="密码:", style='Normal.TLabel').grid(row=1, column=0, sticky=tk.W, padx=10, pady=8)
        self.password_var = tk.StringVar(value=Config.LOGIN_DATA['mm'])
        ttk.Entry(form_frame, textvariable=self.password_var, show="*", width=35).grid(row=1, column=1, sticky=tk.W, padx=10, pady=8)
        ttk.Label(form_frame, text="（登录系统的密码）", style='Normal.TLabel').grid(row=1, column=2, sticky=tk.W, padx=10, pady=8)
        
        # 默认使用者
        ttk.Label(form_frame, text="默认使用者:", style='Normal.TLabel').grid(row=2, column=0, sticky=tk.W, padx=10, pady=8)
        self.users_var = tk.StringVar(value=Config.DEFAULT_USERS)
        ttk.Entry(form_frame, textvariable=self.users_var, width=35).grid(row=2, column=1, sticky=tk.W, padx=10, pady=8)
        ttk.Label(form_frame, text="（实际入场学号，多个用/分隔，包括主预约人和随行人员）", style='Normal.TLabel').grid(row=2, column=2, sticky=tk.W, padx=10, pady=8)
        
        # 场馆类型
        ttk.Label(form_frame, text="场馆类型:", style='Normal.TLabel').grid(row=3, column=0, sticky=tk.W, padx=10, pady=8)
        self.service_var = tk.StringVar(value=Config.SERVICE_ID)
        ttk.Entry(form_frame, textvariable=self.service_var, width=15).grid(row=3, column=1, sticky=tk.W, padx=10, pady=8)
        ttk.Label(form_frame, text="（羽毛球馆：22）", style='Normal.TLabel').grid(row=3, column=2, sticky=tk.W, padx=10, pady=8)
        
        # 日期优先级
        ttk.Label(form_frame, text="日期优先级:", style='Normal.TLabel').grid(row=4, column=0, sticky=tk.W, padx=10, pady=8)
        self.date_priority_var = tk.StringVar(value=",".join(Config.PRIORITIZE_DATES))
        ttk.Entry(form_frame, textvariable=self.date_priority_var, width=35).grid(row=4, column=1, sticky=tk.W, padx=10, pady=8)
        ttk.Label(form_frame, text="（如：tomorrow,today）", style='Normal.TLabel').grid(row=4, column=2, sticky=tk.W, padx=10, pady=8)

    def _build_time_preference_section(self, parent):
        """构建全局时间段偏好区域。"""
        slots_frame = ttk.LabelFrame(parent, text="⏰ 时间段偏好设置", padding="20", style='Card.TLabelframe')
        slots_frame.pack(fill=tk.X, padx=20, pady=15)

        ttk.Label(slots_frame, text="全局时间段偏好（默认设置，当某天没有单独设置时使用）:", style='Section.TLabel').pack(pady=8, anchor=tk.W)
        ttk.Label(slots_frame, text="时间段按从早到晚显示；勾选后会显示 1/2/3... 序号，保存按序号优先级尝试。", style='Muted.TLabel').pack(pady=(0, 8), anchor=tk.W)

        self.global_time_slot_vars = self._build_time_slot_selector(
            slots_frame,
            selected_slots=Config.PREFERRED_TIME_SLOTS,
            columns=4,
        )

        ttk.Label(slots_frame, text="⚠️ 系统预约速度非常快，时间段写在前面的优先约到", style='Warning.TLabel').pack(pady=4)

    def _build_weekly_time_preference_section(self, parent):
        """构建按星期几的时间偏好区域。"""
        week_frame = ttk.LabelFrame(parent, text="📅 按星期几的时间段偏好", padding="20", style='Card.TLabelframe')
        week_frame.pack(fill=tk.X, padx=20, pady=15)
        
        ttk.Label(week_frame, text="为每周每天设置不同偏好（留空则使用全局设置，序号越小优先级越高）:", style='Section.TLabel').pack(pady=8)
        
        # 星期几列表
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        weekday_names = {"monday": "周一", "tuesday": "周二", "wednesday": "周三", "thursday": "周四", "friday": "周五", "saturday": "周六", "sunday": "周日"}
        
        # 存储每个星期几的时间偏好
        self.weekly_time_slot_vars = {}
        
        for i, weekday in enumerate(weekdays):
            frame = ttk.Frame(week_frame)
            frame.pack(fill=tk.X, pady=4, padx=10)
            
            ttk.Label(frame, text=weekday_names[weekday], style='Normal.TLabel', width=8).pack(side=tk.LEFT, padx=10)
            
            slot_panel = ttk.Frame(frame, style='Card.TFrame')
            slot_panel.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

            slots = Config.WEEKLY_PREFERRED_TIME_SLOTS.get(weekday, [])
            self.weekly_time_slot_vars[weekday] = self._build_time_slot_selector(
                slot_panel,
                selected_slots=slots,
                columns=4,
                compact=True,
            )

    def _build_config_save_section(self, parent):
        """构建配置保存操作区。"""
        save_frame = ttk.Frame(parent)
        save_frame.pack(pady=25)

        save_button = self._create_primary_button(save_frame, "💾 保存配置", self.save_config)
        save_button.pack(side=tk.LEFT, padx=15)
        
        # 提示信息
        ttk.Label(save_frame, text="保存后配置会写入 config.py 文件", style='Normal.TLabel').pack(side=tk.LEFT, padx=15)
    
    def init_operation_tab(self):
        """初始化操作页"""
        scrollable_frame = self._create_scrollable_tab(self.operation_tab, 'operation')
        self._build_operation_status_section(scrollable_frame)
        self._build_operation_action_section(scrollable_frame)
        self._build_operation_auto_section(scrollable_frame)
        self._build_operation_stats_section(scrollable_frame)

    def _build_operation_status_section(self, parent):
        """构建操作页状态展示区域。"""
        status_frame = ttk.LabelFrame(parent, text="📊 系统状态", padding="20", style='Card.TLabelframe')
        status_frame.pack(fill=tk.X, padx=20, pady=15)
        
        self.status_var = tk.StringVar(value="✅ 系统就绪")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, style='Success.TLabel', font=('Microsoft YaHei UI', 16, 'bold'))
        status_label.pack(pady=12)
        
        # 详细信息
        self.detail_status_var = tk.StringVar(value="等待操作...")
        detail_label = ttk.Label(status_frame, textvariable=self.detail_status_var, style='Normal.TLabel', font=('Microsoft YaHei UI', 11))
        detail_label.pack(pady=6)

    def _build_operation_action_section(self, parent):
        """构建预拉取与立即预约操作区。"""
        action_frame = ttk.LabelFrame(parent, text="🎯 操作面板", padding="20", style='Card.TLabelframe')
        action_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # 预拉取场地
        fetch_frame = ttk.Frame(action_frame)
        fetch_frame.pack(fill=tk.X, pady=12)
        
        fetch_button = self._create_primary_button(fetch_frame, "📍 预拉取场地", self.fetch_venues)
        fetch_button.pack(side=tk.LEFT, padx=15)
        
        ttk.Label(fetch_frame, text="测试配置，获取可用场地信息", style='Normal.TLabel').pack(side=tk.LEFT, padx=15, fill=tk.Y, expand=True)
        
        # 立即预约
        book_frame = ttk.Frame(action_frame)
        book_frame.pack(fill=tk.X, pady=12)
        
        book_button = self._create_primary_button(book_frame, "⚡ 立即预约", self.manual_book)
        book_button.pack(side=tk.LEFT, padx=15)
        
        book_info_frame = ttk.Frame(book_frame)
        book_info_frame.pack(side=tk.LEFT, padx=15, fill=tk.Y, expand=True)
        ttk.Label(book_info_frame, text="立即尝试预约一次", style='Normal.TLabel').pack(anchor=tk.W)
        ttk.Label(book_info_frame, text="⚠️ 请先点击【预拉取场地】获取数据", style='Warning.TLabel').pack(anchor=tk.W, pady=2)

    def _build_operation_auto_section(self, parent):
        """构建自动预约控制区。"""
        auto_frame = ttk.LabelFrame(parent, text="🔄 自动预约控制", padding="20", style='Card.TLabelframe')
        auto_frame.pack(fill=tk.X, padx=20, pady=15)
        
        ttk.Label(auto_frame, text="启动后系统会在每天 08:00 自动尝试预约", style='Normal.TLabel').pack(pady=8)
        
        button_frame = ttk.Frame(auto_frame)
        button_frame.pack(pady=12)
        
        start_button = self._create_primary_button(button_frame, "▶️ 启动自动预约", self.start_auto_booking)
        start_button.pack(side=tk.LEFT, padx=15)

        stop_button = self._create_primary_button(button_frame, "⏹️ 停止自动预约", self.stop_auto_booking)
        stop_button.pack(side=tk.LEFT, padx=15)

    def _build_operation_stats_section(self, parent):
        """构建统计信息区域。"""
        stats_frame = ttk.LabelFrame(parent, text="📈 统计信息", padding="20", style='Card.TLabelframe')
        stats_frame.pack(fill=tk.X, padx=20, pady=15)
        
        self.stats_var = tk.StringVar(value="预约次数：0 | 最后预约时间：未预约")
        stats_label = ttk.Label(stats_frame, textvariable=self.stats_var, style='Normal.TLabel', font=('Microsoft YaHei UI', 11))
        stats_label.pack(pady=8)
    
    def init_log_tab(self):
        """初始化日志页"""
        # 日志控制区域
        control_frame = ttk.Frame(self.log_tab)
        control_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(control_frame, text="📋 操作日志 - 实时记录系统运行状态", style='Section.TLabel').pack(side=tk.LEFT, padx=10)
        
        clear_button = ttk.Button(control_frame, text="🗑️ 清空日志", command=self.clear_log, style='Normal.TButton')
        clear_button.pack(side=tk.RIGHT, padx=10)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(self.log_tab, wrap=tk.WORD, font=('Consolas', 11))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 设置日志文本颜色
        self.log_text.tag_config("info", foreground="#2c3e50")
        self.log_text.tag_config("success", foreground="#27ae60")
        self.log_text.tag_config("warning", foreground="#e67e22")
        self.log_text.tag_config("error", foreground="#c0392b")
        
        # 设置日志文本框的边框和背景
        self.log_text.config(borderwidth=1, relief=tk.SUNKEN, bg="#fbfdff", foreground="#1f2d3d", insertbackground="#1f2d3d")
        
        # 添加初始日志
        self.log("系统初始化完成", "success")
        self.log("欢迎使用南京医科大学场馆预约系统 v2", "info")
        self.log(f"当前 Python 解释器: {sys.executable}", "info")
        self.log(self._dependency_diagnostic_text(), "info")
        self.log("请先在【配置】页面设置账号和偏好", "warning")
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        self.log("日志已清空", "info")
    
    def save_config(self):
        """保存配置"""
        try:
            self._apply_form_values_to_config()
            self._persist_config_file()
            
            self.log("配置保存成功！", "success")
            self.welcome_status_var.set("配置已保存，可以开始使用")
            messagebox.showinfo("✅ 成功", "配置保存成功！\n\n请切换到【操作】页面进行预约。")
        except Exception as e:
            self.log(f"保存配置失败：{str(e)}", "error")
            messagebox.showerror("❌ 错误", f"保存配置失败：{str(e)}")

    def _collect_global_slots_from_ui(self):
        return self._collect_slots_from_vars(self.global_time_slot_vars)

    def _collect_weekly_slots_from_ui(self):
        weekly_slots = {}
        for weekday, slot_vars in self.weekly_time_slot_vars.items():
            weekly_slots[weekday] = self._collect_slots_from_vars(slot_vars)
        return weekly_slots

    def _apply_form_values_to_config(self):
        """将 GUI 表单值同步到运行时 Config 对象。"""
        Config.LOGIN_DATA['dlm'] = self.username_var.get().strip()
        Config.LOGIN_DATA['mm'] = self.password_var.get().strip()
        Config.DEFAULT_USERS = self.users_var.get().strip()
        Config.SERVICE_ID = self.service_var.get().strip()
        Config.PRIORITIZE_DATES = self._normalize_date_priority_input(self.date_priority_var.get())
        Config.PREFERRED_TIME_SLOTS = self._collect_global_slots_from_ui()
        Config.WEEKLY_PREFERRED_TIME_SLOTS = self._collect_weekly_slots_from_ui()

    def _persist_config_file(self):
        """将当前 Config 关键字段持久化回 backend/config.py。"""
        config_path = os.path.join(os.path.dirname(__file__), 'backend', 'config.py')
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        updated = self._update_config_content(content)
        self._write_config_atomically(config_path, updated)

    def _write_config_atomically(self, config_path, content):
        """以原子方式写回配置，先校验语法，失败时不覆盖原文件。"""
        # 先做语法校验，避免把损坏内容写入磁盘。
        compile(content, config_path, 'exec')

        temp_path = f"{config_path}.tmp"
        backup_path = f"{config_path}.bak"

        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(content)

        shutil.copy2(config_path, backup_path)
        os.replace(temp_path, config_path)
    
    def _update_config_content(self, content):
        """更新配置文件内容"""
        # 更新登录信息（在 LOGIN_DATA 字典内部）
        content = self._replace_login_fields(content)

        # 更新顶层配置
        content = self._replace_singleline_assignment(content, 'DEFAULT_USERS', Config.DEFAULT_USERS)
        content = self._replace_singleline_assignment(content, 'SERVICE_ID', Config.SERVICE_ID)
        content = self._replace_singleline_assignment(content, 'PRIORITIZE_DATES', Config.PRIORITIZE_DATES)
        content = self._replace_singleline_assignment(content, 'PREFERRED_TIME_SLOTS', Config.PREFERRED_TIME_SLOTS)
        content = self._replace_singleline_assignment(
            content,
            'WEEKLY_PREFERRED_TIME_SLOTS',
            Config.WEEKLY_PREFERRED_TIME_SLOTS,
        )

        return content

    def _replace_login_fields(self, content):
        """仅在 LOGIN_DATA 字典块内替换账号字段，避免误替换其他位置。"""
        import re

        block_pattern = r"(LOGIN_DATA\s*=\s*\{)(.*?)(\n\s*\})"
        block_match = re.search(block_pattern, content, flags=re.DOTALL)
        if not block_match:
            raise ValueError("未找到 LOGIN_DATA 配置块")

        block_prefix, block_body, block_suffix = block_match.groups()
        updated_body = self._replace_login_field_in_block(block_body, 'dlm', self.username_var.get())
        updated_body = self._replace_login_field_in_block(updated_body, 'mm', self.password_var.get())
        updated_block = f"{block_prefix}{updated_body}{block_suffix}"

        return content[:block_match.start()] + updated_block + content[block_match.end():]

    def _replace_singleline_assignment(self, content, key, value):
        """替换形如 KEY = value 的单行赋值。"""
        import re

        pattern = rf"^(\s*{re.escape(key)}\s*=\s*).*$"
        replacement = rf"\1{repr(value)}"
        updated, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
        if count == 0:
            raise ValueError(f"未找到配置项：{key}")
        return updated

    def _replace_login_field_in_block(self, block_body, field_key, field_value):
        """在指定 LOGIN_DATA 字典体中替换单个字段值。"""
        import re

        pattern = rf"([\'\"]{re.escape(field_key)}[\'\"]\s*:\s*)[\'\"][^\'\"]*[\'\"]"
        replacement = rf"\1{repr(field_value)}"
        updated, count = re.subn(pattern, replacement, block_body)
        if count == 0:
            raise ValueError(f"未找到 LOGIN_DATA 字段：{field_key}")
        return updated
    
    def fetch_venues(self):
        """预拉取场地"""
        def fetch_task():
            self._set_status("⏳ 正在拉取场地...", "正在连接服务器获取场地信息...")
            try:
                self._ensure_dependencies()
                
                setup_config()
                self.log("场地拉取成功！", "success")
                self._set_status("✅ 场地拉取成功", "配置正确，可以开始预约")
                messagebox.showinfo("✅ 成功", "场地拉取成功！\n\n请切换到【操作】页面进行预约。")
            except Exception as e:
                self.log(f"拉取场地失败：{str(e)}", "error")
                self._set_status("❌ 拉取失败", "请检查配置和网络连接")
                messagebox.showerror("❌ 错误", f"拉取场地失败：{str(e)}")

        self._run_in_background(fetch_task)
    
    def manual_book(self):
        """手动预约"""
        def book_task():
            self._set_status("⏳ 正在预约...", "正在尝试预约场地...")
            try:
                self._ensure_dependencies()
                
                # 检查是否已预拉取数据
                required_keys = ['stockid', 'stockdetail_id']
                missing = [key for key in required_keys if not Config.BOOKING_DATA.get(key)]
                if missing:
                    raise RuntimeError("请先点击【预拉取场地】获取数据，然后再尝试预约")
                
                Booking.book_venue()
                self.log("预约成功！", "success")
                self._set_status("✅ 预约成功", "预约已完成，请查看日志")
                self.booking_count += 1
                self.last_booking_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.update_stats()
                messagebox.showinfo("✅ 成功", "预约成功！\n\n请查看【日志】页面了解详情。")
            except Exception as e:
                self.log(f"预约失败：{str(e)}", "error")
                self._set_status("❌ 预约失败", "预约失败，请查看日志")
                messagebox.showerror("❌ 错误", f"预约失败：{str(e)}")

        self._run_in_background(book_task)
    
    def start_auto_booking(self):
        """启动自动预约"""
        if self.scheduler_running:
            messagebox.showinfo("ℹ️ 提示", "自动预约已经在运行中！")
            return

        try:
            self._ensure_dependencies()
        except Exception as e:
            messagebox.showerror("❌ 错误", str(e))
            return
        
        def scheduler_task():
            self.scheduler_running = True
            self._set_status("🔄 自动预约运行中", "系统将在每天 08:00 自动尝试预约")
            self.log("自动预约已启动", "success")
            try:
                start_scheduler()
            except Exception as e:
                self.log(f"自动预约异常：{str(e)}", "error")
                self._set_status("❌ 自动预约异常", "出现异常，请查看日志")
            finally:
                self.scheduler_running = False
                self.scheduler_thread = None

        self.scheduler_thread = self._run_in_background(scheduler_task)
        messagebox.showinfo("✅ 成功", "自动预约已启动！\n\n系统会在每天 08:00 自动尝试预约。\n请保持程序运行。")
    
    def stop_auto_booking(self):
        """停止自动预约"""
        if not self.scheduler_running:
            messagebox.showinfo("ℹ️ 提示", "自动预约未运行！")
            return
        
        # 尝试停止自动预约
        try:
            if stop_scheduler is not None:
                self._set_status("⏹️ 正在停止自动预约...", "等待调度线程安全退出")
                stop_scheduler()

            if self.scheduler_thread is not None and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=1.5)

            if self.scheduler_thread is not None and self.scheduler_thread.is_alive():
                self.scheduler_running = True
                self._set_status("⚠️ 停止请求已发出", "调度线程仍在收尾，稍后会自动停止")
                self.log("调度线程仍在收尾，请稍后再检查状态", "warning")
                messagebox.showwarning("⚠️ 提示", "停止请求已发出，调度线程正在收尾。")
                return

            self.scheduler_running = False
            self.scheduler_thread = None
            self._set_status("✅ 自动预约已停止", "自动预约已停止运行")
            self.log("自动预约已停止", "info")
            messagebox.showinfo("✅ 成功", "自动预约已停止！")
        except Exception as e:
            self.log(f"停止自动预约失败：{str(e)}", "error")
            messagebox.showerror("❌ 错误", f"停止自动预约失败：{str(e)}")
    
    def update_stats(self):
        """更新统计信息"""
        stats_text = f"预约次数：{self.booking_count} | 最后预约时间：{self.last_booking_time or '未预约'}"
        self.stats_var.set(stats_text)
    
    def log(self, message, level="info"):
        """记录日志"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry, level)
        self.log_text.see(tk.END)
        
        # 更新欢迎页状态
        if level == "error":
            self.welcome_status_var.set(f"⚠️ 发生错误：{message}")
        elif level == "success":
            self.welcome_status_var.set(f"✅ {message}")

    def _set_status(self, summary: str, detail: str | None = None):
        """统一更新操作页状态。"""
        self.status_var.set(summary)
        if detail is not None:
            self.detail_status_var.set(detail)

    def _ensure_dependencies(self):
        """检查运行依赖是否可用。"""
        missing = []
        for name in ("requests", "schedule"):
            try:
                importlib.import_module(name)
            except ImportError:
                missing.append(name)

        if missing:
            raise ImportError(
                f"当前解释器缺少依赖: {', '.join(missing)}\\n"
                f"Python: {sys.executable}"
            )

        if not load_dependencies():
            detail = _last_dependency_error or "后端模块导入失败"
            raise ImportError(f"后端依赖加载失败: {detail}\\nPython: {sys.executable}")

    def _run_in_background(self, target):
        """使用守护线程执行后台任务。"""
        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        return thread

    def _tick_clock(self):
        """顶部状态栏时钟。"""
        self.clock_var.set(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.root.after(1000, self._tick_clock)

    def _create_primary_button(self, parent, text, command):
        """创建统一样式的主要操作按钮。"""
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=self.ui['action_font'],
            bg=self.ui['primary'],
            fg='white',
            padx=20,
            pady=10,
            relief=tk.RAISED,
            activebackground=self.ui['primary_hover'],
            activeforeground='white',
            borderwidth=0,
            cursor='hand2',
        )

    def _build_time_slot_selector(self, parent, selected_slots, columns=4, compact=False):
        """构建时间段勾选器，返回带优先级顺序信息的选择器状态。"""
        normalized_selected = [item.strip() for item in (selected_slots or []) if item and item.strip()]
        merged_slots = list(dict.fromkeys(normalized_selected + self.available_time_slots))
        merged_slots.sort(key=self._time_slot_sort_key)

        selector_state = {
            'items': [],
            'order': [slot for slot in normalized_selected if slot in merged_slots],
        }
        panel = ttk.Frame(parent, style='Card.TFrame')
        panel.pack(fill=tk.X, padx=6, pady=4)

        for idx, slot in enumerate(merged_slots):
            var = tk.BooleanVar(value=slot in normalized_selected)

            row = idx // columns
            col = idx % columns
            cb = tk.Checkbutton(
                panel,
                text=slot,
                variable=var,
                command=lambda slot=slot, state=selector_state: self._on_time_slot_toggled(state, slot),
                anchor='w',
                justify='left',
                bg=self.ui['surface'],
                fg=self.ui['text'],
                activebackground=self.ui['surface'],
                activeforeground=self.ui['text'],
                selectcolor=self.ui['surface'],
                font=('Microsoft YaHei UI', 9 if compact else 10),
                padx=4,
                pady=2,
            )
            cb.grid(row=row, column=col, sticky='w', padx=6, pady=2)
            selector_state['items'].append({
                'slot': slot,
                'var': var,
                'checkbox': cb,
            })

        self._refresh_time_slot_labels(selector_state)

        return selector_state

    def _on_time_slot_toggled(self, selector_state, slot):
        """处理勾选变化，维护选择顺序并刷新序号显示。"""
        items = selector_state.get('items', [])
        order = selector_state.get('order', [])

        selected = False
        for item in items:
            if item['slot'] == slot:
                selected = bool(item['var'].get())
                break

        if selected and slot not in order:
            order.append(slot)
        elif not selected and slot in order:
            order.remove(slot)

        self._refresh_time_slot_labels(selector_state)

    def _refresh_time_slot_labels(self, selector_state):
        """刷新时间段文本，已勾选项展示优先级序号。"""
        order = selector_state.get('order', [])
        index_map = {slot: idx + 1 for idx, slot in enumerate(order)}

        for item in selector_state.get('items', []):
            slot = item['slot']
            rank = index_map.get(slot)
            if rank is None:
                item['checkbox'].configure(text=f"- {slot}")
            else:
                item['checkbox'].configure(text=f"{rank}. {slot}")

    def _collect_slots_from_vars(self, slot_vars):
        """收集已勾选时间段，优先使用显式序号顺序。"""
        if isinstance(slot_vars, dict):
            return list(slot_vars.get('order', []))

        selected = []
        for slot, var in slot_vars:
            if var.get():
                selected.append(slot)
        return selected

    def _normalize_date_priority_input(self, raw_text):
        """规范化日期优先级输入，去空值并保留原有顺序。"""
        normalized = []
        seen = set()
        for item in (raw_text or '').split(','):
            token = item.strip()
            if not token or token in seen:
                continue
            normalized.append(token)
            seen.add(token)

        if not normalized:
            return ['tomorrow', 'today']
        return normalized

    def _time_slot_sort_key(self, slot):
        """按时间段起始时间排序；非标准格式排在后面。"""
        text = (slot or "").strip()
        if '-' not in text:
            return (1, 99, 99, text)

        start_text = text.split('-', 1)[0].strip()
        if ':' not in start_text:
            return (1, 99, 99, text)

        try:
            hour_text, minute_text = start_text.split(':', 1)
            hour = int(hour_text)
            minute = int(minute_text)
            return (0, hour, minute, text)
        except ValueError:
            return (1, 99, 99, text)

    def _dependency_diagnostic_text(self):
        """返回关键依赖的可导入状态，便于快速确认运行环境。"""
        status = []
        for name in ("requests", "schedule"):
            try:
                importlib.import_module(name)
                status.append(f"{name}=ok")
            except ImportError:
                status.append(f"{name}=missing")
        return "依赖状态: " + ", ".join(status)

def main():
    root = tk.Tk()
    app = BookingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
