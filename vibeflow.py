#!/usr/bin/env python3
"""
VIBE FLOW - The Ultimate Productivity & Mood App for Gen Z
Combines: Duolingo streaks + Notion productivity + Discord vibes + TikTok quick actions
Features:
- Gamified XP & Leveling system
- Streak tracking with fire emojis
- Mood/Vibe tracking with beautiful visuals
- Focus timer with ambient modes
- Habit builder with progress rings
- Daily challenges
- Animated gradients & smooth transitions
- Neon dark theme
"""

import flet as ft
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
import math

# Data storage
DATA_FILE = Path(__file__).parent / "vibeflow_data.json"

class VibeFlowApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "VIBE FLOW ⚡"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#0a0a0f"
        self.page.padding = 0
        self.page.spacing = 0
        
        # Load or initialize data
        self.data = self.load_data()
        
        # State
        self.current_view = "home"
        self.timer_running = False
        self.timer_seconds = 0
        self.selected_mood = None
        self.focus_duration = 25 * 60  # 25 minutes
        
        # Colors - Neon palette
        self.colors = {
            "bg": "#0a0a0f",
            "card": "#12121a",
            "card_hover": "#1a1a25",
            "primary": "#00f5ff",
            "secondary": "#ff00ff",
            "accent": "#ffff00",
            "success": "#00ff88",
            "warning": "#ffaa00",
            "error": "#ff4466",
            "text": "#ffffff",
            "text_dim": "#888899",
            "gradient_1": "#ff00ff",
            "gradient_2": "#00f5ff",
            "gradient_3": "#ffff00",
        }
        
        self.setup_page()
        
    def load_data(self):
        """Load user data from JSON file"""
        if DATA_FILE.exists():
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        else:
            # Initialize new user data
            today = datetime.now().strftime("%Y-%m-%d")
            return {
                "user": {
                    "name": "Viber",
                    "level": 1,
                    "xp": 0,
                    "xp_to_next": 100,
                    "streak": 0,
                    "last_active": None,
                    "total_focus_minutes": 0,
                    "completed_habits": 0,
                },
                "habits": [
                    {"id": 1, "name": "💧 Drink Water", "icon": "💧", "completed_today": False, "streak": 0},
                    {"id": 2, "name": "📱 Digital Detox", "icon": "📱", "completed_today": False, "streak": 0},
                    {"id": 3, "name": "🏃 Move Body", "icon": "🏃", "completed_today": False, "streak": 0},
                    {"id": 4, "name": "📚 Learn Something", "icon": "📚", "completed_today": False, "streak": 0},
                    {"id": 5, "name": "😴 Good Sleep", "icon": "😴", "completed_today": False, "streak": 0},
                ],
                "moods": [],
                "challenges": self.generate_daily_challenges(),
                "last_reset": today,
            }
    
    def save_data(self):
        """Save user data to JSON file"""
        # Check if we need to reset daily data
        today = datetime.now().strftime("%Y-%m-%d")
        if self.data.get("last_reset") != today:
            self.reset_daily_data()
        
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=2)
    
    def reset_daily_data(self):
        """Reset daily counters"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Check streak
        last_active = self.data["user"].get("last_active")
        if last_active:
            last_date = datetime.strptime(last_active, "%Y-%m-%d")
            yesterday = datetime.now() - timedelta(days=1)
            if last_date.date() < yesterday.date():
                # Streak broken
                self.data["user"]["streak"] = 0
        
        # Reset habits
        for habit in self.data["habits"]:
            habit["completed_today"] = False
        
        # Generate new challenges
        self.data["challenges"] = self.generate_daily_challenges()
        self.data["last_reset"] = today
        
        self.save_data()
    
    def generate_daily_challenges(self):
        """Generate random daily challenges"""
        challenges_pool = [
            {"name": "Complete 3 habits", "xp": 50, "icon": "🎯"},
            {"name": "Focus for 30 min", "xp": 75, "icon": "⏱️"},
            {"name": "Log your mood", "xp": 25, "icon": "😊"},
            {"name": "Take a break", "xp": 30, "icon": "☕"},
            {"name": "Hydrate 5x", "xp": 40, "icon": "💧"},
            {"name": "No social media 1hr", "xp": 60, "icon": "📵"},
        ]
        return random.sample(challenges_pool, 3)
    
    def add_xp(self, amount):
        """Add XP and handle leveling up"""
        self.data["user"]["xp"] += amount
        
        # Level up logic
        while self.data["user"]["xp"] >= self.data["user"]["xp_to_next"]:
            self.data["user"]["xp"] -= self.data["user"]["xp_to_next"]
            self.data["user"]["level"] += 1
            self.data["user"]["xp_to_next"] = int(self.data["user"]["xp_to_next"] * 1.5)
            
            # Show level up notification
            self.show_notification(f"🎉 LEVEL UP! You're now level {self.data['user']['level']}!", "success")
        
        self.save_data()
        self.update_stats_display()
    
    def setup_page(self):
        """Setup the main page layout"""
        # Animated gradient background
        self.gradient_container = ft.Container(
            content=ft.Column([], spacing=0),
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=[self.colors["gradient_1"], self.colors["gradient_2"], self.colors["gradient_3"]],
                stops=[0.0, 0.5, 1.0],
            ),
            opacity=0.03,
            expand=True,
        )
        
        # Main content
        self.main_content = ft.Column(
            controls=[self.build_home_view()],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )
        
        # Bottom navigation
        self.nav_rail = self.build_nav_rail()
        
        # Layout
        self.page.add(
            ft.Row(
                controls=[
                    ft.Container(
                        content=self.main_content,
                        expand=True,
                        padding=20,
                    ),
                    self.nav_rail,
                ],
                spacing=0,
                expand=True,
            )
        )
        
        # Start animation
        self.page.on_interval = self.animate_background
        self.page.interval = 100
        self.page.update()
    
    def animate_background(self, e):
        """Subtle background animation"""
        # Could add more complex animations here
        pass
    
    def build_nav_rail(self):
        """Build the navigation rail"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(height=40),
                    self.nav_button("🏠", "home", True),
                    self.nav_button("⚡", "focus", False),
                    self.nav_button("🎯", "habits", False),
                    self.nav_button("😊", "mood", False),
                    self.nav_button("🏆", "stats", False),
                    ft.Container(expand=True),
                    self.nav_button("⚙️", "settings", False),
                    ft.Container(height=20),
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=80,
            bgcolor=self.colors["card"],
            border_radius=ft.BorderRadius(20, 0, 20, 0),
            padding=10,
        )
    
    def nav_button(self, icon, view_name, active=False):
        """Create a navigation button"""
        def on_click(e):
            self.navigate_to(view_name)
        
        return ft.IconButton(
            icon=icon,
            icon_size=28,
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.HOVERED: self.colors["card_hover"]},
                overlay_color={ft.ControlState.HOVERED: self.colors["primary"]},
            ),
            icon_color=self.colors["primary"] if active else self.colors["text_dim"],
            tooltip=view_name.capitalize(),
        )
    
    def navigate_to(self, view_name):
        """Navigate to different views"""
        self.current_view = view_name
        
        # Update nav buttons
        nav_buttons = self.nav_rail.content.controls[1:-2]
        view_names = ["home", "focus", "habits", "mood", "stats"]
        
        for i, btn in enumerate(nav_buttons):
            btn.icon_color = self.colors["primary"] if view_names[i] == view_name else self.colors["text_dim"]
        
        # Load appropriate view
        views = {
            "home": self.build_home_view,
            "focus": self.build_focus_view,
            "habits": self.build_habits_view,
            "mood": self.build_mood_view,
            "stats": self.build_stats_view,
            "settings": self.build_settings_view,
        }
        
        if view_name in views:
            self.main_content.controls = [views[view_name]()]
        
        self.page.update()
    
    def build_home_view(self):
        """Build the home/dashboard view"""
        # Update streak if needed
        today = datetime.now().strftime("%Y-%m-%d")
        if self.data["user"].get("last_active") != today:
            self.data["user"]["last_active"] = today
            self.data["user"]["streak"] += 1
            self.save_data()
        
        user = self.data["user"]
        
        # Welcome section with animated stats
        welcome_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("✨ What's good,", size=32, weight=ft.FontWeight.BOLD, color=self.colors["text"]),
                    ft.Text(f"{user['name']}!", 
                           size=48, 
                           weight=ft.FontWeight.BOLD,
                           style=ft.TextStyle(foreground=ft.LinearGradient(colors=[self.colors["primary"], self.colors["secondary"]])),
                           ),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("🔥", size=32),
                                    ft.Text(f"{user['streak']}", size=24, weight=ft.FontWeight.BOLD, color=self.colors["warning"]),
                                    ft.Text("day streak", size=12, color=self.colors["text_dim"]),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                padding=15,
                                border_radius=15,
                                bgcolor=self.colors["card"],
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("⭐", size=32),
                                    ft.Text(f"Lvl {user['level']}", size=24, weight=ft.FontWeight.BOLD, color=self.colors["primary"]),
                                    ft.Text(f"{user['xp']}/{user['xp_to_next']} XP", size=12, color=self.colors["text_dim"]),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                padding=15,
                                border_radius=15,
                                bgcolor=self.colors["card"],
                            ),
                            ft.Container(
                                content=ft.ProgressBar(
                                    value=user["xp"] / user["xp_to_next"] if user["xp_to_next"] > 0 else 0,
                                    color=self.colors["primary"],
                                    bgcolor=self.colors["card"],
                                ),
                                width=200,
                                padding=ft.padding.only(top=25),
                            ),
                        ],
                        spacing=20,
                    ),
                ],
                spacing=15,
            ),
            padding=30,
            border_radius=25,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=["#1a1a2e", "#16213e"],
            ),
        )
        
        # Quick actions
        quick_actions = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("⚡ Quick Actions", size=20, weight=ft.FontWeight.BOLD, color=self.colors["text"]),
                    ft.Row(
                        controls=[
                            self.quick_action_button("🎯", "Start Focus", lambda e: self.navigate_to("focus")),
                            self.quick_action_button("😊", "Log Mood", lambda e: self.navigate_to("mood")),
                            self.quick_action_button("💧", "Drink Water", self.complete_habit_quick),
                            self.quick_action_button("🏃", "Move", self.complete_habit_move),
                        ],
                        spacing=15,
                    ),
                ],
                spacing=15,
            ),
            padding=25,
            border_radius=20,
            bgcolor=self.colors["card"],
        )
        
        # Today's challenges
        challenges_list = ft.Column(
            controls=[
                ft.Text("🎮 Daily Challenges", size=20, weight=ft.FontWeight.BOLD, color=self.colors["text"]),
            ],
            spacing=10,
        )
        
        for challenge in self.data["challenges"]:
            challenges_list.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(challenge["icon"], size=24),
                            ft.Text(challenge["name"], size=16, color=self.colors["text"]),
                            ft.Container(expand=True),
                            ft.Text(f"+{challenge['xp']} XP", size=14, color=self.colors["warning"], weight=ft.FontWeight.BOLD),
                        ],
                    ),
                    padding=15,
                    border_radius=12,
                    bgcolor=self.colors["card"],
                    on_hover=self.hover_effect,
                )
            )
        
        challenges_card = ft.Container(
            content=challenges_list,
            padding=25,
            border_radius=20,
            bgcolor=self.colors["card"],
        )
        
        return ft.Column(
            controls=[
                ft.Container(height=20),
                welcome_card,
                quick_actions,
                challenges_card,
                ft.Container(height=40),
            ],
            spacing=20,
        )
    
    def quick_action_button(self, icon, label, on_click):
        """Create a quick action button"""
        return ft.GestureDetector(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(icon, size=32),
                        ft.Text(label, size=12, color=self.colors["text_dim"], text_align=ft.TextAlign.CENTER),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                ),
                width=100,
                height=100,
                border_radius=20,
                bgcolor=self.colors["card"],
                alignment=ft.alignment.center,
            ),
            on_tap=on_click,
            hover_color=self.colors["card_hover"],
        )
    
    def hover_effect(self, e):
        """Hover effect for containers"""
        if e.data == "true":
            e.control.bgcolor = self.colors["card_hover"]
        else:
            e.control.bgcolor = self.colors["card"]
        e.control.update()
    
    def complete_habit_quick(self, e):
        """Quick complete water habit"""
        for habit in self.data["habits"]:
            if "Water" in habit["name"]:
                if not habit["completed_today"]:
                    habit["completed_today"] = True
                    habit["streak"] += 1
                    self.add_xp(10)
                    self.show_notification("💧 Hydrated! +10 XP", "success")
                else:
                    self.show_notification("Already completed! 💪", "info")
                break
        self.save_data()
        self.page.update()
    
    def complete_habit_move(self, e):
        """Quick complete move habit"""
        for habit in self.data["habits"]:
            if "Move" in habit["name"]:
                if not habit["completed_today"]:
                    habit["completed_today"] = True
                    habit["streak"] += 1
                    self.add_xp(15)
                    self.show_notification("🏃 Let's go! +15 XP", "success")
                else:
                    self.show_notification("Already crushed it! 🔥", "info")
                break
        self.save_data()
        self.page.update()
    
    def build_focus_view(self):
        """Build the focus timer view"""
        self.timer_display = ft.Text(
            "25:00",
            size=96,
            weight=ft.FontWeight.BOLD,
            font_family="monospace",
            color=self.colors["primary"],
        )
        
        self.timer_status = ft.Text("Ready to focus?", size=18, color=self.colors["text_dim"])
        
        self.start_pause_btn = ft.ElevatedButton(
            "▶️ START",
            style=ft.ButtonStyle(
                bgcolor=self.colors["primary"],
                color="#000000",
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=30),
            ),
            on_click=self.toggle_timer,
        )
        
        self.reset_btn = ft.ElevatedButton(
            "🔄 RESET",
            style=ft.ButtonStyle(
                bgcolor=self.colors["card"],
                color=self.colors["text"],
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=30),
            ),
            on_click=self.reset_timer,
        )
        
        # Duration selector
        duration_options = [
            ("🍅 Pomodoro (25min)", 25 * 60),
            ("⚡ Quick (10min)", 10 * 60),
            ("🧘 Deep Work (50min)", 50 * 60),
            ("🌟 Ultra (90min)", 90 * 60),
        ]
        
        duration_row = ft.Row(
            controls=[
                ft.Text("Choose duration:", size=16, color=self.colors["text_dim"]),
            ],
            spacing=10,
        )
        
        for label, seconds in duration_options:
            duration_row.controls.append(
                ft.ElevatedButton(
                    label,
                    style=ft.ButtonStyle(
                        bgcolor=self.colors["card"],
                        color=self.colors["text"],
                        padding=15,
                        shape=ft.RoundedRectangleBorder(radius=15),
                    ),
                    on_click=lambda e, s=seconds: self.set_duration(s),
                )
            )
        
        # Ambient sound options
        ambient_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("🎵 Ambient Sounds", size=18, color=self.colors["text_dim"]),
                    ft.Row(
                        controls=[
                            ft.IconButton("🌧️", tooltip="Rain"),
                            ft.IconButton("🔥", tooltip="Fireplace"),
                            ft.IconButton("🌊", tooltip="Ocean"),
                            ft.IconButton("🌲", tooltip="Forest"),
                            ft.IconButton("☕", tooltip="Cafe"),
                        ],
                    ),
                ],
                spacing=10,
            ),
            padding=20,
            border_radius=15,
            bgcolor=self.colors["card"],
        )
        
        # Circular progress indicator
        self.progress_ring = ft.ProgressRing(
            value=0,
            stroke_width=8,
            color=self.colors["primary"],
            bgcolor=self.colors["card"],
            width=300,
            height=300,
        )
        
        timer_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(height=30),
                    self.progress_ring,
                    ft.Stack(
                        controls=[
                            ft.Container(width=300, height=300),  # Spacer
                            ft.Positioned(
                                top=75,
                                left=75,
                                child=ft.Column(
                                    controls=[
                                        self.timer_display,
                                        self.timer_status,
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=10,
                                ),
                            ),
                        ],
                    ),
                    ft.Container(height=20),
                    ft.Row(
                        controls=[
                            self.start_pause_btn,
                            self.reset_btn,
                        ],
                        spacing=20,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Container(height=30),
                    duration_row,
                    ft.Container(height=20),
                    ambient_section,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            padding=40,
            border_radius=30,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=["#1a1a2e", "#16213e", "#0f3460"],
            ),
        )
        
        return ft.Column(
            controls=[
                ft.Container(height=20),
                ft.Text("🎯 Focus Zone", size=36, weight=ft.FontWeight.BOLD, color=self.colors["text"]),
                timer_container,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    
    def set_duration(self, seconds):
        """Set timer duration"""
        self.focus_duration = seconds
        self.timer_seconds = seconds
        self.update_timer_display()
        self.progress_ring.value = 0
        self.page.update()
    
    def toggle_timer(self, e):
        """Start/pause timer"""
        if self.timer_running:
            self.timer_running = False
            self.start_pause_btn.text = "▶️ RESUME"
            self.timer_status.value = "Paused"
            if self.page.interval:
                self.page.interval = None
        else:
            self.timer_running = True
            self.start_pause_btn.text = "⏸️ PAUSE"
            self.timer_status.value = "Let's get it! 🔥"
            self.page.interval = 1000  # Update every second
            self.page.on_interval = self.update_timer
        
        self.page.update()
    
    def update_timer(self, e):
        """Update timer every second"""
        if self.timer_running and self.timer_seconds > 0:
            self.timer_seconds -= 1
            self.update_timer_display()
            
            # Update progress ring
            progress = 1 - (self.timer_seconds / self.focus_duration)
            self.progress_ring.value = progress
            
            # Check if timer completed
            if self.timer_seconds <= 0:
                self.timer_complete()
        
        self.page.update()
    
    def update_timer_display(self):
        """Update timer display"""
        minutes = self.timer_seconds // 60
        seconds = self.timer_seconds % 60
        self.timer_display.value = f"{minutes:02d}:{seconds:02d}"
    
    def reset_timer(self, e):
        """Reset timer"""
        self.timer_running = False
        self.timer_seconds = self.focus_duration
        self.start_pause_btn.text = "▶️ START"
        self.timer_status.value = "Ready to focus?"
        self.progress_ring.value = 0
        self.page.interval = None
        self.update_timer_display()
        self.page.update()
    
    def timer_complete(self):
        """Handle timer completion"""
        self.timer_running = False
        self.start_pause_btn.text = "▶️ START"
        self.timer_status.value = "Session complete! 🎉"
        self.page.interval = None
        
        # Add XP and stats
        minutes_focused = self.focus_duration // 60
        xp_earned = minutes_focused * 2
        self.add_xp(xp_earned)
        self.data["user"]["total_focus_minutes"] += minutes_focused
        
        self.show_notification(f"🎯 Focus complete! +{xp_earned} XP", "success")
        self.save_data()
    
    def build_habits_view(self):
        """Build the habits tracker view"""
        habits_list = ft.Column(spacing=15)
        
        for habit in self.data["habits"]:
            completed = habit["completed_today"]
            
            habit_card = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Checkbox(
                                value=completed,
                                on_change=lambda e, h=habit: self.toggle_habit(h),
                                fill_color=self.colors["success"],
                                check_color="#000000",
                            ),
                        ),
                        ft.Text(habit["icon"], size=32),
                        ft.Column(
                            controls=[
                                ft.Text(habit["name"], size=18, weight=ft.FontWeight.BOLD, color=self.colors["text"]),
                                ft.Text(f"🔥 {habit['streak']} day streak", size=12, color=self.colors["warning"]),
                            ],
                            spacing=2,
                        ),
                        ft.Container(expand=True),
                        ft.Container(
                            content=ft.Icon(
                                ft.icons.STAR if completed else ft.icons.STAR_BORDER,
                                color=self.colors["accent"],
                                size=28,
                            ),
                            padding=10,
                        ),
                    ],
                ),
                padding=20,
                border_radius=20,
                bgcolor=self.colors["card"] if not completed else "#1a3a2a",
                border=ft.border.all(2, self.colors["success"] if completed else ft.colors.TRANSPARENT),
                on_hover=self.hover_effect,
            )
            
            habits_list.controls.append(habit_card)
        
        # Add habit button
        add_habit_btn = ft.ElevatedButton(
            "+ Add New Habit",
            style=ft.ButtonStyle(
                bgcolor=self.colors["card"],
                color=self.colors["primary"],
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=15),
            ),
            on_click=self.add_new_habit,
        )
        
        return ft.Column(
            controls=[
                ft.Container(height=20),
                ft.Text("🎯 Habits", size=36, weight=ft.FontWeight.BOLD, color=self.colors["text"]),
                ft.Text("Build your empire one habit at a time", size=16, color=self.colors["text_dim"]),
                ft.Container(height=20),
                habits_list,
                ft.Container(height=20),
                add_habit_btn,
            ],
            spacing=10,
        )
    
    def toggle_habit(self, habit):
        """Toggle habit completion"""
        habit["completed_today"] = not habit["completed_today"]
        
        if habit["completed_today"]:
            habit["streak"] += 1
            self.data["user"]["completed_habits"] += 1
            self.add_xp(15)
            self.show_notification(f"✅ {habit['name']} complete! +15 XP", "success")
        else:
            habit["streak"] = max(0, habit["streak"] - 1)
            self.show_notification("Habit unmarked", "info")
        
        self.save_data()
        self.page.update()
    
    def add_new_habit(self, e):
        """Add a new habit (placeholder)"""
        self.show_notification("Habit creation coming soon! 🚀", "info")
    
    def build_mood_view(self):
        """Build the mood tracker view"""
        mood_options = [
            ("🔥", "Lit", "Feeling amazing!"),
            ("😊", "Good", "Pretty solid day"),
            ("😐", "Meh", "Just okay"),
            ("😔", "Low", "Could be better"),
            ("😤", "Stressed", "Overwhelmed"),
        ]
        
        mood_grid = ft.Row(wrap=True, spacing=15)
        
        for emoji, name, desc in mood_options:
            mood_btn = ft.GestureDetector(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(emoji, size=48),
                            ft.Text(name, size=16, weight=ft.FontWeight.BOLD, color=self.colors["text"]),
                            ft.Text(desc, size=12, color=self.colors["text_dim"], text_align=ft.TextAlign.CENTER),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5,
                    ),
                    width=140,
                    height=160,
                    border_radius=20,
                    bgcolor=self.colors["card"],
                    alignment=ft.alignment.center,
                    border=ft.border.all(2, ft.colors.TRANSPARENT),
                ),
                on_tap=lambda e, m=name: self.select_mood(m),
                hover_color=self.colors["card_hover"],
            )
            mood_grid.controls.append(mood_btn)
        
        # Recent moods
        recent_moods = ft.Column(
            controls=[
                ft.Text("📊 Recent Vibes", size=20, weight=ft.FontWeight.BOLD, color=self.colors["text"]),
            ],
            spacing=10,
        )
        
        for mood_entry in reversed(self.data["moods"][-7:]):
            recent_moods.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(mood_entry["emoji"], size=24),
                            ft.Text(f"{mood_entry['mood']} - {mood_entry['date']}", color=self.colors["text_dim"]),
                        ],
                    ),
                    padding=10,
                    border_radius=10,
                    bgcolor=self.colors["card"],
                )
            )
        
        if not self.data["moods"]:
            recent_moods.controls.append(
                ft.Text("No moods logged yet. Track your first vibe!", color=self.colors["text_dim"])
            )
        
        return ft.Column(
            controls=[
                ft.Container(height=20),
                ft.Text("😊 How's your vibe?", size=36, weight=ft.FontWeight.BOLD, color=self.colors["text"]),
                ft.Text("Check in with yourself", size=16, color=self.colors["text_dim"]),
                ft.Container(height=30),
                mood_grid,
                ft.Container(height=40),
                ft.Container(
                    content=recent_moods,
                    padding=25,
                    border_radius=20,
                    bgcolor=self.colors["card"],
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    
    def select_mood(self, mood_name):
        """Log a mood"""
        emoji_map = {
            "Lit": "🔥",
            "Good": "😊",
            "Meh": "😐",
            "Low": "😔",
            "Stressed": "😤",
        }
        
        today = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        self.data["moods"].append({
            "mood": mood_name,
            "emoji": emoji_map.get(mood_name, "😊"),
            "date": today,
        })
        
        self.add_xp(25)
        self.show_notification(f"Mood logged: {mood_name} {emoji_map.get(mood_name, '😊')} +25 XP", "success")
        self.save_data()
        self.page.update()
    
    def build_stats_view(self):
        """Build the statistics view"""
        user = self.data["user"]
        
        # Stats cards
        stats_grid = ft.Row(
            wrap=True,
            spacing=20,
            controls=[
                self.stat_card("🔥", "Current Streak", f"{user['streak']} days", self.colors["warning"]),
                self.stat_card("⭐", "Level", str(user["level"]), self.colors["primary"]),
                self.stat_card("💎", "Total XP", f"{user['xp']:,}", self.colors["accent"]),
                self.stat_card("⏱️", "Focus Time", f"{user['total_focus_minutes']} min", self.colors["success"]),
                self.stat_card("✅", "Habits Done", f"{user['completed_habits']}", self.colors["secondary"]),
                self.stat_card("📝", "Moods Logged", f"{len(self.data['moods'])}", self.colors["text"]),
            ],
        )
        
        # Weekly chart placeholder
        weekly_chart = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("📈 This Week", size=20, weight=ft.FontWeight.BOLD, color=self.colors["text"]),
                    ft.Row(
                        controls=[
                            self.bar_chart_day("Mon", 75),
                            self.bar_chart_day("Tue", 90),
                            self.bar_chart_day("Wed", 45),
                            self.bar_chart_day("Thu", 100),
                            self.bar_chart_day("Fri", 60),
                            self.bar_chart_day("Sat", 85),
                            self.bar_chart_day("Sun", 70),
                        ],
                        spacing=15,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            padding=30,
            border_radius=20,
            bgcolor=self.colors["card"],
        )
        
        # Achievements
        achievements = ft.Column(
            controls=[
                ft.Text("🏆 Achievements", size=20, weight=ft.FontWeight.BOLD, color=self.colors["text"]),
                ft.Row(
                    controls=[
                        self.achievement_badge("🌟", "First Steps", "Complete your first habit", True),
                        self.achievement_badge("🔥", "On Fire", "7 day streak", user["streak"] >= 7),
                        self.achievement_badge("⏱️", "Focused", "100 min focus", user["total_focus_minutes"] >= 100),
                        self.achievement_badge("💪", "Dedicated", "30 day streak", user["streak"] >= 30),
                    ],
                    spacing=15,
                    wrap=True,
                ),
            ],
            spacing=15,
        )
        
        return ft.Column(
            controls=[
                ft.Container(height=20),
                ft.Text("📊 Your Stats", size=36, weight=ft.FontWeight.BOLD, color=self.colors["text"]),
                ft.Text("Track your progress", size=16, color=self.colors["text_dim"]),
                ft.Container(height=30),
                stats_grid,
                ft.Container(height=30),
                weekly_chart,
                ft.Container(height=30),
                ft.Container(
                    content=achievements,
                    padding=30,
                    border_radius=20,
                    bgcolor=self.colors["card"],
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    
    def stat_card(self, icon, label, value, color):
        """Create a stat card"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(icon, size=32),
                    ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=color),
                    ft.Text(label, size=12, color=self.colors["text_dim"], text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            width=140,
            height=140,
            border_radius=20,
            bgcolor=self.colors["card"],
            alignment=ft.alignment.center,
        )
    
    def bar_chart_day(self, day, height_percent):
        """Create a bar chart day"""
        return ft.Column(
            controls=[
                ft.Container(
                    height=height_percent,
                    width=30,
                    bgcolor=self.colors["primary"],
                    border_radius=ft.BorderRadius(10, 10, 0, 0),
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment.BOTTOM_CENTER,
                        end=ft.Alignment.TOP_CENTER,
                        colors=[self.colors["primary"], self.colors["secondary"]],
                    ),
                ),
                ft.Text(day, size=12, color=self.colors["text_dim"]),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        )
    
    def achievement_badge(self, icon, name, desc, unlocked):
        """Create an achievement badge"""
        opacity = 1.0 if unlocked else 0.3
        color = self.colors["accent"] if unlocked else self.colors["text_dim"]
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(icon, size=36, opacity=opacity),
                    ft.Text(name, size=14, weight=ft.FontWeight.BOLD, color=color, opacity=opacity),
                    ft.Text(desc, size=10, color=self.colors["text_dim"], opacity=opacity, text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            width=120,
            padding=15,
            border_radius=15,
            bgcolor=self.colors["card"] if unlocked else "#1a1a1a",
            border=ft.border.all(2, color if unlocked else ft.colors.TRANSPARENT),
        )
    
    def build_settings_view(self):
        """Build the settings view"""
        return ft.Column(
            controls=[
                ft.Container(height=20),
                ft.Text("⚙️ Settings", size=36, weight=ft.FontWeight.BOLD, color=self.colors["text"]),
                ft.Container(height=30),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.PERSON, color=self.colors["primary"]),
                                title=ft.Text("Username", color=self.colors["text"]),
                                subtitle=ft.Text(self.data["user"]["name"], color=self.colors["text_dim"]),
                            ),
                            ft.Divider(color=self.colors["card_hover"]),
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.NOTIFICATIONS, color=self.colors["primary"]),
                                title=ft.Text("Notifications", color=self.colors["text"]),
                                trailing=ft.Switch(value=True, active_color=self.colors["primary"]),
                            ),
                            ft.Divider(color=self.colors["card_hover"]),
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.PALETTE, color=self.colors["primary"]),
                                title=ft.Text("Theme", color=self.colors["text"]),
                                trailing=ft.Dropdown(
                                    options=[
                                        ft.dropdown.Option("Dark Neon"),
                                        ft.dropdown.Option("Light"),
                                        ft.dropdown.Option("Purple Haze"),
                                    ],
                                    value="Dark Neon",
                                    bgcolor=self.colors["card"],
                                    color=self.colors["text"],
                                ),
                            ),
                            ft.Divider(color=self.colors["card_hover"]),
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.DATA_USAGE, color=self.colors["primary"]),
                                title=ft.Text("Export Data", color=self.colors["text"]),
                                on_click=lambda e: self.export_data(),
                            ),
                            ft.Divider(color=self.colors["card_hover"]),
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.INFO, color=self.colors["primary"]),
                                title=ft.Text("About VIBE FLOW", color=self.colors["text"]),
                                subtitle=ft.Text("Version 1.0.0 • Made with ⚡"),
                            ),
                        ],
                        spacing=0,
                    ),
                    padding=20,
                    border_radius=20,
                    bgcolor=self.colors["card"],
                ),
            ],
            spacing=10,
        )
    
    def export_data(self):
        """Export user data"""
        self.show_notification("Data exported! (placeholder)", "info")
    
    def show_notification(self, message, type="info"):
        """Show a notification/snackbar"""
        colors = {
            "success": self.colors["success"],
            "error": self.colors["error"],
            "info": self.colors["primary"],
            "warning": self.colors["warning"],
        }
        
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color="#000000", weight=ft.FontWeight.BOLD),
            bgcolor=colors.get(type, self.colors["primary"]),
            behavior=ft.SnackBarBehavior.FLOATING,
            shape=ft.RoundedRectangleBorder(radius=15),
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def update_stats_display(self):
        """Update stats display when navigating back to home"""
        pass


def main(page: ft.Page):
    """Main entry point"""
    app = VibeFlowApp(page)
    page.update()


if __name__ == "__main__":
    ft.run(main, port=8550)
