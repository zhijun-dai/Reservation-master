# Start.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys, os, re
import importlib
import shutil


from backend.config import Config
import datetime

# 延迟导入依赖项，以便GUI可以启动
setup_config = None
book_venue = None
start_scheduler = None
stop_scheduler = None
_last_dependency_error = ""

def load_dependencies():
    global _last_dependency_error
    global setup_config, book_venue, start_scheduler, stop_scheduler
    try:
        from backend.config_setup import setup_config
        from backend.book import book_venue
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
            'bg': '#f0f2f5',
            'surface': '#ffffff',
            'text': '#1a2332',
            'muted_text': '#6b7a8d',
            'primary': '#4f6ef7',
            'primary_hover': '#3b5de7',
            'primary_light': '#eef1ff',
            'accent': '#ff6b6b',
            'success': '#20c997',
            'warning': '#fbbf24',
            'error': '#ef4444',
            'border': '#e2e5ea',
            'header_bg': '#4f6ef7',
            'header_fg': '#ffffff',
            'title_font': ('Microsoft YaHei UI', 20, 'bold'),
            'subtitle_font': ('Microsoft YaHei UI', 14),
            'normal_font': ('Microsoft YaHei UI', 10),
            'action_font': ('Microsoft YaHei UI', 11, 'bold'),
            'small_font': ('Microsoft YaHei UI', 9),
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
        self.style.configure('Card.TLabelframe', background=self.ui['surface'], bordercolor=self.ui['border'], relief=tk.FLAT, borderwidth=1)
        self.style.configure('Card.TLabelframe.Label', background=self.ui['surface'], foreground=self.ui['primary'], font=self.ui['action_font'])

        self.style.configure('Header.TFrame', background=self.ui['header_bg'])
        self.style.configure('Title.TLabel', font=self.ui['title_font'], foreground=self.ui['text'], background=self.ui['bg'])
        self.style.configure('HeaderTitle.TLabel', font=self.ui['title_font'], foreground=self.ui['header_fg'], background=self.ui['header_bg'])
        self.style.configure('HeaderSub.TLabel', font=('Microsoft YaHei UI', 11), foreground='#c8d6ff', background=self.ui['header_bg'])
        self.style.configure('Subtitle.TLabel', font=self.ui['subtitle_font'], foreground=self.ui['muted_text'], background=self.ui['surface'])
        self.style.configure('Section.TLabel', font=self.ui['subtitle_font'], foreground=self.ui['primary'], background=self.ui['surface'])
        self.style.configure('Normal.TLabel', font=self.ui['normal_font'], foreground=self.ui['text'], background=self.ui['surface'])
        self.style.configure('Muted.TLabel', font=self.ui['normal_font'], foreground=self.ui['muted_text'], background=self.ui['surface'])
        self.style.configure('Success.TLabel', font=self.ui['normal_font'], foreground=self.ui['success'], background=self.ui['surface'])
        self.style.configure('Warning.TLabel', font=self.ui['normal_font'], foreground=self.ui['warning'], background=self.ui['surface'])
        self.style.configure('Error.TLabel', font=self.ui['normal_font'], foreground=self.ui['error'], background=self.ui['surface'])
        self.style.configure('Normal.TButton', font=self.ui['normal_font'], padding=5)
        self.style.configure('TButton', font=self.ui['normal_font'])

        self.style.configure('Card.TLabelframe', background=self.ui['surface'], bordercolor=self.ui['border'], relief=tk.FLAT, borderwidth=1)
        self.style.configure('TNotebook', background=self.ui['bg'], borderwidth=0)
        self.style.configure('TNotebook.Tab', padding=(20, 10), font=self.ui['action_font'])
        self.style.map('TNotebook.Tab',
                  background=[('selected', self.ui['surface']), ('!selected', self.ui['bg'])],
                  foreground=[('selected', self.ui['primary']), ('!selected', self.ui['muted_text'])],
                  lightcolor=[('selected', self.ui['surface']), ('!selected', self.ui['bg'])],
                  borderwidth=[('selected', 0), ('!selected', 0)])

        # 顶部标题栏
        header_frame = tk.Frame(root, bg=self.ui['header_bg'], height=64)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="🏸 南京医科大学场馆预约系统", font=self.ui['title_font'],
                 bg=self.ui['header_bg'], fg=self.ui['header_fg']).pack(side=tk.LEFT, padx=24, pady=12)
        tk.Label(header_frame, text="智能预约助手", font=('Microsoft YaHei UI', 12),
                 bg=self.ui['header_bg'], fg='#dce3ff').pack(side=tk.LEFT, padx=(4, 0), pady=12)

        self.clock_var = tk.StringVar(value="")
        tk.Label(header_frame, textvariable=self.clock_var, font=('Microsoft YaHei UI', 11),
                 bg=self.ui['header_bg'], fg='#c8d6ff').pack(side=tk.RIGHT, padx=24, pady=12)
        self._tick_clock()

        # 主框架
        self.main_frame = ttk.Frame(root, padding="16", style='App.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.welcome_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.welcome_tab, text="🏠 首页")
        self.config_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.config_tab, text="⚙️ 配置")
        self.operation_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.operation_tab, text="🎯 操作")
        self.log_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.log_tab, text="📋 日志")

        self.canvases = {}

        self.init_welcome_tab()
        self.init_config_tab()
        self.init_operation_tab()
        self.init_log_tab()

        self.root.bind("<MouseWheel>", self._on_mouse_wheel)
        
        # 调度器线程
        self.scheduler_thread = None
        self.scheduler_running = False
        
        self.last_booking_time = None
        self.booking_count = 0
    
    _tab_key_map = {"🏠 首页": "welcome", "⚙️ 配置": "config", "🎯 操作": "operation"}

    def _on_mouse_wheel(self, event):
        try:
            tab_text = self.notebook.tab(self.notebook.select(), "text")
        except:
            return
        canvas = self.canvases.get(self._tab_key_map.get(tab_text))
        if canvas:
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _create_scrollable_tab(self, tab_widget, tab_key):
        canvas = tk.Canvas(tab_widget, bg=self.ui['bg'], highlightthickness=0, borderwidth=0)
        scrollbar = ttk.Scrollbar(tab_widget, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='App.TFrame')

        def _configure_inner(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # 让内层 frame 宽度跟随 canvas
            canvas.itemconfig(win_id, width=canvas.winfo_width())

        scrollable_frame.bind("<Configure>", _configure_inner)

        win_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        self.canvases[tab_key] = canvas

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return scrollable_frame
    
    def _make_section(self, parent, title):
        outer = tk.Frame(parent, bg=self.ui['bg'], pady=5)
        outer.pack(fill=tk.X, padx=6)

        card = tk.Frame(outer, bg=self.ui['surface'], padx=16, pady=14)
        card.pack(fill=tk.X)

        # 顶部彩色条
        tk.Frame(card, bg=self.ui['primary'], height=3).pack(fill=tk.X)

        # 标题行
        header = tk.Frame(card, bg=self.ui['surface'])
        header.pack(fill=tk.X, pady=(10, 6))
        tk.Label(header, text=title, font=self.ui['action_font'],
                 bg=self.ui['surface'], fg=self.ui['primary']).pack(side=tk.LEFT)

        # 分隔线
        tk.Frame(card, bg=self.ui['border'], height=1).pack(fill=tk.X, pady=(0, 8))

        return card

    def init_welcome_tab(self):
        scrollable_frame = self._create_scrollable_tab(self.welcome_tab, 'welcome')

        welcome_frame = self._make_section(scrollable_frame, "👋 欢迎使用")
        
        ttk.Label(welcome_frame, text="欢迎使用南京医科大学场馆预约系统！", style='Subtitle.TLabel').pack(pady=8)
        ttk.Label(welcome_frame, text="本系统专为医学生设计，无需编程知识即可自动预约场馆。", style='Normal.TLabel').pack(pady=5)
        
        # 系统信息
        info_frame = self._make_section(scrollable_frame, "ℹ️ 系统信息")
        
        info_text = """
当前版本：v2
适用场馆：羽毛球馆（serviceid=22）

自动预约时间：每天 08:00 自动尝试预约
放号窗口：08:00 - 08:30（30 分钟）
        """
        info_label = ttk.Label(info_frame, text=info_text, style='Normal.TLabel', justify=tk.LEFT)
        info_label.pack(pady=8)

        py_path_label = tk.Label(info_frame, text=f"Python: {sys.executable}",
                                 font=('Consolas', 8), anchor=tk.W, justify=tk.LEFT,
                                 bg=self.ui['surface'], fg=self.ui['muted_text'])
        py_path_label.pack(fill=tk.X, padx=4, pady=(0, 4))

        # 快速开始指南
        guide_frame = self._make_section(scrollable_frame, "📖 快速开始指南")
        
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
        help_frame = self._make_section(scrollable_frame, "❓ 使用说明")
        
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
        faq_frame = self._make_section(scrollable_frame, "❗ 常见问题")
        
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
        
        status_frame = self._make_section(scrollable_frame, "📊 当前状态")

        self.welcome_status_var = tk.StringVar(value="系统就绪，可以开始使用")
        status_container = tk.Frame(status_frame, bg=self.ui['primary_light'], padx=16, pady=12)
        status_container.pack(fill=tk.X, padx=10, pady=8)
        tk.Label(status_container, textvariable=self.welcome_status_var,
                 font=('Microsoft YaHei UI', 12, 'bold'), bg=self.ui['primary_light'], fg=self.ui['primary']).pack()
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tk.Label(status_container, text=f"当前时间：{current_time}",
                 font=self.ui['normal_font'], bg=self.ui['primary_light'], fg=self.ui['muted_text']).pack(pady=(4, 0))
        
    
    def init_config_tab(self):
        """初始化配置页"""
        scrollable_frame = self._create_scrollable_tab(self.config_tab, 'config')
        self._build_account_config_section(scrollable_frame)
        self._build_time_preference_section(scrollable_frame)
        self._build_weekly_time_preference_section(scrollable_frame)
        self._build_config_save_section(scrollable_frame)

    def _build_account_config_section(self, parent):
        """构建账号与基础配置区域。"""
        config_frame = self._make_section(parent, "🔑 账号配置")
        
        form_frame = ttk.Frame(config_frame)
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        fields = [
            ("学号:", Config.LOGIN_DATA['dlm'], "（登录系统的账号，只需填一个）", None, 30),
            ("密码:", Config.LOGIN_DATA['mm'], "（登录系统的密码）", "*", 30),
            ("默认使用者:", Config.DEFAULT_USERS, "（实际入场学号，多个用/分隔）", None, 30),
            ("场馆类型:", Config.SERVICE_ID, "（羽毛球馆：22）", None, 15),
        ]
        self._form_vars = {}
        for row, (label, default, hint, show, width) in enumerate(fields):
            tk.Label(form_frame, text=label, font=self.ui['normal_font'],
                     bg=self.ui['surface'], fg=self.ui['text'], anchor='e', width=12).grid(
                row=row, column=0, sticky=tk.E, padx=(10, 4), pady=8)
            var = tk.StringVar(value=default)
            entry = tk.Entry(form_frame, textvariable=var, width=width, show=show,
                             font=self.ui['normal_font'], relief=tk.FLAT, bd=1,
                             highlightthickness=1, highlightcolor=self.ui['border'],
                             highlightbackground=self.ui['border'])
            entry.grid(row=row, column=1, sticky=tk.W, padx=4, pady=8, ipady=4)
            tk.Label(form_frame, text=hint, font=self.ui['small_font'],
                     bg=self.ui['surface'], fg=self.ui['muted_text']).grid(
                row=row, column=2, sticky=tk.W, padx=10, pady=8)
            self._form_vars[label] = var

        self.username_var = self._form_vars["学号:"]
        self.password_var = self._form_vars["密码:"]
        self.users_var = self._form_vars["默认使用者:"]
        self.service_var = self._form_vars["场馆类型:"]

        # 日期优先级（点击排序）
        date_frame = tk.Frame(config_frame, bg=self.ui['surface'])
        date_frame.pack(fill=tk.X, padx=10, pady=(0, 8))
        tk.Label(date_frame, text="日期优先级:", font=self.ui['normal_font'],
                 bg=self.ui['surface'], fg=self.ui['text'], anchor='e', width=12).pack(side=tk.LEFT, padx=(10, 4))
        tk.Label(date_frame, text="点击设置顺序（1=优先尝试）",
                 font=self.ui['small_font'], bg=self.ui['surface'], fg=self.ui['muted_text']).pack(side=tk.RIGHT, padx=10)

        self._date_priority_vars = {}
        self._date_priority_cells = {}
        date_options = ["today", "tomorrow"]
        saved = Config.PRIORITIZE_DATES or []

        dp_row = tk.Frame(config_frame, bg=self.ui['surface'])
        dp_row.pack(fill=tk.X, padx=10, pady=(0, 10))

        for d in date_options:
            var = tk.BooleanVar(value=d in saved)
            rank = self._dp_rank(d, saved)
            display = str(rank) if rank else ""
            cell = tk.Label(dp_row, text=display, font=('Microsoft YaHei UI', 16, 'bold'),
                            width=3, anchor=tk.CENTER, cursor='hand2',
                            bg=self.ui['primary'] if rank else self.ui['border'],
                            fg='white' if rank else self.ui['muted_text'])
            cell.pack(side=tk.LEFT, padx=6, ipadx=10, ipady=6)
            cell.bind('<Button-1>', lambda e, x=d: self._dp_click(x))
            cell.bind('<Enter>', lambda e, c=cell, x=d: c.configure(
                bg=self.ui['primary_light'] if x in Config.PRIORITIZE_DATES else '#e8e8ec'))
            cell.bind('<Leave>', lambda e, c=cell, x=d: c.configure(
                bg=self.ui['primary'] if x in Config.PRIORITIZE_DATES else self.ui['border']))

            tk.Label(dp_row, text=d, font=self.ui['small_font'],
                     bg=self.ui['surface'], fg=self.ui['text']).pack(side=tk.LEFT, padx=(0, 8))

            self._date_priority_vars[d] = var
            self._date_priority_cells[d] = cell

    def _dp_rank(self, date_val, order):
        try:
            return order.index(date_val) + 1
        except ValueError:
            return 0

    def _dp_click(self, date_val):
        order = Config.PRIORITIZE_DATES
        if date_val in order:
            order.remove(date_val)
            self._date_priority_vars[date_val].set(False)
        else:
            order.append(date_val)
            self._date_priority_vars[date_val].set(True)
        self._refresh_dp()

    def _refresh_dp(self):
        order = Config.PRIORITIZE_DATES
        for d, cell in self._date_priority_cells.items():
            rank = self._dp_rank(d, order)
            selected = rank > 0
            cell.config(text=str(rank) if selected else "",
                        bg=self.ui['primary'] if selected else self.ui['border'],
                        fg='white' if selected else self.ui['muted_text'])

    def _build_time_preference_section(self, parent):
        slots_frame = self._make_section(parent, "⏰ 时间段偏好设置")

        tk.Label(slots_frame, text="全局时间段偏好 — 点击设置优先级（数字越小优先级越高）",
                 font=self.ui['normal_font'], bg=self.ui['surface'], fg=self.ui['text'],
                 anchor=tk.W).pack(pady=(10, 2), padx=6, anchor=tk.W)
        tk.Label(slots_frame, text="留空时使用系统默认顺序，按从早到晚尝试",
                 font=self.ui['small_font'], bg=self.ui['surface'], fg=self.ui['muted_text'],
                 anchor=tk.W).pack(pady=(0, 8), padx=6, anchor=tk.W)

        # 垂直列表容器
        list_frame = tk.Frame(slots_frame, bg=self.ui['surface'])
        list_frame.pack(fill=tk.X, padx=10, pady=4)

        # 初始化数据
        saved = Config.PREFERRED_TIME_SLOTS or []
        self.global_time_slot_vars = {
            'items': {ts: tk.BooleanVar(value=ts in saved) for ts in self.available_time_slots},
            'order': [ts for ts in saved if ts in self.available_time_slots],
        }
        self._global_cells = {}

        row_bg = [self.ui['surface'], '#f8f9fc']
        for ri, slot in enumerate(self.available_time_slots):
            bg = row_bg[ri % 2]
            rank = self._global_rank(slot)
            display = str(rank) if rank else ""

            row = tk.Frame(list_frame, bg=bg)
            row.pack(fill=tk.X, pady=1)
            row.bind('<Enter>', lambda e, c=row, b=bg: c.configure(bg=self.ui['primary_light']) if b != self.ui['primary_light'] else None)
            row.bind('<Leave>', lambda e, c=row, b=bg: c.configure(bg=b))

            cell = tk.Label(row, text=display, font=('Microsoft YaHei UI', 10 if rank else 11, 'bold'),
                            bg=bg, fg=self.ui['primary'] if rank else self.ui['border'],
                            width=3, anchor=tk.CENTER, cursor='hand2')
            cell.pack(side=tk.LEFT, padx=3, pady=1, ipady=4)
            cell.bind('<Button-1>', lambda e, s=slot: self._global_cell_click(s))

            tk.Label(row, text=slot, font=('Microsoft YaHei UI', 10),
                     bg=bg, fg=self.ui['text'], anchor=tk.W, width=14).pack(side=tk.LEFT, padx=6, pady=2)

            tk.Label(row, text='', bg=bg).pack(side=tk.LEFT, fill=tk.X, expand=True, pady=2)

            self._global_cells[slot] = cell

        warning_frame = tk.Frame(slots_frame, bg='#fffbeb', padx=12, pady=8)
        warning_frame.pack(fill=tk.X, padx=6, pady=(6, 4))
        tk.Label(warning_frame, text="⚠️ 系统预约速度非常快，时间段的序号决定了尝试的先后顺序",
                 font=self.ui['small_font'], bg='#fffbeb', fg=self.ui['warning']).pack(anchor=tk.W)

    def _global_rank(self, slot):
        order = self.global_time_slot_vars.get('order', [])
        try:
            return order.index(slot) + 1
        except ValueError:
            return 0

    def _global_cell_click(self, slot):
        data = self.global_time_slot_vars
        var = data['items'][slot]
        order = data['order']
        if var.get():
            var.set(False)
            if slot in order:
                order.remove(slot)
        else:
            var.set(True)
            if slot not in order:
                order.append(slot)
        self._refresh_global_cells()

    def _refresh_global_cells(self):
        for slot in self.available_time_slots:
            cell = self._global_cells.get(slot)
            if not cell:
                continue
            rank = self._global_rank(slot)
            cell.config(text=str(rank) if rank else "－",
                        fg=self.ui['primary'] if rank else self.ui['border'])


    def _build_weekly_time_preference_section(self, parent):
        week_frame = self._make_section(parent, "📅 按星期几的时间段偏好")

        hint = tk.Label(week_frame, text="点击格子设置优先级（数字越小优先级越高，留空则使用全局设置）",
                        font=self.ui['small_font'], bg=self.ui['surface'], fg=self.ui['muted_text'],
                        anchor=tk.W).pack(pady=(8, 4), padx=6, anchor=tk.W)

        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        weekday_labels = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

        self.weekly_time_slot_vars = {}
        self._weekly_cells = {}

        table_container = tk.Frame(week_frame, bg=self.ui['surface'])
        table_container.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        canvas = tk.Canvas(table_container, bg=self.ui['surface'], highlightthickness=0, height=420)
        h_scroll = tk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=canvas.xview)
        canvas.configure(xscrollcommand=h_scroll.set)

        inner = tk.Frame(canvas, bg=self.ui['surface'])
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        HEADER_BG = '#f0f2f5'
        tk.Label(inner, text="时段", font=('Microsoft YaHei UI', 9, 'bold'),
                 bg=HEADER_BG, fg=self.ui['text'], width=11, anchor=tk.CENTER,
                 relief=tk.FLAT, bd=0).grid(row=0, column=0, sticky='ns', padx=1, pady=1, ipady=3)
        for ci, name in enumerate(weekday_labels):
            tk.Label(inner, text=name, font=('Microsoft YaHei UI', 9, 'bold'),
                     bg=HEADER_BG, fg=self.ui['text'], width=7, anchor=tk.CENTER,
                     relief=tk.FLAT, bd=0).grid(row=0, column=ci+1, sticky='ns', padx=1, pady=1, ipady=3)

        row_bg = [self.ui['surface'], '#f8f9fc']
        for ri, slot in enumerate(self.available_time_slots):
            bg_color = row_bg[ri % 2]
            r = ri + 1

            tk.Label(inner, text=slot, font=('Microsoft YaHei UI', 8),
                     bg=bg_color, fg=self.ui['muted_text'], width=11, anchor=tk.CENTER
                     ).grid(row=r, column=0, sticky='ns', padx=1, pady=1, ipady=1)

            for ci, weekday in enumerate(weekdays):
                if weekday not in self.weekly_time_slot_vars:
                    saved = Config.WEEKLY_PREFERRED_TIME_SLOTS.get(weekday, [])
                    self.weekly_time_slot_vars[weekday] = {
                        'items': {ts: tk.BooleanVar(value=ts in saved) for ts in self.available_time_slots},
                        'order': [ts for ts in saved if ts in self.available_time_slots],
                    }
                var = self.weekly_time_slot_vars[weekday]['items'][slot]
                rank = self._weekly_rank(weekday, slot)
                display = str(rank) if rank else "－"
                fg_color = self.ui['primary'] if rank else self.ui['border']

                cell = tk.Label(inner, text=display, font=('Microsoft YaHei UI', 9, 'bold'),
                                bg=bg_color, fg=fg_color, width=7, anchor=tk.CENTER,
                                cursor='hand2', relief=tk.FLAT, bd=0)
                cell.grid(row=r, column=ci+1, sticky='ns', padx=1, pady=1, ipady=2)
                cell.bind('<Button-1>', lambda e, w=weekday, s=slot: self._weekly_cell_click(w, s))
                cell.bind('<Enter>', lambda e, c=cell: c.configure(bg=self.ui['primary_light']))
                cell.bind('<Leave>', lambda e, c=cell, b=bg_color: c.configure(bg=b))
                self._weekly_cells[(weekday, slot)] = cell

    def _weekly_rank(self, weekday, slot):
        order = self.weekly_time_slot_vars[weekday].get('order', [])
        try:
            return order.index(slot) + 1
        except ValueError:
            return 0

    def _weekly_cell_click(self, weekday, slot):
        data = self.weekly_time_slot_vars[weekday]
        var = data['items'][slot]
        order = data['order']
        if var.get():
            var.set(False)
            if slot in order:
                order.remove(slot)
        else:
            var.set(True)
            if slot not in order:
                order.append(slot)
        self._refresh_weekly_cells(weekday)

    def _refresh_weekly_cells(self, weekday):
        for slot in self.available_time_slots:
            cell = self._weekly_cells.get((weekday, slot))
            if not cell:
                continue
            rank = self._weekly_rank(weekday, slot)
            cell.config(text=str(rank) if rank else "－",
                        fg=self.ui['primary'] if rank else self.ui['border'])

    def _build_config_save_section(self, parent):
        save_frame = tk.Frame(parent, bg=self.ui['bg'])
        save_frame.pack(pady=25)

        self._save_btn = self._create_primary_button(save_frame, "💾 保存配置", self.save_config)
        self._save_btn.pack(side=tk.LEFT, padx=10)
        tk.Label(save_frame, text="保存后配置会写入 config.py 文件", font=self.ui['small_font'],
                 bg=self.ui['bg'], fg=self.ui['muted_text']).pack(side=tk.LEFT, padx=10)
    
    def init_operation_tab(self):
        """初始化操作页"""
        scrollable_frame = self._create_scrollable_tab(self.operation_tab, 'operation')
        self._build_operation_status_section(scrollable_frame)
        self._build_operation_action_section(scrollable_frame)
        self._build_operation_auto_section(scrollable_frame)
        self._build_operation_stats_section(scrollable_frame)

    def _build_operation_status_section(self, parent):
        status_frame = self._make_section(parent, "📊 系统状态")

        self.status_var = tk.StringVar(value="✅ 系统就绪")
        status_container = tk.Frame(status_frame, bg=self.ui['primary_light'], padx=16, pady=16)
        status_container.pack(fill=tk.X, padx=10, pady=8)
        tk.Label(status_container, textvariable=self.status_var,
                 font=('Microsoft YaHei UI', 18, 'bold'), bg=self.ui['primary_light'], fg=self.ui['primary']).pack()

        self.detail_status_var = tk.StringVar(value="等待操作...")
        tk.Label(status_container, textvariable=self.detail_status_var,
                 font=self.ui['normal_font'], bg=self.ui['primary_light'], fg=self.ui['muted_text']).pack(pady=(4, 0))

    def _build_operation_action_section(self, parent):
        action_frame = self._make_section(parent, "🎯 操作面板")

        self._action_btns = {}
        for btn_text, cmd, desc, warn in [
            ("📍 预拉取场地", self.fetch_venues, "测试配置，获取可用场地信息", None),
            ("⚡ 立即预约", self.manual_book, "立即尝试预约一次", "⚠️ 请先点击【预拉取场地】获取数据"),
        ]:
            row = tk.Frame(action_frame, bg=self.ui['surface'])
            row.pack(fill=tk.X, pady=6, padx=6)

            btn = self._create_primary_button(row, btn_text, cmd)
            btn.pack(side=tk.LEFT, padx=8)
            self._action_btns[btn_text.strip("📍⚡ ")] = btn

            info_col = tk.Frame(row, bg=self.ui['surface'])
            info_col.pack(side=tk.LEFT, padx=8, fill=tk.Y, expand=True)
            tk.Label(info_col, text=desc, font=self.ui['normal_font'],
                     bg=self.ui['surface'], fg=self.ui['text'], anchor=tk.W).pack(anchor=tk.W)
            if warn:
                warn_label = tk.Label(info_col, text=warn, font=self.ui['small_font'],
                         bg=self.ui['surface'], fg=self.ui['warning'], anchor=tk.W)
                warn_label.pack(anchor=tk.W, pady=2)

    def _build_operation_auto_section(self, parent):
        auto_frame = self._make_section(parent, "🔄 自动预约控制")

        desc_frame = tk.Frame(auto_frame, bg=self.ui['surface'])
        desc_frame.pack(fill=tk.X, padx=10, pady=(10, 4))
        tk.Label(desc_frame, text="启动后系统会在每天 08:00 自动尝试预约",
                 font=self.ui['normal_font'], bg=self.ui['surface'], fg=self.ui['text']).pack(anchor=tk.W)

        button_frame = tk.Frame(auto_frame, bg=self.ui['surface'])
        button_frame.pack(pady=(8, 14))

        self._start_auto_btn = self._create_primary_button(button_frame, "▶️ 启动自动预约", self.start_auto_booking)
        self._start_auto_btn.pack(side=tk.LEFT, padx=12)

        self._stop_auto_btn = tk.Label(button_frame, text="⏹️ 停止自动预约", font=self.ui['action_font'],
                            bg=self.ui['surface'], fg=self.ui['error'], padx=16, pady=9, cursor='hand2')
        self._stop_auto_btn.pack(side=tk.LEFT, padx=12)
        self._stop_auto_btn.bind('<Button-1>', lambda e: self.stop_auto_booking())
        self._stop_auto_btn.bind('<Enter>', lambda e: self._stop_auto_btn.configure(bg='#fef2f2'))
        self._stop_auto_btn.bind('<Leave>', lambda e: self._stop_auto_btn.configure(bg=self.ui['surface']))

    def _build_operation_stats_section(self, parent):
        stats_frame = self._make_section(parent, "📈 统计信息")

        self.stats_var = tk.StringVar(value="预约次数：0 | 最后预约时间：未预约")
        stat_container = tk.Frame(stats_frame, bg=self.ui['primary_light'], padx=16, pady=12)
        stat_container.pack(fill=tk.X, padx=10, pady=8)
        tk.Label(stat_container, textvariable=self.stats_var, font=self.ui['normal_font'],
                 bg=self.ui['primary_light'], fg=self.ui['primary']).pack()
    
    def init_log_tab(self):
        control_frame = tk.Frame(self.log_tab, bg=self.ui['surface'])
        control_frame.pack(fill=tk.X, padx=20, pady=(15, 5))

        tk.Label(control_frame, text="📋 操作日志", font=self.ui['subtitle_font'],
                 bg=self.ui['surface'], fg=self.ui['primary']).pack(side=tk.LEFT, padx=10)

        clear_btn = tk.Label(control_frame, text="🗑️ 清空日志", font=self.ui['normal_font'],
                             bg=self.ui['surface'], fg=self.ui['muted_text'], cursor='hand2')
        clear_btn.pack(side=tk.RIGHT, padx=10)
        clear_btn.bind('<Button-1>', lambda e: self.clear_log())
        clear_btn.bind('<Enter>', lambda e: clear_btn.configure(fg=self.ui['error']))
        clear_btn.bind('<Leave>', lambda e: clear_btn.configure(fg=self.ui['muted_text']))

        self.log_text = scrolledtext.ScrolledText(self.log_tab, wrap=tk.WORD, font=('Consolas', 11),
                                                   borderwidth=1, relief=tk.FLAT, bg="#fafbfc",
                                                   foreground=self.ui['text'], insertbackground=self.ui['text'])
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.log_text.tag_config("info", foreground=self.ui['muted_text'])
        self.log_text.tag_config("success", foreground=self.ui['success'])
        self.log_text.tag_config("warning", foreground=self.ui['warning'])
        self.log_text.tag_config("error", foreground=self.ui['error'])
        
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
        self._save_btn.config(text="⏳ 保存中...", bg=self.ui['primary_hover'])
        self.root.update_idletasks()
        try:
            self._apply_form_values_to_config()
            self._persist_config_file()

            self._save_btn.config(text="✅ 已保存", bg=self.ui['success'])
            self.root.after(1500, lambda: self._save_btn.config(text="💾 保存配置", bg=self.ui['primary']))
            self.log("配置保存成功！", "success")
            self.welcome_status_var.set("配置已保存，可以开始使用")
            messagebox.showinfo("✅ 成功", "配置保存成功！\n\n请切换到【操作】页面进行预约。")
        except Exception as e:
            self._save_btn.config(text="❌ 失败", bg=self.ui['error'])
            self.root.after(2000, lambda: self._save_btn.config(text="💾 保存配置", bg=self.ui['primary']))
            self.log(f"保存配置失败：{str(e)}", "error")
            messagebox.showerror("❌ 错误", f"保存配置失败：{str(e)}")

    def _collect_global_slots_from_ui(self):
        return list(self.global_time_slot_vars.get('order', []))

    def _collect_weekly_slots_from_ui(self):
        weekly_slots = {}
        for weekday, data in self.weekly_time_slot_vars.items():
            weekly_slots[weekday] = list(data.get('order', []))
        return weekly_slots

    def _apply_form_values_to_config(self):
        """将 GUI 表单值同步到运行时 Config 对象。"""
        Config.LOGIN_DATA['dlm'] = self.username_var.get().strip()
        Config.LOGIN_DATA['mm'] = self.password_var.get().strip()
        Config.DEFAULT_USERS = self.users_var.get().strip()
        Config.SERVICE_ID = self.service_var.get().strip()
        # 日期优先级已被 _dp_click 直接修改 Config.PRIORITIZE_DATES
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
        pattern = rf"^(\s*{re.escape(key)}\s*=\s*).*$"
        replacement = rf"\1{repr(value)}"
        updated, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
        if count == 0:
            raise ValueError(f"未找到配置项：{key}")
        return updated

    def _replace_login_field_in_block(self, block_body, field_key, field_value):
        """在指定 LOGIN_DATA 字典体中替换单个字段值。"""
        pattern = rf"([\'\"]{re.escape(field_key)}[\'\"]\s*:\s*)[\'\"][^\'\"]*[\'\"]"
        replacement = rf"\1{repr(field_value)}"
        updated, count = re.subn(pattern, replacement, block_body)
        if count == 0:
            raise ValueError(f"未找到 LOGIN_DATA 字段：{field_key}")
        return updated
    
    def fetch_venues(self):
        self._action_btns.setdefault("预拉取场地", tk.Label())
        self._action_btns["预拉取场地"].config(text="⏳ 拉取中...", bg=self.ui['primary_hover'])
        self.root.update_idletasks()
        def fetch_task():
            self._set_status("⏳ 正在拉取场地...", "正在连接服务器获取场地信息...")
            try:
                self._ensure_dependencies()
                setup_config(scan_all=True)
                self._action_btns["预拉取场地"].config(text="✅ 已获取", bg=self.ui['success'])
                self.root.after(2000, lambda: self._action_btns["预拉取场地"].config(text="📍 预拉取场地", bg=self.ui['primary']))
                self.log("场地拉取成功！", "success")
                self._set_status("✅ 场地拉取成功", "配置正确，可以开始预约")
                messagebox.showinfo("✅ 成功", "场地拉取成功！\n\n请切换到【操作】页面进行预约。")
            except Exception as e:
                self._action_btns["预拉取场地"].config(text="❌ 失败", bg=self.ui['error'])
                self.root.after(2000, lambda: self._action_btns["预拉取场地"].config(text="📍 预拉取场地", bg=self.ui['primary']))
                self.log(f"拉取场地失败：{str(e)}", "error")
                self._set_status("❌ 拉取失败", "请检查配置和网络连接")
                messagebox.showerror("❌ 错误", f"拉取场地失败：{str(e)}")
        self._run_in_background(fetch_task)

    def manual_book(self):
        self._action_btns["立即预约"].config(text="⏳ 预约中...", bg=self.ui['primary_hover'])
        self.root.update_idletasks()
        def book_task():
            self._set_status("⏳ 正在预约...", "正在尝试预约场地...")
            try:
                self._ensure_dependencies()
                required_keys = ['stockid', 'stockdetail_id']
                missing = [key for key in required_keys if not Config.BOOKING_DATA.get(key)]
                if missing:
                    raise RuntimeError("请先点击【预拉取场地】获取数据，然后再尝试预约")
                book_venue()
                self._action_btns["立即预约"].config(text="✅ 已预约", bg=self.ui['success'])
                self.root.after(2000, lambda: self._action_btns["立即预约"].config(text="⚡ 立即预约", bg=self.ui['primary']))
                self.log("预约成功！", "success")
                self._set_status("✅ 预约成功", "预约已完成，请查看日志")
                self.booking_count += 1
                self.last_booking_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.update_stats()
                messagebox.showinfo("✅ 成功", "预约成功！\n\n请查看【日志】页面了解详情。")
            except Exception as e:
                self._action_btns["立即预约"].config(text="❌ 失败", bg=self.ui['error'])
                self.root.after(2000, lambda: self._action_btns["立即预约"].config(text="⚡ 立即预约", bg=self.ui['primary']))
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
        
        self._start_auto_btn.config(text="⏳ 启动中...", bg=self.ui['primary_hover'])
        self.root.update_idletasks()

        def scheduler_task():
            self.scheduler_running = True
            self._start_auto_btn.config(text="▶️ 运行中", bg=self.ui['success'])
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
                self._start_auto_btn.config(text="▶️ 启动自动预约", bg=self.ui['primary'])

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
        btn = tk.Label(
            parent,
            text=text,
            font=self.ui['action_font'],
            bg=self.ui['primary'],
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2',
        )
        btn.bind('<Button-1>', lambda e, cmd=command: cmd())
        btn.bind('<Enter>', lambda e: btn.configure(bg=self.ui['primary_hover']))
        btn.bind('<Leave>', lambda e: btn.configure(bg=self.ui['primary']))
        return btn

    def _create_secondary_button(self, parent, text, command):
        btn = tk.Label(
            parent,
            text=text,
            font=self.ui['action_font'],
            bg=self.ui['surface'],
            fg=self.ui['primary'],
            padx=16,
            pady=8,
            cursor='hand2',
        )
        btn.bind('<Button-1>', lambda e, cmd=command: cmd())
        btn.bind('<Enter>', lambda e: btn.configure(bg=self.ui['primary_light']))
        btn.bind('<Leave>', lambda e: btn.configure(bg=self.ui['surface']))
        return btn

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
